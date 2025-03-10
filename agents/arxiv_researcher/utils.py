"""This module provides utility functions for the arxiv_researcher agent.

Functions:
    build_agent_prompt: Constructs and returns a PromptTemplate using the AGENT_PROMPT.
"""

from langchain_core.prompts import PromptTemplate

from agents.arxiv_researcher.prompts import AGENT_PROMPT


def build_agent_prompt() -> PromptTemplate:
    """Build the reflection prompt."""
    return PromptTemplate.from_template(AGENT_PROMPT)
