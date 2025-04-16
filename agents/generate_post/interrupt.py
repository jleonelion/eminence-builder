"""Utility functions specifically for handling interrupts."""

from dataclasses import dataclass
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage

from agents.generate_post.configuration import GeneratePostConfiguration
from agents.prompts import ROUTE_RESPONSE_PROMPT
from agents.utils import load_chat_model


class RouteResponseArgs(TypedDict):
    """A TypedDict for the arguments required to determine the route response."""

    post: str
    date_or_priority: str
    user_response: str


@dataclass(kw_only=True)
class RouteDecision:
    """A dataclass for making route decisions based on user response."""

    route: Literal["rewrite_post", "update_date", "unknown_response"]


def build_route_content_prompt(
    config: GeneratePostConfiguration,
    post: str,
    date_or_priority: str,
    user_response: str,
) -> str:
    """Build the content prompt for determining the route response.

    Args:
        config (GeneratePostConfiguration): The configuration for generating the post.
        post (str): The post content.
        date_or_priority (str): The date or priority information.
        user_response (str): The user's response.

    Returns:
        str: The formatted route response prompt.
    """
    return ROUTE_RESPONSE_PROMPT.format(
        post=post,
        date_or_priority=date_or_priority,
        user_response=user_response,
    )


async def determine_next_node(
    post: str,
    date_or_priority: str,
    user_response: str,
    config: GeneratePostConfiguration,
) -> RouteResponseArgs:
    """Determine the next node based on the user's response.

    Args:
        post (str): The post content.
        date_or_priority (str): The date or priority information.
        user_response (str): The user's response.
        config (GeneratePostConfiguration): The configuration for generating the post.

    Returns:
        RouteResponseArgs: The arguments required to determine the route response.
    """
    model = load_chat_model(config.route_model)
    model = model.with_structured_output(RouteDecision)
    prompt = build_route_content_prompt(config, post, date_or_priority, user_response)
    # not sure if this should be a system message instead
    result = await model.ainvoke([HumanMessage(content=prompt)])
    return result
