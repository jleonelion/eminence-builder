"""Utility functions for the agent."""

from typing import Any

from langchain_core.prompts import SystemMessagePromptTemplate

from agents.pplx_researcher.prompts import AGENT_PROMPT


def build_research_prompt(**kwargs: Any) -> SystemMessagePromptTemplate:
    """Build the research prompt."""
    return SystemMessagePromptTemplate.from_template(AGENT_PROMPT)
