"""
The generate post graph is responsible for generating a social media post based 
on a collection of source content. The source content may be URLs directly provided, 
or it may need to be located via web search relevant to the desired topic.
"""

from typing import cast

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict
import random

from agents.utils import load_chat_model
from agents.generate_post.state import GeneratePostState
from agents.generate_post.configuration import GeneratePostConfiguration
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from agents.generate_post.utils import *
from agents.verify_source.graph import graph as verify_links_graph

async def generate_report(
    state: GeneratePostState, *, config: RunnableConfig
) -> GeneratePostState:
    """Create report content."""
    
    config = GeneratePostConfiguration.from_runnable_config(config)
    # call model to generate the report
    model = load_chat_model(config.report_model)
    response = await model.ainvoke(
        [
            SystemMessage(build_report_system_prompt(state, config)),
            HumanMessage(build_report_content_prompt(state, config)),
        ]
    )
    return {
        "report": parse_report(response["content"]),
    }

async def generate_post(
    state: GeneratePostState, *, config: RunnableConfig
) -> GeneratePostState:
    """Create post content."""
    
    if not state.report:
        raise ValueError("No report found.")
    if len(state.relevant_links) == 0:
        raise ValueError("No relevant links found.")
    
    config = GeneratePostConfiguration.from_runnable_config(config)
    # call model to generate the post
    model = load_chat_model(config.post_model)
    response = await model.ainvoke(
        [
            SystemMessage(build_post_system_prompt(state, config)),
            HumanMessage(build_report_prompt(state, config)),
        ]
    )
    # calculate post during time for next Saturday
    next_saturday = get_next_saturday()
    random_hour = random.uniform(8, 17) # 8am to 5pm
    random_minute = random.uniform(0, 59)
    schedule_date = next_saturday.replace(hour=random_hour, minute=random_minute)
    return {
        "post": response["post"],
        "schedule_date": schedule_date,
    }

# Define the graph
builder = StateGraph(GeneratePostState, config_schema=GeneratePostConfiguration)
# TODO: add verify links subgraph
# builder.add_node("verify_links_graph", verify_links_graph)
builder.add_node(generate_post)
builder.add_node(generate_report)
builder.add_edge(START, "generate_report")
# builder.add_edge(START, "verify_links_graph")
# builder.add_edge("verify_links_graph", "generate_report")
builder.add_edge("generate_report", "generate_post")
builder.add_edge("generate_post", END)
# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "GeneratePost"
