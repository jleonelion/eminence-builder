"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field

from agents.configuration import BaseConfiguration


@dataclass(kw_only=True)
class PplxResearchAgentConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    # https://docs.perplexity.ai/guides/model-cards
    model: str = field(
        default="perplexity/sonar-deep-research",
        metadata={
            "description": "The language model. Should be in the form: provider/model-name."
        },
    )
    model_kwargs: dict = field(
        default_factory=lambda: {"temperature": 0.7},
        metadata={"description": "Keyword arguments to pass to the rewrite model."},
    )

    max_results: int = field(
        default=10,
        metadata={
            "description": "Maximum number of results to return from the Arxiv API."
        },
    )

    sort_by: str = field(
        default="relevance",
        metadata={"description": "Sort the results by relevance or date."},
    )
