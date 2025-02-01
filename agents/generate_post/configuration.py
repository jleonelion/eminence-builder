"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated

from agents.configuration import BaseConfiguration
import os

@dataclass(kw_only=True)
class GeneratePostConfiguration(BaseConfiguration):
    """The configuration for the agent."""
    text_only_mode: bool = field(
        default=True,
        metadata={
            "description": "Whether or not posts should be plain text."
        },
    )
    parse_request_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating posts Should be in the form: provider/model-name."
        },
    )
    post_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating posts Should be in the form: provider/model-name."
        },
    )
    report_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used for generating information reports that act as input to posts. Should be in the form: provider/model-name."
        },
    )
    rewrite_model: str = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The language model used for rewriting posts. Should be in the form: provider/model-name."
        },
    )
    rewrite_model_kwargs: dict = field(
        default_factory=dict,
        metadata={
            "description": "Keyword arguments to pass to the rewrite model."
        },
    )
    route_model: str = field(
        default="openai/gpt-4o-mini",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "Model used to route user responses Should be in the form: provider/model-name."
        },
    )
    max_post_length: int = field(
        default=1000,
        metadata={
            "description": "The maximum length of the post."
        },
    )
    max_condense_count: int = field(
        default=3,
        metadata={
            "description": "The maximum iterations spent condensing post size."
        },
    )
    timezone: str = field(
        default="America/Los_Angeles",
        metadata={
            "description": "The timezone to use for scheduling posts."
        },
    )
    mongo_url: str = field(
        default="mongodb://localhost:27017/",
        # default_factory=lambda: os.getenv("MONGODB_URL", "mongodb://localhost:27017/"),
        metadata={
            "description": "The connection string to MongoDB."
        },
    )
    mongo_db: str = field(
        default="social-media",
        # default_factory=lambda: os.getenv("MONGODB_DATABASE", "social-media"),
        metadata={
            "description": "The name of the MongoDB database."
        },
    )
    mongo_collection_linkedin_posts: str = field(
        default="linkedin-posts",
        # default_factory=lambda: os.getenv("MONGODB_COLLECTION_LINKEDIN", "linkedin-posts"),
        metadata={
            "description": "The name of the MongoDB collection to store linked in posts."
        },
    )