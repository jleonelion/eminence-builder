import asyncio
from datetime import datetime
from typing import Literal

from pymongo import MongoClient
from agents.linkedin_upload_post.state import LinkedInUploadPostState
from agents.linkedin_upload_post.configuration import LinkedInUploadPostConfiguration
from agents.utils import load_chat_model
from agents.linkedin_upload_post.utils import *
from langgraph.graph import END, START, StateGraph
from langchain_core.runnables import RunnableConfig
from browser_use.browser.browser import Browser
from browser_use import Agent
import logging

logger = logging.getLogger(__name__)


async def load_document(
    state: LinkedInUploadPostState, config: RunnableConfig
) -> LinkedInUploadPostState:
    """Load the post document from the database."""

    logger.debug("Loading pending posts")
    config = LinkedInUploadPostConfiguration.from_runnable_config(config)
    pending_posts = load_next_pending_post(config)
    if not pending_posts:
        logger.debug("No pending posts found.")
        return state

    return {"post": pending_posts[0]}


async def create_post(
    state: LinkedInUploadPostState, config: RunnableConfig
) -> LinkedInUploadPostState:
    """Create report content."""

    if "post" not in state.post:
        logger.error("The state does not contain a post!")
        raise ValueError("The state does not contain a post!")

    config = LinkedInUploadPostConfiguration.from_runnable_config(config)

    browser = None
    try:
        browser = Browser(config=config.browser_config)
        model = load_chat_model(config.browser_model, config.browser_model_kwargs)
        agent = Agent(
            task=build_browser_instructions_prompt(state, config),
            llm=model,
            browser=browser,
        )
        logger.debug("Launching post upload agent.")
        await agent.run(max_steps=20)
    except Exception as e:
        print(e)
    finally:
        await browser.close() if browser else None

    return state


def route_document_loaded(
    state: LinkedInUploadPostConfiguration, config: RunnableConfig
) -> Literal["create_post", "__end__"]:
    """Route to create_post if document exists in state."""

    if state.post:
        return "create_post"
    else:
        return "__end__"


builder = StateGraph(
    LinkedInUploadPostState, config_schema=LinkedInUploadPostConfiguration
)
builder.add_node(load_document)
builder.add_node(create_post)
builder.add_edge(START, "load_document")
# builder.add_edge("parse_post_request", "verify_links")
builder.add_conditional_edges("load_document", route_document_loaded)
builder.add_edge("create_post", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "LinkedInUploadPost"


# async def main():
#     # Invoke the graph
#     state = LinkedInUploadPostState()
#     result = await graph.ainvoke(
#         input=state
#         # {
#         #     "document": {
#         #         "_id": {"$oid": "679c56387036e34fcd74c31e"},
#         #         "topic": "Collect syslogs in Azure Sentinel",
#         #         "post": "🔒 Collect Syslogs In Azure Sentinel! 🚀\n\nImprove how you monitor your Azure estate:\n\n1. **Improved Security Monitoring:** Syslog collection allows for real-time tracking of security events on Linux VMs, enabling quicker responses to potential threats.\n2. **Centralized Log Management:** Streamline your log data from various sources into a single location for easier analysis and compliance reporting.\n3. **Enhanced Troubleshooting:** Quickly identify and resolve issues by analyzing logs from different systems, reducing downtime and improving system reliability.\n\n**Key Steps to Aggregate Syslogs:**\n- **Install Syslog from ContentHub:** Update your Sentinel workspace to install the Syslog capability from Content Hub\n- **Define Data Collection Rules in Azure Monitor:** Rules can collect everything, but you probably only want server facitlities and log levels.\n- **Add Azure Monitor Agent to your Linux VM:** Set up a Syslog collector on a Linux VM.\n- **Implement Security Measures:** Utilize scripts to optimize performance and enhance security alerting.\n\n💡 How does your organization manage log collection?\n\n#Cybersecurity #LogManagement #Azure #Syslog",
#         #         "scheduled_date": {"$date": "2025-01-31T13:57:00.000Z"},
#         #         "status": "pending",
#         #     }
#         # }
#     )
#     print(result)


# asyncio.run(main())
