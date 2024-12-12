"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.configuration import BaseConfiguration
from backend.retrieval_graph import prompts


@dataclass(kw_only=True)
class AgentConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    # models

    query_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider/model-name."
        },
    )

    blog_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating responses. Should be in the form: provider/model-name."
        },
    )

    # prompts and prompt parameters

    router_system_prompt: str = field(
        default=prompts.ROUTER_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for classifying user questions to route them to the correct node."
        },
    )

    more_info_system_prompt: str = field(
        default=prompts.MORE_INFO_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for asking for more information from the user."
        },
    )

    general_system_prompt: str = field(
        default=prompts.GENERAL_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for responding to general questions."
        },
    )

    research_plan_system_prompt: str = field(
        default=prompts.RESEARCH_PLAN_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for generating a research plan based on the user's question."
        },
    )

    research_plan_subtopic_count: int = field(
        default=3,
        metadata={
            "description": "The number of subtopics to consider when building the research plan."
        },
    )

    research_plan_max_steps: int = field(
        default=3,
        metadata={
            "description": "The maximum number of steps for the research plan."
        },
    )

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

    blogger_system_prompt: str = field(
        default=prompts.BLOGGER_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for generating blog post from research materials."
        },
    )
