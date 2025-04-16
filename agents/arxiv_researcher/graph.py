"""This module defines the ArxivResearchAgent class, which is responsible for conducting academic research using the ArXiv API and a language model.

Classes:
    ArxivResearchAgent: A class for conducting academic research using the ArXiv API and a language model.
Functions:
"""

import logging
from typing import List

from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper
from langchain_core.documents import Document

from agents.arxiv_researcher.configuration import ArxivResearcherConfiguration
from agents.arxiv_researcher.utils import build_agent_prompt
from agents.utils import load_chat_model

logger = logging.getLogger(__name__)


class ArxivResearchAgent:
    """ArxivResearchAgent is responsible for conducting academic research using the ArXiv API and a language model.

    Attributes:
        llm (LanguageModel): The language model used for generating and processing research queries.
        arxiv_tool (ArxivQueryRun): The tool for querying the ArXiv API.
        agent (AgentExecutor): The agent executor configured for research paper discovery.

    Methods:
        create_research_agent() -> AgentExecutor:
            Create and configure a ReAct agent for academic research.
        research_topic(topic: str) -> List[Document]:
            Conduct research on a specified topic and return the top research papers as documents.
        _process_research_results(response: dict) -> List[Document]:
            Process and transform research results into structured documents.
    """

    def __init__(self, config: ArxivResearcherConfiguration):
        """Initialize the Arxiv Research Agent.

        Args:
            api_key (str, optional): OpenAI API key
            model (str, optional): Language model to use
        """
        # Initialize Language Model
        self.llm = load_chat_model(config.model, config.model_kwargs)

        # Create Arxiv Tool
        self.arxiv_tool = ArxivQueryRun(
            api_wrapper=ArxivAPIWrapper(
                max_results=config.max_results,  # Limit initial search results
                sort_by=config.sort_by,  # Sort by relevance or date
            )
        )

        # Create the agent
        self.agent = self.create_research_agent()

    def create_research_agent(self):
        """Create a ReAct agent for academic research.

        Returns:
            AgentExecutor: Configured agent for research paper discovery
        """
        # Pull the standard ReAct prompt
        prompt = build_agent_prompt()

        # Create the agent
        agent = create_react_agent(llm=self.llm, tools=[self.arxiv_tool], prompt=prompt)

        # Create an agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=[self.arxiv_tool],
            verbose=True,  # Enable detailed logging
            max_iterations=5,  # Prevent infinite loops
            handle_parsing_errors=True,  # Robust error handling
        )

        return agent_executor

    def research_topic(self, topic: str) -> List[Document]:
        """Conduct research on a specified topic.

        Args:
            topic (str): Research topic to investigate

        Returns:
            List[Document]: Top research papers as documents
        """
        # Refined search query
        research_query = f"""
        Find the most recent and highest-quality research papers on {topic}. 
        Focus on papers that:
        - Are published in the last 2 years
        - Represent cutting-edge research
        - Have significant academic impact
        """

        # Execute research
        try:
            response = self.agent.invoke({"input": research_query})

            # Extract and process results
            research_results = self._process_research_results(response)

            return research_results

        except Exception as e:
            logger.error(f"Research Error: {e}")
            raise Exception(f"Research Error: {e}")

    def _process_research_results(self, response: dict) -> List[Document]:
        """Process and transform research results into Documents.

        Args:
            response (dict): Agent response containing research results

        Returns:
            List[Document]: Processed research papers
        """
        # Extract paper information from response
        output = response.get("output", "")

        # Use LLM to extract structured paper information
        extraction_prompt = f"""
        From the following research results, extract structured information about research papers:
        
        {output}
        
        For each paper, provide:
        - Title
        - Authors
        - Publication Date
        - Key Contributions
        - ArXiv Link
        
        Return results as a valid JSON list of dictionaries. Ensure the JSON is properly formatted.
        """

        try:
            # Invoke LLM for structured extraction
            extraction_response = self.llm.invoke(extraction_prompt)
            extraction_text = extraction_response.content

            # Use JsonOutputParser for robust JSON parsing
            from langchain_core.output_parsers import JsonOutputParser

            json_parser = JsonOutputParser()

            try:
                # Attempt to parse the JSON
                papers_data = json_parser.parse(extraction_text)
            except Exception as json_parse_error:
                logger.error(f"JSON Parsing Error: {json_parse_error}")
                # Fallback to manual parsing
                import json

                try:
                    papers_data = json.loads(extraction_text)
                except json.JSONDecodeError:
                    logger.error("Manual JSON Parsing Failed")
                    return []

            # Convert parsed data to Documents
            research_documents = []
            for paper in papers_data:
                document = Document(
                    page_content=f"""
                    Title: {paper.get("Title", "N/A")}
                    Authors: {", ".join(paper.get("Authors", []))}
                    Publication Date: {paper.get("Publication Date", "N/A")}
                    Key Contributions: {paper.get("Key Contributions", "N/A")}
                    ArXiv Link: {paper.get("ArXiv Link", "N/A")}
                    """,
                    metadata={
                        "title": paper.get("Title", ""),
                        "authors": paper.get("Authors", []),
                        "publication_date": paper.get("Publication Date", ""),
                        "link": paper.get("ArXiv Link", ""),
                        "source": "ArXiv Research Agent",
                    },
                )
                research_documents.append(document)

            return research_documents

        except Exception as e:
            logger.error(f"Research result processing error: {e}")
            return []


config = ArxivResearcherConfiguration()
agent = ArxivResearchAgent(config)
research_results = agent.research_topic("model context protocol")
