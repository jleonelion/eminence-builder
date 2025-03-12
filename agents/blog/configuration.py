"""Define the configurable parameters for the agent."""

from dataclasses import dataclass, field

from agents.configuration import BaseConfiguration


@dataclass(kw_only=True)
class BlogConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    research_details_model: str = field(
        default="openai/gpt-4o",
        metadata={
            "description": "The language model used. Should be in the form: provider/model-name."
        },
    )
    research_details_model_kwargs: dict = field(
        default_factory=lambda: {"temperature": 0.0},
        metadata={"description": "Keyword arguments to pass to the model."},
    )
    pplx_researcher: bool = field(
        default=False,
        metadata={"description": "Enable debug mode."},
    )
