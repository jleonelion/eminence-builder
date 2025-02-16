import asyncio
from langgraph_sdk import get_client, get_sync_client
from langgraph.pregel.remote import RemoteGraph
from agents.reflection.state import ReflectionState
from agents.generate_post.configuration import GeneratePostConfiguration

url = "http://localhost:2024"
graph_name = "reflection"

async def main():
    client = get_client(url=url)
    sync_client = get_sync_client(url=url)
    remote_graph = RemoteGraph(graph_name, url=url)
    await remote_graph.ainvoke(input=ReflectionState(original_text="Hello, world!", revised_text="Hello, world!"))

config = GeneratePostConfiguration()
# asyncio.run(main())