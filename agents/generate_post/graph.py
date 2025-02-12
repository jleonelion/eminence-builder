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
from agents.generate_post.state import GeneratePostState, Image
from agents.generate_post.configuration import GeneratePostConfiguration
from agents.generate_post.interrupt import *
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt, Command
from agents.generate_post.utils import *
from agents.verify_links.graph import graph as verify_links
from agents.find_images.graph import graph as find_images
import pytz
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

@dataclass(kw_only=True)
class PostInformation:
    topic: str
    style: str = field(default="default", metadata={"choices": ["default", "news", "education"]})
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
        "style": response["style"],
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
    state: GeneratePostState, *, config: RunnableConfig, store: BaseStore
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
            SystemMessage(build_post_system_prompt(state, config, store)),
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
    state: GeneratePostState, *, config: RunnableConfig, store: BaseStore
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
            SystemMessage(build_condense_post_system_prompt(state=state, config=config, original_post_length=original_post_length, store=store)),
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
            "image": state.image.image_url | "" if state.image and not config.text_only_mode else None,
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

    if not config.text_only_mode:
        procceesed_image = await process_image_input(response["args"].get("image", None))
        if procceesed_image != "remove":
            image_state = procceesed_image
        elif procceesed_image == "remove":
            image_state = None
        else:
            image_state = state.image

    # TODO would prefer next state calculations be done in router function
    match response["type"]:
        case "ignore":
            return {
                "next": END,
            }
        case "response":
            user_response = response.get("args", "")
            route_determination = await determine_next_node(
                post=state.post,
                date_or_priority=default_date_string,
                user_response=user_response,
                config=config,
            )
            if route_determination["route"] == "rewrite_post":
                return {
                    "user_response": user_response,
                    "next": "rewrite_post",
                }
            elif route_determination["route"] == "update_date":
                return {
                    "user_response": user_response,
                    "next": "update_schedule_date",
                }
            else:
                return {
                    "user_response": user_response,
                    "next": "unknown_response",
                }
        case "edit":
            if "args" not in response["args"]:
                raise ValueError(f"Expected response to have attribute args with key called args: {response['args']}. Must be defined")
            
            cast_args: Dict[str, str] = response["args"]["args"]
            response_post = cast_args.get("post", None)
            post_date = parse_date(cast_args.get("date", default_date_string))
            
            if not post_date:
                raise ValueError(f"Invalid date format: {cast_args.get('date', default_date_string)}")
            
            return {
                "next": "schedule_post",
                "schedule_date": post_date,
                "post": response_post if response_post else state.post,
                "user_response": None,
                "image": Image(imageUrl=image_state.get("image_url", None), mimeType=image_state.get("mime_type", None))
            }      
        case "accept":
            if "args" in response["args"]:                           
                cast_args: Dict[str, str] = response["args"]["args"]
                response_post = cast_args.get("post", None)
                post_date = parse_date(cast_args.get("date", default_date_string))
            
            return {
                "next": "schedule_post",
                "schedule_date": post_date if post_date else state.schedule_date,
                "post": response_post if response_post else state.post,
                "user_response": None,
                "image": Image(imageUrl=image_state.get("image_url", None), mimeType=image_state.get("mime_type", None))
            }
        case _:
            raise ValueError(f"Unexpected response type: {response['type']}")

async def rewrite_post(state: GeneratePostState, *, config: RunnableConfig, store: BaseStore) -> GeneratePostState:
    """Rewrite the post content."""
    if not state.post:
        raise ValueError("No post found.")
    if not state.user_response:
        raise ValueError("No user response found.")
    
    config = GeneratePostConfiguration.from_runnable_config(config)
    model = load_chat_model(config.rewrite_model, config.rewrite_model_kwargs)
    rewrite_post_prompt = await build_rewrite_post_prompt(state, config, store)
    response = await model.ainvoke(
        [
            SystemMessage(rewrite_post_prompt),
            HumanMessage(state.user_response),
        ]
    )
    # TODO call llm to identify and store a new reflection rule basd on original post, rewritten post, and user response
    return {
        "post": parse_post(response.content),
        "next": None,
        "user_response": None,
    }

async def schedule_post(state: GeneratePostState, *, config: RunnableConfig, store: BaseStore) -> GeneratePostState:
    """Schedule the post."""

    config = GeneratePostConfiguration.from_runnable_config(config)
    scheduled_post = {
        "topic": state.topic,
        "post": state.post, 
        "scheduled_date": calc_scheduled_date(state.schedule_date), 
        "status": "pending",
        "image": state.image
    }

    client = MongoClient(config.mongo_url)
    db = client[config.mongo_db]
    collection = db[config.mongo_collection_linkedin_posts]
    result = collection.insert_one(scheduled_post)

    return {
        "object_id": result.inserted_id,
    }

async def update_schedule_date(state: GeneratePostState, *, config: RunnableConfig, store: BaseStore) -> GeneratePostState:
    # TODO: Implement post scheduling
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
        return "find_images"

def route_human_response(
    state: GeneratePostState, config: RunnableConfig
) -> Literal["schedule_post", "rewrite_post", "update_schedule_date", "human", "__end__"]: # have to use string literal for END
    """Route after human."""
    
    if state.next:
        if state.next == "unknown_response":
            return "human"
        return state.next
    return END

# Define the graph
builder = StateGraph(GeneratePostState, config_schema=GeneratePostConfiguration)
builder.add_node(parse_post_request)
builder.add_node("verify_links", verify_links)
builder.add_node(generate_post)
builder.add_node(generate_report)
builder.add_node(condense_post)
builder.add_node(human)
builder.add_node("find_images", find_images)
builder.add_node(rewrite_post)
builder.add_node(schedule_post)
builder.add_node(update_schedule_date)
builder.add_edge(START, "parse_post_request")
builder.add_edge("parse_post_request", "verify_links")
builder.add_edge("verify_links", "generate_report")
builder.add_edge("generate_report", "generate_post")
builder.add_edge("generate_post", "condense_post")
builder.add_conditional_edges("condense_post", route_condense_human_images)
builder.add_edge("find_images", "human")
builder.add_edge("rewrite_post", "human")
builder.add_conditional_edges("human", route_human_response)
builder.add_edge("update_schedule_date", "human")
builder.add_edge("schedule_post", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "GeneratePost"
