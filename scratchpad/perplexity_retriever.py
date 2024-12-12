import os
import asyncio
import inspect
from contextlib import contextmanager
from typing import Iterator
from langchain_community.chat_models import ChatPerplexity
from langchain_core.retrievers import BaseRetriever
from backend.configuration import BaseConfiguration
import dotenv

dotenv.load_dotenv()


@contextmanager
def make_perplexity_retriever(
    configuration: BaseConfiguration
) -> Iterator[BaseRetriever]:
    # Get the constructor parameters of TavilySearchAPIRetriever
    constructor_params = inspect.signature(ChatPerplexity).parameters

    # Filter the configuration properties to match the constructor parameters
    config_dict = {key: value for key, value in configuration.__dict__.items(
    ) if key in constructor_params}

    # Instantiate TavilySearchAPIRetriever with the filtered properties
    retriever = ChatPerplexity(**config_dict)
    yield retriever


config = {
    "metadata": {
        "created_by": "system",
        "graph_id": "chat",
        "run_attempt": 1,
        "langgraph_version": "0.2.58",
        "langgraph_plan": "developer",
        "langgraph_host": "self-hosted",
        "thread_id": "77ef1711-1e8c-4b90-880f-896908dba6f0",
        "run_id": "1efb85f8-3cae-6392-892f-f63729070d09",
        "assistant_id": "eb6db400-e3c8-5d06-a834-015cb89efe69",
        "user_id": "",
        "langgraph_step": 2,
        "langgraph_node": "retrieve_documents",
        "langgraph_checkpoint_ns": "conduct_perplexity_research:70dfe250-2884-77fe-2d67-65415a5b5c4d|retrieve_documents:412cec32-df9e-a6e2-158d-0a0089c59456",
        "checkpoint_ns": "conduct_perplexity_research:70dfe250-2884-77fe-2d67-65415a5b5c4d",
        "retriever_provider": "perplexity"
    },
    "recursion_limit": 100,
    "configurable": {
        "thread_id": "77ef1711-1e8c-4b90-880f-896908dba6f0",
        "run_id": "1efb85f8-3cae-6392-892f-f63729070d09",
        "graph_id": "chat",
        "assistant_id": "eb6db400-e3c8-5d06-a834-015cb89efe69",
        "user_id": "",
    }
}

configuration = BaseConfiguration.from_runnable_config(config)


async def main():
    with make_perplexity_retriever(configuration) as retriever:
        response = await retriever.ainvoke("key components of effective prompt", config)
        print(response)

asyncio.run(main())
