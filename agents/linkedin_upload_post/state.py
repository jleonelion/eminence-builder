"""State management for the ingest-data graph.

This module defines the state structures used in the ingest-data graph.
"""

from dataclasses import dataclass, field
from typing import Annotated, Optional

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from backend.utils import reduce_docs


@dataclass(kw_only=True)
class LinkedInUploadPostState:
    """State of the linkedin upload post graph / agent."""

    post: Optional[dict[any]] = field(default_factory=dict)
    """document from mongodb with information to be uploaded"""
