"""This module defines the state structures used in the agent graph."""

from operator import add
from typing import Annotated, Optional

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from pydantic import BaseModel

from agents.blog.schema import BlogRequest, Section
from agents.utils import reduce_docs


class BlogState(BaseModel):
    """BlogState represents the state structure for the blog generation agent.

    Attributes:
        messages (list[AnyMessage]): A list of messages exchanged during the blog generation process.
        blog_request (Optional[BlogRequest]): The request object containing details about the blog to be generated.
        reference_content (list[Document]): A list of reference documents used to assist in blog creation.
            This field is annotated with a reducer function `reduce_docs` to process the documents.
        sections (list[Section]): A list of sections that make up the blog structure.
        completed_sections (list): A list of completed sections, annotated with an `add` function to handle updates.
        blog_structure (str): A string representation of the overall structure of the blog.
        final_blog (str): The final generated blog content as a string.
        completed_blog_sections (str): A string representation of all completed sections of the blog.
    """

    messages: list[AnyMessage] = []
    blog_request: Optional[BlogRequest]
    reference_content: Annotated[list[Document], reduce_docs] = []
    sections: list[Section] = []
    completed_sections: Annotated[list, add] = []
    blog_structure: str = ""
    final_blog: str = ""
    completed_blog_sections: str = ""
