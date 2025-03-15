"""Utility functions for the agent."""

import asyncio

from langsmith import traceable
from tavily import AsyncTavilyClient, TavilyClient

from agents.blog.configuration import BlogConfiguration
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
