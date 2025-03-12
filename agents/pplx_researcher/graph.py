"""Core logic for the agent."""

import logging
import re

from langchain_core.documents import Document

from agents.pplx_researcher.configuration import PplxResearchAgentConfiguration
from agents.utils import load_chat_model

logger = logging.getLogger(__name__)


class PplxResearchAgent:
    """PplxResearchAgent is responsible for conducting research on specified topics using a language model.

    This agent initializes with a given configuration, conducts research on topics, and processes the research results into structured documents.

    Methods:
        __init__(config: PplxResearchAgentConfiguration):
            Initialize the PplxResearcher agent with the given configuration.
        research_topic(topic: str) -> str:
            Conduct research on a specified topic and return the research results.
        _process_research_results(response: dict) -> List[Document]:
            Process and transform research results into Documents.
    """

    def __init__(self, config: PplxResearchAgentConfiguration):
        """Initialize the PplxResearcher agent with the given configuration.

        Args:
            config (PplxResearchAgentConfiguration): The configuration object containing
                the settings for the PplxResearcher agent, including the model type and
                any additional keyword arguments for the model.

        Attributes:
            llm: The language model loaded based on the provided configuration.
        """
        # Initialize Language Model
        self.llm = load_chat_model(config.model, config.model_kwargs)

    def research_topic(self, topic: str) -> Document:
        """Conduct research on a specified topic.

        Args:
            topic (str): Research topic to investigate
        """
        # invoke llm, explicitly setting stream to False to avoid errors
        response = self.llm.invoke(input=topic, stream=False)
        # Strip everything between <think> tags
        cleaned_content = re.sub(
            r"<think>.*?</think>", "", response.content, flags=re.DOTALL
        )
        response.content = cleaned_content.strip()
        document = Document(
            page_content=response.content, metadata=response.additional_kwargs
        )
        return document


# config = PplxResearchAgentConfiguration()
# agent = PplxResearchAgent(config)
# research_results = agent.research_topic("model context protocol")
# print(research_results)
