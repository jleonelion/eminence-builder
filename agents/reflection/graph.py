import asyncio
import logging
from typing import Literal

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.store.base import BaseStore
from pydantic import BaseModel, Field

from agents.reflection.configuration import ReflectionConfiguration
from agents.reflection.state import ReflectionState
from agents.reflection.utils import *
from agents.utils import fetch_rules, load_chat_model, store_rules

logger = logging.getLogger(__name__)


# Define a Pydantic schema for tool inputs
class NewRuleSchema(BaseModel):
    """Input schema for new rule tool"""

    new_rule: str = Field(description="A new rule to create")


class UpdatedRulesetSchema(BaseModel):
    """Input schema for update ruleset tool"""

    updated_ruleset: list[str] = Field(description="The updated ruleset to store")


# Create a tool using the @tool decorator with a specific schema
@tool(args_schema=NewRuleSchema)
def new_rule(rule: str) -> None:
    """Placeholder to create a new rule"""
    # intentionally does nothing
    pass


def identify_new_rules(
    state: ReflectionState, config: RunnableConfig
) -> ReflectionState:
    """Reflect on changes made to the text and determine if additional writing rules should be created."""

    if not state.original_text:
        raise ValueError("No original text found.")
    if not state.revised_text:
        raise ValueError("No revised text found.")
    
    if state.original_text == state.revised_text:
        logger.info("Skipping analysis.  Original text and revised text match")
        return {
            "new_rules": [],
        }

    config = ReflectionConfiguration.from_runnable_config(config)
    model = load_chat_model(config.reflection_model, config.reflection_model_kwargs)
    model = model.bind_tools([new_rule])
    reflection_prompt = asyncio.run(build_reflection_prompt(state, config))

    response = model.invoke(
        [
            SystemMessage(reflection_prompt),
        ]
    )
    new_rules = []
    if response.tool_calls:
        logger.debug(f"Tool calls: {response.tool_calls}")
        for tool_call in response.tool_calls:
            if tool_call["name"] == "new_rule":
                logger.debug(f"new_rule tool was called with args: {tool_call['args']}")
                for arg_name, arg_value in tool_call["args"].items():
                    if arg_name == "new_rule":
                        new_rules.append(arg_value)
                    else:
                        logger.warning(f"Unknown arg to new_rule tool: {arg_name}")
            else:
                logger.warning(f"Unknown tool call: {tool_call}")
    else:
        logger.info("No tool calls were made, so no new rule to create")

    return {
        "new_rules": new_rules,
    }

def update_ruleset(
    state: ReflectionState, config: RunnableConfig,
) -> ReflectionState:
    """Revise ruleset to incorporate new rules."""

    if not state.new_rules:
        raise ValueError("No new_rules found.")
    
    config = ReflectionConfiguration.from_runnable_config(config)
    existing_rules = asyncio.run(fetch_rules(config=config, post_style=state.post_style))
    if existing_rules:
        # determine how existing rules should be updated to account for new rules
        model = load_chat_model(config.reflection_model, config.reflection_model_kwargs).with_structured_output(UpdatedRulesetSchema)
        update_rules_prompt = asyncio.run(build_update_rules_prompt(existing_rules=existing_rules, new_rules=state.new_rules))
        response = model.invoke(
            [
                SystemMessage(update_rules_prompt),
            ]
        )
        updated_rules = response.updated_ruleset
    else:
        updated_rules = state.new_rules    
    
    asyncio.run(store_rules(config=config, rules=updated_rules, post_style=state.post_style))
    # test out retrieving the ruleset
    return state


def route_update_ruleset(
    state: ReflectionState, config: RunnableConfig
) -> Literal["update_ruleset", "__end__"]:
    """Route to update_ruleset if new_rules exist in state."""

    if state.new_rules:
        return "update_ruleset"
    else:
        return "__end__"


# Define the graph
builder = StateGraph(
    state_schema=ReflectionState, config_schema=ReflectionConfiguration
)
builder.add_node(identify_new_rules)
builder.add_node(update_ruleset)
builder.add_edge(START, "identify_new_rules")
builder.add_conditional_edges("identify_new_rules", route_update_ruleset)
builder.add_edge("update_ruleset", END)

# Compile into a graph object that you can invoke and deploy.
graph = builder.compile()
graph.name = "Reflect on Editor Changes Graph"
