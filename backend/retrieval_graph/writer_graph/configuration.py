"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.configuration import BaseConfiguration
from backend.retrieval_graph import prompts


@dataclass(kw_only=True)
class AgentConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    # models

    writer_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for writing the content. Should be in the form: provider/model-name."
        },
    )

    editor_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for editing the response. Should be in the form: provider/model-name."
        },
    )

    max_iterations: int = field(
        default=3,
        metadata={
            "description": "The maximum number of iterations for the writer and editor."
        },
    )

    # prompts and prompt parameters

    writer_system_prmpt: str = field(
        metadata={
            "description": "The system prompt used for writing."
        },
    )

    editor_system_prmpt: str = field(
        metadata={
            "description": "The system prompt used for editing."
        },
    )
