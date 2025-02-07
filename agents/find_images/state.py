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
class FindImagesState:
    """State of the find images graph / agent."""
    page_contents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Page content used in the verification nodes.  Will be used in the report generation node."""
    relevant_links: list[str] = field(default_factory=list)
    """Unique list of links found in the message"""
    image_options: list[str] = field(default_factory=list)
    """List of image options to choose from"""
    report: str = ""
    """Report generated on the content of the messages.  Used as context for the post generation."""
    post: str = ""
    """The generated post"""

