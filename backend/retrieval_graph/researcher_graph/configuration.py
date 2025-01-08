"""Define the configurable parameters for the research agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Literal

from backend.configuration import BaseConfiguration
from backend.retrieval_graph import prompts


@dataclass(kw_only=True)
class ResearchAgentConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    # models
    query_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider/model-name."
        },
    )

    # prompts and prompt parameters
    generate_queries_system_prompt: str = field(
        default=prompts.GENERATE_QUERIES_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used by the researcher to generate queries based on a step in the research plan."
        },
    )

    generate_queries_count: int = field(
        default=3,
        metadata={
            "description": "The number of queries to generate for each step in the research plan."
        },
    )

    retriever_provider: Annotated[
        Literal["weaviate", "tavily"],
        {"__template_metadata__": {"kind": "retriever"}},
    ] = field(
        default="tavily",
        metadata={"description": "The vector store provider to use for retrieval."},
    )


