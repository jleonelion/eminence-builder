"""This module defines the state structures used in the agent graph."""

from dataclasses import dataclass, field
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


@dataclass(kw_only=True)
class ArxivResearcherState:
    """State structure for the agent."""

    messages: Annotated[list[AnyMessage], add_messages] = field(
        default_factory=list,
        metadata={"description": "History of chat messages."},
    )
