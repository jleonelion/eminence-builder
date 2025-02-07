"""State management for the ingest-data graph.

This module defines the state structures used in the ingest-data graph.
"""

from dataclasses import dataclass, field
from operator import add
from typing import Annotated, TypedDict, Union, Literal
from datetime import datetime

from langchain_core.messages import AnyMessage
from langchain_core.documents import Document
from langgraph.graph import add_messages, END
from agents.utils import reduce_docs, unique_list

PostDate = Annotated[Union[datetime, Literal["p1", "p2", "p3"]], field(default_factory=str)]

@dataclass(kw_only=True)
class Image(TypedDict):
    """Structure to image information"""
    imageUrl: str
    mimeType: str

@dataclass(kw_only=True)
class GeneratePostState:
    """State structure for the generate-post graph."""
    messages: Annotated[list[AnyMessage], add_messages] = field(
        default_factory=list,
        metadata={
            "description": "History of chat messages."
        },
    )
    topic: str = field(
        default="",
        metadata={
            "description": "The topic to verify the content against."
        },
    )
    style: str = field(
        default="default",
        metadata={
            "description": "The style to use when creating the post.",
            "choices": ["default", "news", "education"],
        },
    )
    links: Annotated[list[str], unique_list] = field(
        default_factory=list,
        metadata={
            "description": "The sources (URL links) of content to verify."
        },
    )
    report: str = ""
    """Report generated on the content of the messages.  Used as context for the post generation."""
    page_contents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Page content used in the verification nodes.  Will be used in the report generation node."""
    relevant_links: Annotated[list[str], unique_list] = field(default_factory=list)
    """Unique list of links found in the message"""
    post: str = ""
    """The generated post"""
    schedule_date: PostDate = None
    """The data to schedule the post for."""
    user_response: str = None
    """Response from the user for the post.  Typically used to request changes to be made to the post."""
    # next: Annotated[Optional[str], lambda x: x in ("schedulePost", "rewritePost", "updateScheduleDate", "unknownResponse", END, None)] = None
    next: str = None # TODO: figure out way to ensure only valid node names are used
    """The node to execute next."""
    image: Image = None
    """ The image to attach to the post and the MIME type of the image. """
    image_options: list[str] = field(default_factory=list)
    """ The image options to provide the user. """
    condense_count: int = 0 # TODO: make sure this can handle parrallelism
    object_id: str = None
    """The object ID of the post stored in the mongo database."""

