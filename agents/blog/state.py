"""This module defines the state structures used in the agent graph."""

import operator
from dataclasses import dataclass, field
from typing import Annotated, Optional

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from agents.blog.schema import BlogRequest, Section
from agents.utils import reduce_docs


@dataclass(kw_only=True)
class BlogState:
    """State structure for the agent."""

    messages: Annotated[list[AnyMessage], add_messages] = field(
        default_factory=list,
        metadata={"description": "History of chat messages."},
    )
    blog_request: Optional[BlogRequest] = field(
        default=None,
        metadata={"description": "User inputs describing desired blog."},
    )
    reference_content: Annotated[list[Document], reduce_docs] = field(
        default_factory=list,
        metadata={
            "description": "Collection of documents to reference when writing the blog."
        },
    )
    sections: list[Section] = field(
        default_factory=list,
        metadata={"description": "Sections of the blog post."},
    )
    completed_sections: Annotated[list, operator.add] = field(
        default_factory=list,
        metadata={"description": "Sections that have been completed."},
    )
    blog_structure: str = field(
        default="",
        metadata={"description": "The structure of the blog post."},
    )
    final_blog: str = field(
        default="",
        metadata={"description": "The final blog post."},
    )
