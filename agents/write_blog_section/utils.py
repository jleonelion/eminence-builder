"""Utility functions for the agent."""

import asyncio

import yaml
from langchain_core.documents import Document
from langsmith import traceable
from tavily import AsyncTavilyClient, TavilyClient

from agents.blog.configuration import BlogConfiguration
from agents.blog.schema import Section
from agents.blog.state import BlogState


@traceable
def tavily_search(query):
    """Search the web using the Tavily API.

    Args:
        query (str): The search query to execute

    Returns:
        dict: Tavily search response containing:
            - results (list): List of search result dictionaries, each containing:
                - title (str): Title of the search result
                - url (str): URL of the search result
                - content (str): Snippet/summary of the content
                - raw_content (str): Full content of the page if available
    """
    tavily_client = TavilyClient()
    return tavily_client.search(query, max_results=5, include_raw_content=True)


@traceable
async def tavily_search_async(search_queries, tavily_topic, tavily_days):
    """Perform concurrent web searches using the Tavily API.

    Args:
        search_queries (List[SearchQuery]): List of search queries to process
        tavily_topic (str): Type of search to perform ('news' or 'general')
        tavily_days (int): Number of days to look back for news articles (only used when tavily_topic='news')

    Returns:
        List[dict]: List of search results from Tavily API, one per query

    Note:
        For news searches, each result will include articles from the last `tavily_days` days.
        For general searches, the time range is unrestricted.
    """
    tavily_async_client = AsyncTavilyClient()
    search_tasks = []

    for query in search_queries:
        if tavily_topic == "news":
            search_tasks.append(
                tavily_async_client.search(
                    query,
                    max_results=5,
                    include_raw_content=True,
                    topic="news",
                    days=tavily_days,
                )
            )
        else:
            search_tasks.append(
                tavily_async_client.search(
                    query, max_results=5, include_raw_content=True, topic="general"
                )
            )

    # Execute all searches concurrently
    search_docs = await asyncio.gather(*search_tasks)

    return search_docs


def build_sections_approval(state: BlogState, config: BlogConfiguration) -> dict:
    """Build the sections approval prompt."""
    sections = state.sections
    sections_str = "\n".join(
        [f"{i + 1}. {section.name}" for i, section in enumerate(sections)]
    )
    return f"""
# Confirm Blog Sections
  
Sections for the blog post need your approval.

## Sections:
```
{sections_str}
```
## Instructions

There are a few different actions which can be taken:\n
- **Edit**: Updated sections submitted will be used to generate blog post.
- **Accept**: If 'accept' is selected, the post will be generated using the define sections.
- **Ignore**: If 'ignore' is selected, this post will not generated and the thread will end.
"""


def load_documents_from_yaml(yaml_file_path):
    """Load documents from a YAML file and convert them to LangChain Document objects.

    Args:
        yaml_file_path (str): Path to the YAML file

    Returns:
        list: A list of LangChain Document objects
    """
    with open(yaml_file_path) as file:
        yaml_data = yaml.safe_load(file)

    documents = []

    # Assuming the YAML has a 'reference_content' key with a list of documents
    for doc_data in yaml_data.get("reference_content", []):
        document = Document(
            page_content=doc_data.get("page_content", ""),
            metadata=doc_data.get("metadata", {}),
        )
        documents.append(document)

    return documents


def load_section_from_yaml(yaml_file_path) -> Section:
    """Load section from a YAML file and convert to Section object.

    Args:
        yaml_file_path (str): Path to the YAML file

    Returns:
        Section: A Section object populated with data from the YAML file
    """
    with open(yaml_file_path) as file:
        yaml_data = yaml.safe_load(file)

    section = Section(
        name=yaml_data.get("name", ""),
        description=yaml_data.get("description", ""),
        research=yaml_data.get("research", False),
        content=yaml_data.get("content", ""),
    )

    return section
