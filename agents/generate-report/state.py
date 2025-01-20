"""State management for the ingest-data graph.

This module defines the state structures used in the ingest-data graph.
"""

from dataclasses import dataclass, field
from typing import Annotated

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from backend.utils import reduce_docs


@dataclass(kw_only=True)
class IngestDataState:
    """State of the writer graph / agent."""

    messages: Annotated[list[AnyMessage], add_messages]
    """Messages including the initial user prompt, feedback from the editor, and feedback from user"""
    context: str = ""
    """Additional context to provide.  This information is given a higher level of influence on the writing."""
    documents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """List of documents to reference when writing."""
    critiques: Annotated[list[Critique], add] = field(default_factory=list)
    """List of critiques received from the editor."""
