import operator
from typing import Annotated, Optional, Literal, Union, cast
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore, Item

class State(TypedDict):
    # The operator.add reducer function makes this append-only
    aggregate: Optional[Annotated[list, operator.add]] = None
    post: str = ""

class HumanInterruptConfig(TypedDict):
    allow_ignore: bool
    allow_respond: bool
    allow_edit: bool
    allow_accept: bool

class ActionRequest(TypedDict):
    action: str
    args: dict

class HumanInterrupt(TypedDict):
    action_request: ActionRequest
    config: HumanInterruptConfig
    description: Optional[str]

class HumanResponse(TypedDict):
    type: Literal['accept', 'ignore', 'response', 'edit']
    args: Union[None, str, ActionRequest]

async def human_review(state: State, *, config: RunnableConfig, store: BaseStore):
    """Invoke human-in-the-loop for post content."""

    ruleset = await store.aget(("reflection_rules", "rules"), key="ruleset")

    if not ruleset:
        await store.aput(("reflection_rules", "rules"), key="ruleset", value=["a simple reflection rule", "a more complex reflection rule"])

    ruleset = await store.aget(("reflection_rules", "rules"), key="ruleset")

    request = HumanInterrupt = {
        "action_request": {
            "action": "Schedule LinkedIn posts",
            "args": {
                "post": "post",
                "default_date": "date",
            },
            "config": {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": True,
                "allow_accept": True
            },
            "description": "a description"
        }
    }
    response = interrupt([request])
    response = response[0] if isinstance(response, list) else response
    response = cast(HumanResponse, response)
    print(response['type'])

builder = StateGraph(State)
builder.add_node(human_review)

# Create edges for parallel execution
builder.add_edge(START, "human_review")
builder.add_edge("human_review", END)

# Compile the graph
graph = builder.compile()
