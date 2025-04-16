"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Optional, Type, TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config

MODEL_NAME_TO_RESPONSE_MODEL = {
    "anthropic_claude_3_5_sonnet": "anthropic/claude-3-5-sonnet-20240620",
}


@dataclass(kw_only=True)
class BaseConfiguration:
    """Base configuration class for agents."""

    @classmethod
    def from_runnable_config(
        cls: Type[T], config: Optional[RunnableConfig] = None
    ) -> T:
        """Create an IndexConfiguration instance from a RunnableConfig object.

        Args:
            cls (Type[T]): The class itself.
            config (Optional[RunnableConfig]): The configuration object to use.

        Returns:
            T: An instance of IndexConfiguration with the specified configuration.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        # configurable = _update_configurable_for_backwards_compatibility(configurable)
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

    mongo_url: str = field(
        default="mongodb://localhost:27017/",
        # default_factory=lambda: os.getenv("MONGODB_URL", "mongodb://localhost:27017/"),
        metadata={"description": "The connection string to MongoDB."},
    )
    mongo_db: str = field(
        default="social-media",
        # default_factory=lambda: os.getenv("MONGODB_DATABASE", "social-media"),
        metadata={"description": "The name of the MongoDB database."},
    )
    mongo_collection_linkedin_posts: str = field(
        default="linkedin-posts",
        # default_factory=lambda: os.getenv("MONGODB_COLLECTION_LINKEDIN", "linkedin-posts"),
        metadata={
            "description": "The name of the MongoDB collection to store linked in posts."
        },
    )
    mongo_collection_rules: str = field(
        default="rules",
        # default_factory=lambda: os.getenv("MONGODB_COLLECTION_RULES", "rules"),
        metadata={
            "description": "The name of the MongoDB collection to store rules for writing posts."
        },
    )
    mongo_collection_blog_posts: str = field(
        default="blog-posts",
        metadata={
            "description": "The name of the MongoDB collection to store blog posts."
        },
    )


T = TypeVar("T", bound=BaseConfiguration)
