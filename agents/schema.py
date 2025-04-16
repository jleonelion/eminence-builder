"""Defines the schema by various agents."""

from typing import Literal, Optional, TypedDict, Union


class HumanInterruptConfig(TypedDict):
    """Configuration for human interrupt actions."""

    allow_ignore: bool
    allow_respond: bool
    allow_edit: bool
    allow_accept: bool


class ActionRequest(TypedDict):
    """Represents a request for an action with its arguments."""

    action: str
    args: dict


class HumanInterrupt(TypedDict):
    """Represents a human interrupt with its configuration and description."""

    action_request: ActionRequest
    config: HumanInterruptConfig
    description: Optional[str]


class HumanResponse(TypedDict):
    """Represents a human response with its type and arguments."""

    type: Literal["accept", "ignore", "response", "edit"]
    args: Union[None, str, ActionRequest]
