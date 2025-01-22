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
from agents.verify_links.graph import graph as verify_links

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
        "report": parse_report(response.content),
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
    random_hour = random.randint(8, 17) # 8am to 5pm
    random_minute = random.randint(0, 59)
    schedule_date = next_saturday.replace(hour=random_hour, minute=random_minute)
    return {
        "post": parse_post(response.content),
        "schedule_date": schedule_date,
    }

async def condense_post(
    state: GeneratePostState, *, config: RunnableConfig
) -> GeneratePostState:
    """Condense post content."""
    
    if not state.post:
        raise ValueError("No post found.")
    if not state.report:
        raise ValueError("No report found.")
    if len(state.relevant_links) == 0:
        raise ValueError("No relevant links found.")
    
    config = GeneratePostConfiguration.from_runnable_config(config)
    original_post_length = len(remove_urls(state.post))
    
    # call model to generate the post
    model = load_chat_model(config.post_model)
    response = await model.ainvoke(
        [
            SystemMessage(build_condense_post_system_prompt(state, config, original_post_length)),
            HumanMessage(f"Here is the the post I'd like to condense: {state.post}"),
        ]
    )
    return {
        "post": parse_post(response.content),
        "condense_count": state.condense_count + 1,
    }

async def human(
    state: GeneratePostState, *, config: RunnableConfig
) -> GeneratePostState:
    """Invoke human-in-the-loop for post content."""
    
    if not state.post:
        raise ValueError("No post found.")
    
    config = GeneratePostConfiguration.from_runnable_config(config)
    default_date = state.schedule_date or get_next_saturday()
    # TODO: Implement human-in-the-loop logic
    return {
        "schedule_date": default_date,
        "post": state.post,
    }

async def find_images(
    state: GeneratePostState, *, config: RunnableConfig
) -> GeneratePostState:
    """Locate images for post."""
    
    # TODO: Implement image management
    return {
        "post": state.post,
    }

def route_condense_human_images(
        state: GeneratePostState, config: RunnableConfig
    ) -> Literal["condense_post", "human", "find_images"]:
    """Route to condense or human."""
    config = GeneratePostConfiguration.from_runnable_config(config)

    if state.condense_count >= config.max_condense_count:
        return "human"
    elif len(remove_urls(state.post)) > config.max_post_length:
        return "condense_post"
    elif config.text_only_mode:
        return "human"
    else:
        # TODO implement image management and...
        # return "find_images"
        return "human"

# Define the graph
builder = StateGraph(GeneratePostState, config_schema=GeneratePostConfiguration)
builder.add_node("verify_links", verify_links)
builder.add_node(generate_post)
builder.add_node(generate_report)
builder.add_node(condense_post)
builder.add_node(human)
builder.add_node(find_images)
builder.add_edge(START, "verify_links")
builder.add_edge("verify_links", "generate_report")
builder.add_edge("generate_report", "generate_post")
builder.add_edge("generate_post", "condense_post")
builder.add_conditional_edges("condense_post", route_condense_human_images)
builder.add_edge("human", END)
builder.add_edge("find_images", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "GeneratePost"
