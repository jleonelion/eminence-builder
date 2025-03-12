"""Prompts for the agent."""

from typing import Any

from langchain_core.prompts import SystemMessagePromptTemplate

RESEARCH_DETAILS = """
Examine the user message to provide details that will focus research activities for a blog page.
"""


def build_research_details_prompt(**kwargs: Any) -> SystemMessagePromptTemplate:
    """Build the research prompt."""
    return SystemMessagePromptTemplate.from_template(RESEARCH_DETAILS)
