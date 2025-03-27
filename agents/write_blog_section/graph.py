"""Main graph for the agent."""

from typing import Annotated, List

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.document_loaders import PlaywrightURLLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from playwright.async_api import async_playwright

from agents.blog.schema import Section
from agents.utils import load_chat_model
from agents.write_blog_section.configuration import BlogWriteSectionConfiguration
from agents.write_blog_section.prompts import (
    build_section_writer_message,
    build_section_writer_system_prompt,
)
from agents.write_blog_section.state import (
    BlogWriteSectionOutput,
    BlogWriteSectionState,
)


async def create_async_playwright_browser():
    """Create and return an asynchronous Playwright browser instance."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        return browser


# Create Playwright browser and toolkit
async def initialize_browsing_tools():
    """Initialize and return browsing tools for the agent."""
    browser = await create_async_playwright_browser()
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)

    @tool
    async def custom_url_loader(
        url: Annotated[str, "The URL to load"],
    ) -> List[Document]:
        """Load and extract text content from a specific URL."""
        loader = PlaywrightURLLoader(urls=[url], remove_selectors=["header", "footer"])
        documents = await loader.aload()
        return documents

    # Combine Playwright tools with custom URL loader
    tools = toolkit.get_tools() + [custom_url_loader]

    return tools


async def write_section(
    state: BlogWriteSectionState, *, config: RunnableConfig
) -> BlogWriteSectionOutput:
    """Extract information from the user message to begin building a research plan."""
    agent_config = BlogWriteSectionConfiguration.from_runnable_config(config)

    llm = load_chat_model(
        fully_specified_name=agent_config.default_model,
        model_kwargs=agent_config.default_model_kwargs,
    )
    system_prompt = build_section_writer_system_prompt(state, agent_config)
    search_tool = TavilySearchResults(max_results=agent_config.max_results)
    browsing_tools = await initialize_browsing_tools()
    tools = [search_tool] + browsing_tools

    # Create the React agent to write section content
    react_agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt,
    )
    response = react_agent.invoke(
        {"messages": [build_section_writer_message(state, agent_config)]}
    )
    # store last message in response to section.content
    if isinstance(state.section, Section):
        state.section.content = response["messages"][-1].content
    else:
        state.section["content"] = response["messages"][-1].content

    return BlogWriteSectionOutput(completed_sections=[state.section])


# Define the graph
builder = StateGraph(
    state_schema=BlogWriteSectionState,
    config_schema=BlogWriteSectionConfiguration,
    output=BlogWriteSectionOutput,
)
builder.add_node(write_section)

builder.add_edge(START, "write_section")
builder.add_edge("write_section", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "Write Blog Section Graph"

# Example usage
# import yaml
# from agents.write_blog_section.utils import (
#     load_documents_from_yaml,
#     load_section_from_yaml,
# )
# async def main():
#     yaml_file_path = "/Users/jamesleone/code/eminence-builder/agents/write_blog_section/test.yaml"
#     # Load objects from "test.yaml" file
#     documents = load_documents_from_yaml(yaml_file_path)
#     section = load_section_from_yaml(yaml_file_path)
#     section_state = BlogWriteSectionState(reference_content=documents, section=section)
#     report_section = await graph.ainvoke(input=section_state)
#     print(report_section)

# # Run the async main function
# import asyncio
# asyncio.run(main())
