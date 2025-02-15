"""State management for the ingest-data graph.

This module defines the state structures used in the ingest-data graph.
"""

from dataclasses import dataclass, field
from typing import Annotated, Optional
from langchain_core.messages import HumanMessage

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from backend.utils import reduce_docs


@dataclass(kw_only=True)
class ReflectionState:
    """State of the reflection graph / agent."""

    original_text: str = field(
        default="",
        metadata={"description": "The original text to be reflected upon."},
    )
    revised_text: str = field(
        default="",
        metadata={"description": "The revised text."},
    )
    user_response: Optional[HumanMessage] = field(
        metadata={"description": "The user's response triggering the reflection."},
    )
