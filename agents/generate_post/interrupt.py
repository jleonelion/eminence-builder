from typing import Protocol, TypedDict, Literal, Optional, Union
from dataclasses import dataclass

from langchain_core.messages import HumanMessage

from agents.generate_post.configuration import GeneratePostConfiguration
from agents.generate_post.state import GeneratePostState
from agents.prompts import ROUTE_RESPONSE_PROMPT
from agents.utils import load_chat_model

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

class RouteResponseArgs(TypedDict):
    post: str
    date_or_priority: str
    user_response: str

@dataclass(kw_only=True)
class RouteDecision:
    route: Literal["rewrite_post", "update_date", "unknown_response"]


def build_route_content_prompt(
    config: GeneratePostConfiguration, post: str, date_or_priority: str, user_response: str
) -> str:
    return ROUTE_RESPONSE_PROMPT.format(
        post=post,
        date_or_priority=date_or_priority,
        user_response=user_response,
    )

async def determine_next_node(
    post: str,
    date_or_priority: str,
    user_response: str,
    config: GeneratePostConfiguration,
) -> RouteResponseArgs:
    model = load_chat_model(config.route_model)
    model = model.with_structured_output(RouteDecision)
    prompt = build_route_content_prompt(config, post, date_or_priority, user_response)
    # not sure if this should be a system message instead
    result = await model.ainvoke([HumanMessage(content=prompt)])
    return result

# class CustomInterruptHandler(BaseCallbackHandler):
#     def __init__(self, validation_func=None, logger=None):
#         """
#         Initialize a custom interrupt handler
        
#         Args:
#             validation_func (callable, optional): A function to validate interrupt inputs
#             logger (callable, optional): A logging function for tracking interrupts
#         """
#         self.validation_func = validation_func or (lambda x: True)
#         self.logger = logger or print

#     def on_custom_event(
#         self,
#         name: str,
#         data: Any,
#         *,
#         run_id: UUID,
#         tags: Optional[List[str]] = None,
#         metadata: Optional[Dict[str, Any]] = None,
#         **kwargs: Any,
#     ) -> None:
#         """
#         Handle custom interrupt events
        
#         Args:
#             name (str): Name of the event
#             data (Any): Data associated with the interrupt
#             run_id (UUID): Unique identifier for the run
#             tags (List[str], optional): Tags associated with the event
#             metadata (Dict[str, Any], optional): Additional metadata
#         """
#         if name == "interrupt":
#             self.logger(f"Interrupt triggered: {data}")
            
#             # Optional: Perform custom validation
#             if not self.validation_func(data):
#                 self.logger("Interrupt validation failed")
#                 # You could raise an exception or take alternative action
#                 return

