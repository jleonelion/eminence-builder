"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated

from agents.configuration import BaseConfiguration

@dataclass(kw_only=True)
class GeneratePostConfiguration(BaseConfiguration):
    """The configuration for the agent."""
    text_only_mode: bool = field(
        default=True,
        metadata={
            "description": "Whether or not posts should be plain text."
        },
    )
    parse_request_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating posts Should be in the form: provider/model-name."
        },
    )
    post_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating posts Should be in the form: provider/model-name."
        },
    )
    report_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating information reports that act as input to posts. Should be in the form: provider/model-name."
        },
    )
    route_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "Model used to route user responses Should be in the form: provider/model-name."
        },
    )
    max_post_length: int = field(
        default=1000,
        metadata={
            "description": "The maximum length of the post."
        },
    )
    max_condense_count: int = field(
        default=3,
        metadata={
            "description": "The maximum iterations spent condensing post size."
        },
    )
    timezone: str = field(
        default="America/Los_Angeles",
        metadata={
            "description": "The timezone to use for scheduling posts."
        },
    )
