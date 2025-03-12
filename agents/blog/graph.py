"""Main graph for the agent."""

from langchain_community.document_loaders import PlaywrightURLLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from agents.blog.configuration import BlogConfiguration
from agents.blog.prompts import build_research_details_prompt
from agents.blog.schema import BlogRequest, Sections
from agents.blog.state import BlogState
from agents.pplx_researcher.graph import PplxResearchAgent
from agents.utils import format_docs, load_chat_model


async def extract_details(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Extract information from the user message to begin building a research plan."""
    agent_config = BlogConfiguration.from_runnable_config(config)
    llm = load_chat_model(
        fully_specified_name=agent_config.extract_details_model
        if agent_config.extract_details_model
        else agent_config.default_model,
        model_kwargs=agent_config.extract_details_model_kwargs
        if agent_config.extract_details_model_kwargs
        else agent_config.default_model_kwargs,
    )
    system_prompt_template = build_research_details_prompt()
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_prompt_template] + state.messages
    )
    chain = chat_prompt | llm.with_structured_output(BlogRequest)
    response = chain.invoke({})

    return {
        "blog_request": response,
    }


async def define_structure(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Define structure for the blog post."""
    agent_config = BlogConfiguration.from_runnable_config(config)
    llm = load_chat_model(
        fully_specified_name=agent_config.define_structure_model
        if agent_config.define_structure_model
        else agent_config.default_model,
        model_kwargs=agent_config.define_structure_model_kwargs
        if agent_config.define_structure_model_kwargs
        else agent_config.default_model_kwargs,
    )
    # Generate sections
    structured_llm = llm.with_structured_output(Sections)
    content = format_docs(state.reference_content)
    # TODO: not sure if the Human Message is helpful here or just a waste of tokens
    report_sections = structured_llm.invoke(
        [SystemMessage(content=content)]
        + [
            HumanMessage(
                content="Generate the sections of the blog post. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields."
            )
        ]
    )
    # TODO: trigger interrupt for hitl to review and approve sections
    return {"sections": report_sections.sections}


async def pplx_researcher(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Conduct research on the main topic of the blog post."""
    agent_config = BlogConfiguration.from_runnable_config(config)
    # skip if not enabled
    if not agent_config.run_pplx_research:
        return state

    pplx_config = agent_config.pplx_config
    agent = PplxResearchAgent(pplx_config)
    document = agent.research_topic(state.blog_request.message)

    return {
        "reference_content": [document],
    }


async def load_priority_links(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Load data from links provided by user."""
    documents = []
    if state.blog_request.priority_links:
        loader = PlaywrightURLLoader(
            urls=state.blog_request.priority_links,
            remove_selectors=["header", "footer"],
        )
        documents = await loader.aload()

    return {
        "reference_content": documents,
    }


async def autonomous_writer(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Asynchronously writes blog content autonomously based on the given state and configuration.

    Args:
        state (BlogState): The current state of the blog.
        config (RunnableConfig): Configuration parameters for the autonomous writer.

    Returns:
        BlogState: The updated state of the blog after writing content.
    """
    return state


async def generate_images(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Asynchronously generates images for blog content defined in that state.

    Args:
        state (BlogState): The current state of the blog.
        config (RunnableConfig): Configuration parameters for the autonomous writer.

    Returns:
        BlogState: The updated state of the blog after writing content.
    """
    return state


async def summarize_reference_links(
    state: BlogState, *, config: RunnableConfig
) -> BlogState:
    """Spawns reference link summary for each reference link included in the Human messages.

    Args:
        state (BlogState): The current state of the blog.
        config (RunnableConfig): Configuration parameters for the autonomous writer.

    Returns:
        BlogState: The updated state with updated reference summaries.
    """
    return state


# Define the graph
builder = StateGraph(state_schema=BlogState, config_schema=BlogConfiguration)
builder.add_node(extract_details)
builder.add_node(pplx_researcher)
builder.add_node(load_priority_links)
builder.add_node(define_structure)

builder.add_edge(START, "extract_details")
builder.add_edge("extract_details", "pplx_researcher")
builder.add_edge("extract_details", "load_priority_links")
builder.add_edge("load_priority_links", "define_structure")
builder.add_edge("pplx_researcher", "define_structure")
builder.add_edge("define_structure", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "Blog Graph"
