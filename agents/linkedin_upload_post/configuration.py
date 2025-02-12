"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated
from browser_use.browser.browser import BrowserConfig

from agents.configuration import BaseConfiguration
import os


@dataclass(kw_only=True)
class LinkedInUploadPostConfiguration(BaseConfiguration):
    """The configuration for the agent."""

    browser_model: str = field(
        default="openai/gpt-4o",
        metadata={
            "description": "The language model used to validate images. Should be in the form: provider/model-name."
        },
    )
    browser_model_kwargs: dict = field(
        default_factory=lambda: {"temperature": 0.0},
        metadata={"description": "Keyword arguments to pass to the rewrite model."},
    )
    mongo_url: str = field(
        # default="mongodb://localhost:27017/",
        default_factory=lambda: os.getenv("MONGODB_URL", "mongodb://localhost:27017/"),
        metadata={"description": "The connection string to MongoDB."},
    )
    mongo_db: str = field(
        # default="social-media",
        default_factory=lambda: os.getenv("MONGODB_DATABASE", "social-media"),
        metadata={"description": "The name of the MongoDB database."},
    )
    mongo_collection_linkedin_posts: str = field(
        # default="linkedin-posts",
        default_factory=lambda: os.getenv(
            "MONGODB_COLLECTION_LINKEDIN", "linkedin-posts"
        ),
        metadata={
            "description": "The name of the MongoDB collection to store linked in posts."
        },
    )
    browser_config: BrowserConfig = field(
        default_factory=lambda: BrowserConfig(
            headless=False,
            chrome_instance_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ),
        metadata={"description": "The configuration for the browser."},
    )
