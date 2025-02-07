"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated

from agents.configuration import BaseConfiguration
import os

@dataclass(kw_only=True)
class FindImagesConfiguration(BaseConfiguration):
    """The configuration for the agent."""
    text_only_mode: bool = field(
        default=True,
        metadata={
            "description": "Whether or not posts should be plain text."
        },
    )
    validate_image_model: str = field(
        default="openai/gpt-4o",
        # default="anthropic/claude-3-sonnet-20240229",
        metadata={
            "description": "The language model used to validate images. Should be in the form: provider/model-name."
        },
    )
    rerank_image_model: str = field(
        default="openai/gpt-4o",
        # default="vertex/gemini-2.0-flash-exp",
        metadata={
            "description": "The language model used to validate images. Should be in the form: provider/model-name."
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