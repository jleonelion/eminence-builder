"""State management for the verify links graph."""

from dataclasses import dataclass, field
from typing import Annotated

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from agents.utils import reduce_docs, unique_list

# TODO: enhance verify source graph to handle multiple sources
@dataclass(kw_only=True)
class VerifyLinksState:
    """State of the verify links graph."""
    topic: str = field(
        metadata={
            "description": "The topic to verify the content against."
        },
    )
    links: Annotated[list[str], unique_list] = field(
        default_factory=list,
        metadata={
            "description": "The sources (URL links) of content to verify."
        },
    )
    """Messages including the initial user prompt, feedback from the editor, and feedback from user"""
    page_contents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
    """Page content used in the verification nodes.  Will be used in the report generation node."""
    relevant_links: Annotated[list[str], unique_list] = field(default_factory=list)
    # TODO: implement image options
    #     imageOptions: Annotation<string[]>({
    #     reducer: (_state, update) => update,
    #     default: () => [],
    #   }),


@dataclass(kw_only=True)
class VerifySingleLinkState:
    """State of the verify sources graph."""

    link: str = field(
        metadata={
            "description": "The source (a URL link) of content to verify."
        },
    )
    topic: str = field(
        metadata={
            "description": "The topic to verify the content against."
        },
    )

# @dataclass(kw_only=True)
# class VerifyGeneralSourceReturnState:
#     """When the source url points to a general web page, this is returned."""

#     relevant_links: Annotated[list[str], unique_list] = field(default_factory=list)
#     """links referenced in the web page that are relevant to the topic"""
#     page_contents: Annotated[list[Document], reduce_docs] = field(default_factory=list)
#     """Contents of the web page that was verified"""
