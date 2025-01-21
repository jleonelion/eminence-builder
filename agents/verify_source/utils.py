from agents.verify_source.state import VerifyLinksState
from agents.verify_source.configuration import VerifyLinksConfiguration
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from langchain_community.document_loaders import FireCrawlLoader
from agents.prompts import RELEVANCE_EVALUATION_SYSTEM_PROMPT
from agents.utils import load_chat_model

# TODO: consider moving these dataclasses to models.py
@dataclass(kw_only=True)
class UrlContents:
    """Contents of a defined URL loaded into memory."""

    content: str = field(
        metadata={
            "description": "Content of the URL."
        },
    )
    image_urls: list[str] = field(
        default=None,
        metadata={
            "description": "Image URLs found in the content."
        },
    )

class RelevanceEvaluation(BaseModel):
    """Schema for evaluating the relevance of a source."""

    reasoning: str = Field(
        description = "Reasoning for why the content is or isn't relavant to the topic."
    )
    relevant: bool = Field(
        description = "Final verdict if the content is relevant to the topic."
    )

async def get_url_contents(
    state: VerifyLinksState, config: VerifyLinksConfiguration
) -> UrlContents:
    """Get content from state.url"""
    # TODO: add support for using other loaders defined in the configuration
    loader = FireCrawlLoader(
        url = state.link,
        mode = "scrape",
        params={
            "formats": ["markdown", "screenshot"],
        },
    )
    docs = await loader.aload()
    docsText = ""
    for doc in docs:
        docsText += doc.page_content + "\n"
    if docsText:
        return UrlContents(content=docsText, image_urls=[
            url for doc in docs for url in (doc.metadata.get("image", []), doc.metadata.get("ogImage", [])) if url
        ])
    else:
        # TODO: attempt to retrieve content from other loaders
        raise ValueError(f"Failed to fetch content from {state.link}.")

def get_relevance_eval_system_prompt(
    state: VerifyLinksState, config: VerifyLinksConfiguration
) -> str:
    """Get content rules."""
    return RELEVANCE_EVALUATION_SYSTEM_PROMPT.format(topic=state.topic)
    
