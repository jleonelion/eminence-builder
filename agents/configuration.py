"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Any, Literal, Optional, Type, TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config

MODEL_NAME_TO_RESPONSE_MODEL = {
    "anthropic_claude_3_5_sonnet": "anthropic/claude-3-5-sonnet-20240620",
}


@dataclass(kw_only=True)
class BaseConfiguration:
    """Base configuration class for agents."""
