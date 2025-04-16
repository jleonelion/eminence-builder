"""This module defines the state structures used in the agent graph."""

from operator import add
from typing import Annotated, Literal, Optional

from langchain_core.documents import Document
from pydantic import BaseModel

from agents.blog.schema import Section
from agents.utils import reduce_docs


class BlogWriteSectionState(BaseModel):
    """BlogWriteSectionState represents the state of the blog writing process.

    Attributes:
        tavily_topic (Literal["general", "news"]): The topic category for the blog section. Defaults to "general".
        tavily_days (Optional[int]): The number of days to consider for the topic. Defaults to None.
        number_of_queries (int): The number of queries to perform during the blog writing process. Defaults to 5.
        section (Section): The current section being worked on.
        completed_sections (list[Section]): A list of completed sections. Annotated with a custom `add` function.
        reference_content (list[Document]): A list of reference documents for the blog. Annotated with a custom `reduce_docs` function.
        word_limit (int): The maximum word limit for the blog section. Defaults to 500.
        search_limit (int): The maximum number of searches allowed. Defaults to 3.
        completed_blog_sections (str): A string representation of all completed blog sections.
    """

    tavily_topic: Literal["general", "news"] = "general"
    tavily_days: Optional[int] = None
    number_of_queries: int = 5
    section: Section
    completed_sections: Annotated[list[Section], add] = []
    reference_content: Annotated[list[Document], reduce_docs] = []
    word_limit: int = 500
    search_limit: int = 3
    completed_blog_sections: str = ""


class BlogWriteSectionOutput(BaseModel):
    """BlogWriteSectionOutput represents the output state of a blog writing section.

    Attributes:
        completed_sections (list[Section]): A list of completed sections for the blog.
            This field is annotated with an additional metadata `add`. Defaults to None.
    """

    completed_sections: Annotated[list[Section], add] = None
