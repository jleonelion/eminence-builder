"""Define the configurable parameters for the agent."""

from dataclasses import dataclass, field

from agents.configuration import BaseConfiguration


@dataclass(kw_only=True)
class BlogWriteSectionConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    default_model: str = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The language model used. Should be in the form: provider/model-name."
        },
    )
    default_model_kwargs: dict = field(
        default_factory=lambda: {"temperature": 0.0},
        metadata={"description": "Keyword arguments to pass to the model."},
    )
    max_results: int = field(
        default=5,
        metadata={"description": "Maximum number of search results to return."},
    )
