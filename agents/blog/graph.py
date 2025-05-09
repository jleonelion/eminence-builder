"""Main graph for the agent."""

from datetime import datetime
from typing import Dict, Literal

from langchain_community.document_loaders import PlaywrightURLLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph

from agents.blog.configuration import BlogConfiguration
from agents.blog.prompts import (
    build_blog_planner_prompt,
    build_compile_blog_prompt,
    build_final_section_writer_prompt,
    build_research_details_prompt,
)
from agents.blog.schema import BlogRequest, Sections
from agents.blog.state import BlogState
from agents.blog.utils import format_sections
from agents.pplx_researcher.graph import PplxResearchAgent
from agents.schema import HumanResponse
from agents.utils import load_blog_posts_collection, load_chat_model
from agents.write_blog_section.configuration import BlogWriteSectionConfiguration
from agents.write_blog_section.graph import graph as section_writer_graph
from agents.write_blog_section.state import (
    BlogWriteSectionOutput,
    BlogWriteSectionState,
)

# from __future__ import annotations


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
    prompt = build_blog_planner_prompt(state=state, config=agent_config)
    report_sections = structured_llm.invoke([SystemMessage(content=prompt)])
    # TODO: trigger interrupt for hitl to review and approve sections
    return {"sections": report_sections.sections}


