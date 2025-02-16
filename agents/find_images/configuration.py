"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated

from agents.configuration import BaseConfiguration
import os

@dataclass(kw_only=True)
class FindImagesConfiguration(BaseConfiguration):
    """The configuration for the agent."""
    text_only_mode: bool = field(
        default=True,
        metadata={
            "description": "Whether or not posts should be plain text."
        },
    )
    validate_image_model: str = field(
        default="openai/gpt-4o",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used to validate images. Should be in the form: provider/model-name."
        },
    )
    rerank_image_model: str = field(
        default="openai/gpt-4o",
        # default="vertex/gemini-2.0-flash-exp",
        metadata={
            "description": "The language model used to validate images. Should be in the form: provider/model-name."
        },
    )
