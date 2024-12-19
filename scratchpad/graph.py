import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt

# Define the state structure


class State(TypedDict):
    # The operator.add reducer function makes this append-only
    aggregate: Annotated[list, operator.add]
    post: str = ""

# Define a node that returns a value


class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: State) -> Any:
        print(f"Adding {self._value} to {state['aggregate']}")
        return {"aggregate": [self._value]}

# Define a human review node


def draft_post(state: State) -> Command:
    # Merge values in state.aggregate into a single string
    merged_values = " ".join(state["aggregate"])
    print(f"Merged values: {merged_values}")

    return {"post": merged_values}


def human_review(state: State) -> Command:
    # Create a message for the user to review
    review_message = f"Review the results: {state['post']}. Do you approve?"
    user_input = interrupt(review_message)  # Wait for user input
    return {"review_message": user_input}


# Build the graph
builder = StateGraph(State)
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_edge(START, "a")
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))
builder.add_node("review", human_review)
builder.add_node("draft", draft_post)

# Create edges for parallel execution
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "draft")
builder.add_edge("c", "draft")
builder.add_edge("draft", "review")
builder.add_edge("review", "d")
builder.add_edge("d", END)

# Compile the graph
graph = builder.compile()

# # Invoke the graph
# result = graph.invoke({"aggregate": []})
# print(result)
