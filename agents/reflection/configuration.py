"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated
from browser_use.browser.browser import BrowserConfig

from agents.configuration import BaseConfiguration
import os


@dataclass(kw_only=True)
class ReflectionConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    reflection_model: str = field(
        default="openai/gpt-4o",
        metadata={
            "description": "The language model used to validate images. Should be in the form: provider/model-name."
        },
    )
    reflection_model_kwargs: dict = field(
        default_factory=lambda: {"temperature": 0.0},
        metadata={"description": "Keyword arguments to pass to the rewrite model."},
    )
