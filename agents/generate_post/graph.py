"""
The generate post graph is responsible for generating a social media post based 
on a collection of source content. The source content may be URLs directly provided, 
or it may need to be located via web search relevant to the desired topic.
"""

from typing import Dict, cast

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict
import random

from agents.utils import load_chat_model
from agents.generate_post.state import GeneratePostState
from agents.generate_post.configuration import GeneratePostConfiguration
from agents.generate_post.interrupt import *
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt, Command
from agents.generate_post.utils import *
from agents.verify_links.graph import graph as verify_links
import pytz
from datetime import datetime

@dataclass(kw_only=True)
class PostInformation:
    topic: str
    links: list[str]

async def parse_post_request(
    state: GeneratePostState, *, config: RunnableConfig
) -> GeneratePostState:
    """Parse most recent Human message to determine the post topic and associated links."""
    
    config = GeneratePostConfiguration.from_runnable_config(config)
    # call model to generate the report
    model = load_chat_model(config.parse_request_model)
    model = model.with_structured_output(PostInformation)
    # extract last elements of type HumanMessage from state.messages list
    human_messages = [msg for msg in state.messages if isinstance(msg, HumanMessage)]
    if not human_messages:
        raise ValueError("No human messages found.")
    
    response = await model.ainvoke(
        [
            SystemMessage(get_parse_post_request_prompt(state, config)),
            human_messages[-1],
        ]
    )
    if not response["topic"]:
        raise ValueError("Could not determine topic.")
    return {
        "topic": response["topic"],
        "links": response["links"],
    }

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
    default_date_string = build_default_date(state, config)

    request = HumanInterrupt = {
        "action_request": {
            "action": "Schedule LinkedIn posts",
            "args": {
                "post": state.post,
                "default_date": default_date_string,
            },
            "config": {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": True,
                "allow_accept": True
            },
            "description": build_interrupt_desc(state, config)
        }
    }
    response = interrupt([request])
    response = response[0] if isinstance(response, list) else response
    response = cast(HumanResponse, response)

    if response["type"] == "ignore":
        return {
            "next": END,
        }

    if not response["args"]:
        # TODO log error
        raise ValueError(f"Unexpected response args: {response["args"]}.  Must be defined")
    
    if response["type"] == "response":
        route_determination = await route_determination(
            post=state.post,
            date_or_priority=default_date_string,
            user_response=response["args"],
        )
        if route_determination["route"] == "rewrite_post":
            return {
                "user_response": response["args"],
                "next": "rewrite_post",
            }
        elif route_determination["route"] == "update_date":
            return {
                "user_response": response["args"],
                "next": "update_schedule_date",
            }
        else:
            return {
                "user_response": response["args"],
                "next": "unknown_response",
            }
    
    # make sure response.args is a dict with key 'args'
    if "args" not in response["args"]:
        # TODO log error
        raise ValueError(f"Unexpected response args value: {response["args"]}.  Must be defined")
    # Cast to the expected type
    cast_args: Dict[str, str] = response["args"]["args"]

    # if 'post' key in cast_args is not defined, then raise an error
    if "post" not in cast_args:
        # TODO log error
        raise ValueError(f"post key not defined in response args: {cast_args}")
    else:
        response_post = cast_args["post"]
    
    post_date = parse_date(cast_args.get("date", default_date_string))
    
    if not post_date:
        # TODO log error
        raise ValueError(f"Invalid date format: {cast_args.get('date', default_date_string)}")

    # TODO: implement image management
    # let imageState: { imageUrl: string; mimeType: string } | undefined =
    #     undefined;
    #   if (!isTextOnlyMode) {
    #     const processedImage = await processImageInput(castArgs.image);
    #     if (processedImage && processedImage !== "remove") {
    #       imageState = processedImage;
    #     } else if (processedImage === "remove") {
    #       imageState = undefined;
    #     } else {
    #       imageState = state.image;
    #     }
    #   }

    return {
        "next": "schedule_post",
        "schedule_date": post_date,
        "post": response_post,
        "user_response": None,
        # "image": imageState,
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
builder.add_node(parse_post_request)
builder.add_node("verify_links", verify_links)
builder.add_node(generate_post)
builder.add_node(generate_report)
builder.add_node(condense_post)
builder.add_node(human)
builder.add_node(find_images)
builder.add_edge(START, "parse_post_request")
builder.add_edge("parse_post_request", "verify_links")
builder.add_edge("verify_links", "generate_report")
builder.add_edge("generate_report", "generate_post")
builder.add_edge("generate_post", "condense_post")
builder.add_conditional_edges("condense_post", route_condense_human_images)
builder.add_edge("human", END)
builder.add_edge("find_images", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "GeneratePost"
