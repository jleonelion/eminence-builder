"""Schema classes for agent."""

from typing import Optional

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
