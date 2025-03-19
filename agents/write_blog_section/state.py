"""This module defines the state structures used in the agent graph."""

from dataclasses import dataclass, field
from typing import Annotated, Literal, Optional

from langchain_core.documents import Document

from agents.blog.schema import Section
from agents.utils import reduce_docs


@dataclass(kw_only=True)
class WriteBlogSectionState:
    """State structure for the agent."""

    tavily_topic: Literal["general", "news"] = field(
        default="general",
        metadata={"description": "Type of search to perform ('news' or 'general')"},
    )
    # tavily_days: Optional[int] # Only applicable for news topic
    number_of_queries: int = field(
        default=5,
        metadata={"description": "Number web search queries to perform per section"},
    )
    section: Section = field(
        metadata={"description": "Section of the blog post to write."},
    )
    completed_sections: Optional[list[Section]] = field(
        default=None,
        metadata={"description": "Sections that have been completed."},
    )
    reference_content: Annotated[list[Document], reduce_docs] = field(
        metadata={
            "description": "Collection of documents to reference when writing the blog."
        },
    )
    word_limit: int = field(
        default=500,
        metadata={"description": "Word limit for the section being written."},
    )
    search_limit: int = field(
        default=3,
        metadata={
            "description": "Limit on number of searches to perform when writing content."
        },
    )
    completed_blog_sections: str = field(
        default="",
        metadata={
            "description": "String of any completed sections from research to write final sections"
        },
    )

    # TODO not sure if these are needed
    # blog_request: Optional[BlogRequest] = field(
    #     default=None,
    #     metadata={"description": "User inputs describing desired blog."},
    # )
    # search_queries: list[SearchQuery] # List of search queries
    # source_str: str # String of formatted source content from web search


@dataclass(kw_only=True)
class WriteBlogSectionOutput:
    """Output structure for the agent."""

    completed_sections: Optional[list[Section]] = field(
        default=None,
        metadata={"description": "Sections that have been completed."},
    )
