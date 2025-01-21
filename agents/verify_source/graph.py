"""
Verify source graph examines the content at a specific url and determines if that material
is relevant to the topic defined as an input.
"""
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig
from agents.verify_source.configuration import VerifySourceConfiguration
from agents.verify_source.state import VerifySourceInputState, VerifyGeneralSourceReturnState
from agents.verify_source.utils import get_url_contents, RelevanceEvaluation, get_relevance_eval_system_prompt
from agents.utils import load_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

async def verify_general(
    state: VerifySourceInputState, *, config: RunnableConfig
) -> VerifyGeneralSourceReturnState:
    """Verify general web source content against the topic."""

    config = VerifySourceConfiguration.from_runnable_config(config)

    if not state.url:
        # TODO: log error
        raise ValueError("No URL provided as source content to verify.")
    
    url_contents = await get_url_contents(state, config)

    model = load_chat_model(config.relevancy_model).with_structured_output(RelevanceEvaluation)
    response = await model.ainvoke(
        [
            SystemMessage(get_relevance_eval_system_prompt(state, config)),
            HumanMessage(url_contents.content),
        ]
    )

    if response.relevant:
        # return the relevant links and page contents for use in crafting the post
        return VerifyGeneralSourceReturnState(
            relevant_links=[state.url],
            page_contents=[{"content": url_contents.content}], 
            # TODO: include image urls
        )
    else:
        # return empty arrays so this URL is not included when crafting the post
        return VerifyGeneralSourceReturnState(
            relevant_links=[],
            page_contents=[],
        )

# Define the graph
builder = StateGraph(VerifySourceInputState, config_schema=VerifySourceConfiguration)
builder.add_node(verify_general)
builder.add_edge(START, "verify_general")
builder.add_edge("verify_general", END)
# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "VerifySource"
