"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated

from agents.configuration import BaseConfiguration

@dataclass(kw_only=True)
class VerifySourceConfiguration(BaseConfiguration):
    """The configuration for the agent."""
    text_only_mode: bool = field(
        default=True,
        metadata={
            "description": "Whether or not posts should be plain text."
        },
    )
    relevancy_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used to evaluate if content is relevant to the topic. Should be in the form: provider/model-name."
        },
    )

    report_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating information reports that act as input to posts. Should be in the form: provider/model-name."
        },
    )