async def approve_structure(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Define structure for the blog post."""
    # TODO: implement HITL review
    # action_request = ActionRequest(
    #     action=f"Review Blog sections: {state.blog_request.main_topic}",
    #     args={
    #         "sections": state.sections,
    #         "reference_content": state.reference_content,
    #         "blog_request": state.blog_request,
    #     },
    # )
    # interrupt_config = HumanInterruptConfig(
    #     allow_ignore=True,  # Allow the user to `ignore` the interrupt.
    #     allow_respond=False,  # Allow the user to `respond` to the interrupt.
    #     allow_edit=True,  # Allow the user to `edit` the interrupt's args.
    #     allow_accept=True,  # Allow the user to `accept` the interrupt's args.
    # )
    # description = build_sections_approval(state, config)
    # request = HumanInterrupt(
    #     action_request=action_request, config=interrupt_config, description=description
    # )
    # response = interrupt([request])
    # response = response[0] if isinstance(response, list) else response
    # response = cast(HumanResponse, response)
    response = HumanResponse(
        type="accept",
    )
    match response["type"]:
        case "ignore":
            return {
                "sections": [],
            }
        case "edit":
            if "args" not in response["args"]:
                raise ValueError(
                    f"Expected response to have attribute args with key called args: {response['args']}. Must be defined"
                )

            cast_args: Dict[str, str] = response["args"]["args"]
            response_sections = cast_args.get("sections", state.sections)
            # convert response_sections to a list of Section objects
            response_sections = [
                Sections(**section) if isinstance(section, dict) else section
                for section in response_sections
            ]

            # TODO implement reflection on changes made to sections
            # if state.sections != response_sections:
            #     spawn_reflection_graph(
            #         state=ReflectionState(
            #             original_text=state.post, revised_text=response_post
            #         ),
            #         config=config,
            #     )

            return {
                "sections": response_sections,
            }
        case "accept":
            return {
                "sections": state.sections,
            }
        case _:
            raise ValueError(f"Unexpected response type: {response['type']}")


def calculate_section_word_limit(state: BlogState) -> int:
    """Calculate the word limit for each section based on the total word count of the blog."""
    # TODO implement logic to calculate word limit based on the total word count of the blog
    return 500


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


def proceed_with_writing(state: BlogState) -> Literal["proceed", "cancel"]:
    """Route based on human approval of sections."""
    if state.sections:
        return "proceed"
    else:
        return "cancel"


def spawn_section_writing(state: BlogState):
    """Route based on human approval of sections."""
    word_limit = calculate_section_word_limit(state)
    return [
        Send(
            "write_section",
            BlogWriteSectionState(
                section=s,
                word_limit=word_limit,
                reference_content=state.reference_content,
            ),
        )
        for s in state.sections
        if s.research
    ]


def gather_completed_sections(state: BlogState) -> BlogState:
    """Gather completed sections from research and render formatted string of completed sections."""
    # List of completed sections
    completed_sections = state.completed_sections

    # Format completed section to str to use as context for final sections
    state.completed_blog_sections = format_sections(completed_sections)

    return state


def spawn_final_section_writing(state: BlogState) -> list[Send]:
    """Kick off research on any sections that require it using the Send API."""
    return [
        Send(
            "write_final_sections",
            BlogWriteSectionState(
                section=s, completed_blog_sections=state.completed_blog_sections
            ),
        )
        for s in state.sections
        if not s.research
    ]


def write_final_sections(
    state: BlogWriteSectionState, *, config: RunnableConfig
) -> BlogWriteSectionOutput:
    """Write final sections of the report, which do not require web search and use the completed sections as context."""
    agent_config = BlogWriteSectionConfiguration.from_runnable_config(config)

    # Format system instructions
    system_instructions = build_final_section_writer_prompt(state, agent_config)
    # Generate section
    llm = load_chat_model(
        fully_specified_name=agent_config.default_model,
        model_kwargs=agent_config.default_model_kwargs,
    )
    section_content = llm.invoke(
        [SystemMessage(content=system_instructions)]
        + [
            HumanMessage(
                content="Generate a report section based on the provided sources."
            )
        ]
    )

    # Write content to section
    state.section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [state.section]}


def compile_final_blog(state: BlogState, *, config: RunnableConfig) -> BlogState:
    """Compile the final blog."""
    # Get sections
    sections = state.sections
    completed_sections = {s.name: s.content for s in state.completed_sections}

    # Update sections with completed content while maintaining original order
    for section in sections:
        section.content = completed_sections[section.name]
    # update state with sections that have been written
    state.sections = sections

    agent_config = BlogConfiguration.from_runnable_config(config)
    llm = load_chat_model(
        fully_specified_name=agent_config.compile_final_blog_model
        if agent_config.compile_final_blog_model
        else agent_config.default_model,
        model_kwargs=agent_config.compile_final_blog_model_kwargs
        if agent_config.compile_final_blog_model_kwargs
        else agent_config.default_model_kwargs,
    )
    # Format system instructions
    prompt = build_compile_blog_prompt(state, agent_config)
    # Rewrite content of the sections
    response = llm.invoke([SystemMessage(content=prompt)])
    # TODO: trigger interrupt for hitl to review and approve sections
    return {"final_blog": response.content}


def save_blog(state: BlogState, config: BlogConfiguration) -> BlogState:
    """Save blog for later use."""
    blog_config = BlogConfiguration.from_runnable_config(config)
    try:
        scheduled_blog = {
            "status": "pending",
            "created_date": datetime.now(),
            **state.model_dump(),
        }
        collection = load_blog_posts_collection(blog_config)
        result = collection.insert_one(scheduled_blog)
    except Exception as e:
        raise ValueError(f"Error storing new post: {e}")
    return {
        "object_id": result.inserted_id if result else None,
    }


# Define the graph
builder = StateGraph(state_schema=BlogState, config_schema=BlogConfiguration)
builder.add_node(extract_details)
builder.add_node(pplx_researcher)
builder.add_node(load_priority_links)
builder.add_node(define_structure)
builder.add_node(approve_structure)
builder.add_node("write_section", section_writer_graph)
builder.add_node(gather_completed_sections)
builder.add_node(write_final_sections)
builder.add_node("gather_final_sections", gather_completed_sections)
builder.add_node(compile_final_blog)
builder.add_node(save_blog)

builder.add_edge(START, "extract_details")
builder.add_edge("extract_details", "pplx_researcher")
builder.add_edge("extract_details", "load_priority_links")
builder.add_edge("load_priority_links", "define_structure")
builder.add_edge("pplx_researcher", "define_structure")
builder.add_edge("define_structure", "approve_structure")
# Use conditional edge to send documents to summarization
builder.add_conditional_edges(
    "approve_structure",
    spawn_section_writing,
    ["write_section"],
)
builder.add_edge("write_section", "gather_completed_sections")
builder.add_conditional_edges(
    "gather_completed_sections",
    spawn_final_section_writing,
    ["write_final_sections"],
)
builder.add_edge("write_final_sections", "gather_final_sections")
builder.add_edge("gather_final_sections", "compile_final_blog")
builder.add_edge("compile_final_blog", "save_blog")
builder.add_edge("save_blog", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "Blog Graph"
