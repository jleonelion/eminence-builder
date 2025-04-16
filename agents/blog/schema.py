"""Schema classes for agent."""

from typing import List, Optional

from pydantic import BaseModel, Field


class BlogRequest(BaseModel):
    """Details for a research project."""

    main_topic: str = Field(description="The main topic that research is focused on.")
    related_topics: Optional[list[str]] = Field(
        description="A list of topics closely related to the main topic that should also be examined when researching the main topic."
    )
    priority_links: list[str] = Field(
        description="A list of URLs provided by the user.  If the user did not provide any links, this should be empty"
    )
    message: Optional[str] = Field(
        description="The original message from the user describing the desired blog post.  If the user provided URLs in the request those should be ommitted.  If the user did not request a blog post this should be empty."
    )


class Section(BaseModel):
    """Details for a section of the report."""

    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section.",
    )
    research: bool = Field(
        description="Whether to perform web research for this section of the report."
    )
    content: Optional[str] = Field(description="The content of the section.")


class Sections(BaseModel):
    """Details for the sections of the report."""

    sections: List[Section] = Field(
        description="Sections of the report.",
    )


class SearchQuery(BaseModel):
    """Details for a search query."""

    search_query: str = Field(None, description="Query for web search.")


class Queries(BaseModel):
    """Details for a list of search queries."""

    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )
