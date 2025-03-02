"""This module provides functionality to delete all threads using the LangGraph SDK."""

import asyncio

from langgraph_sdk import get_client


async def delete_all_threads(client):
    """Delete all threads using the provided client.

    Args:
        client: The client instance to interact with the threads.
    """
    # Optional: Add filters if you want to delete specific types of threads
    threads = await client.threads.search(
        limit=100,  # Adjust based on your expected number of threads
        offset=0,
        # Optional: Add metadata or status filters
        # metadata={"your_filter": "value"},
        # status="interrupted"
    )

    deleted_count = 0
    for thread in threads:
        try:
            await client.threads.delete(thread_id=thread["thread_id"])
            deleted_count += 1
            print(f"Deleted thread: {thread['thread_id']}")  # noqa: T201
        except Exception as e:
            print(f"Error deleting thread {thread['thread_id']}: {e}")  # noqa: T201

    print(f"Total threads deleted: {deleted_count}")  # noqa: T201


# Usage
async def main():  # noqa: D103
    # Replace with your actual LangGraph Cloud deployment URL
    client = get_client(url="http://localhost:2024")

    await delete_all_threads(client)


# Run the async function
asyncio.run(main())
