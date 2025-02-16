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
        metadata={"description": "The original text to be reflected upon."},
    )
    revised_text: str = field(
        metadata={"description": "The revised text."},
    )
    post_style: str = field(
        default="default",
        metadata={"description": "Style associated with the text being anlayzed."},
    )
    editor_feedback: Optional[HumanMessage] = field(
        default=None,
        metadata={"description": "Feedback from the editor resulting in revised text."},
    )
    new_rules: list[str] = field(
        default_factory=list,
        metadata={"description": "Rules identified during reflection."},
    )
