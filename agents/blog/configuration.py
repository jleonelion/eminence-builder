"""Define the configurable parameters for the agent."""

from dataclasses import dataclass, field

from agents.configuration import BaseConfiguration
from agents.pplx_researcher.configuration import PplxResearchAgentConfiguration


@dataclass(kw_only=True)
class BlogConfiguration(BaseConfiguration):
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
    extract_details_model: str = field(
        default=None,
        metadata={
            "description": "The language model used. Should be in the form: provider/model-name."
        },
    )
    extract_details_model_kwargs: dict = field(
        default=None,
        metadata={"description": "Keyword arguments to pass to the model."},
    )
    define_structure_model: str = field(
        default=None,
        metadata={
            "description": "The language model used. Should be in the form: provider/model-name."
        },
    )
    define_structure_model_kwargs: dict = field(
        default=None,
        metadata={"description": "Keyword arguments to pass to the model."},
    )
    run_pplx_research: bool = field(
        default=True,
        metadata={"description": "Whether or not to run Perplexity deep search."},
    )
    pplx_config: PplxResearchAgentConfiguration = field(
        default_factory=PplxResearchAgentConfiguration,
        metadata={"description": "Configuration for the PPLX researcher."},
    )
    compile_final_blog_model: str = field(
        default=None,
        metadata={
            "description": "The language model used. Should be in the form: provider/model-name."
        },
    )
    compile_final_blog_model_kwargs: dict = field(
        default=None,
        metadata={"description": "Keyword arguments to pass to the model."},
    )
