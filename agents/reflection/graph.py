from os import path
from typing import Literal
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from agents.reflection.state import ReflectionState
from agents.reflection.configuration import ReflectionConfiguration
from agents.utils import get_link_type, load_chat_model
from agents.find_images.utils import *
from agents.utils import is_valid_url
from langchain_core.documents import Document


# Define the graph
builder = StateGraph(state_schema=ReflectionState, config_schema=ReflectionConfiguration)
# builder.add_node(find_images)
# builder.add_node(validate_images)
# builder.add_node(rerank_images)
# builder.add_edge(START, "find_images")
# builder.add_conditional_edges("find_images", route_validate_images)
# builder.add_edge("validate_images", "rerank_images")
# builder.add_edge("rerank_images", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "Reflect on Text Changes Graph"
