"""Researcher graph used in the conversational retrieval system as a subgraph.

This module defines the core structure and functionality of the researcher graph,
which is responsible for generating search queries and retrieving relevant documents.
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
from agents.generate_post.utils import *
from agents.contstants import ALLOWED_TIMES


async def generate_report(
    state: GeneratePostState, *, config: GeneratePostConfiguration
) -> GeneratePostState:
    """Create report content."""
    
    # call model to generate the report
    model = load_chat_model(config.report_model)
    messages = [
        {"role": "system", "content": build_report_system_prompt(state, config)},
        {"role": "human", "content": build_report_content_prompt(state, config)},
    ]
    response = await model.ainvoke(messages)
    return {
        "report": parse_report(response["content"]),
    }

async def generate_post(
    state: GeneratePostState, *, config: GeneratePostConfiguration
) -> GeneratePostState:
    """Create post content."""
    
    if not state.report:
        raise ValueError("No report found.")
    if len(state.relevant_links) == 0:
        raise ValueError("No relevant links found.")
    # call model to generate the post
    model = load_chat_model(config.post_model)
    messages = [
        {"role": "system", "content": build_post_system_prompt(state, config)},
        {"role": "human", "content": build_report_prompt(state, config)},
    ]
    response = await model.ainvoke(messages)
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
builder = StateGraph(GeneratePostState, GeneratePostConfiguration)
builder.add_node(generate_post)
builder.add_node(generate_report)
builder.add_edge(START, "generate_report")
builder.add_edge("generate_report", "generate_post")
builder.add_edge("generate_post", END)
# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "GeneratePost"
