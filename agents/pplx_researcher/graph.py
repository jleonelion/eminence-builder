"""Core logic for the agent."""

import logging

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from agents.pplx_researcher.configuration import PplxResearchAgentConfiguration
from agents.pplx_researcher.utils import build_research_prompt
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
        # Execute research
        system_prompt_template = build_research_prompt()
        full_prompt = ChatPromptTemplate.from_messages(
            [system_prompt_template, HumanMessage(content=topic)]
        )
        chain = full_prompt | self.llm
        response = chain.invoke({"topic": topic})
        document = Document(
            page_content=response.content, metadata=response.additional_kwargs
        )
        return document


# config = PplxResearchAgentConfiguration()
# agent = PplxResearchAgent(config)
# research_results = agent.research_topic("model context protocol")
# print(research_results)
