"""Utility functions for generating posts."""

import logging
import re
import threading
from datetime import datetime, timedelta
from typing import Any, cast

import aiohttp
import pytz
from langgraph.store.base import BaseStore

from agents.find_images.utils import BLACKLISTED_MIME_TYPES
from agents.generate_post.configuration import GeneratePostConfiguration
from agents.generate_post.state import GeneratePostState, PostDate
from agents.prompts import (
    CONDENSE_POST_PROMPT,
    NEWS_POST_CONTENT_RULES,
    NEWS_POST_EXAMPLES,
    NEWS_POST_STRUCTURE_INSTRUCTIONS,
    PARSE_POST_REQUEST_PROMPT,
    POST_CONTENT_RULES,
    POST_EXAMPLES,
    POST_STRUCTURE_INSTRUCTIONS,
    REFLECTIONS_PROMPT,
    REPORT_CONTENT_RULES,
    REPORT_STRUCTURE_GUIDELINES,
    REPORT_SYSTEM_PROMPT_DEFAULT,
    REPORT_SYSTEM_PROMPT_NEWS,
    REWRITE_POST_PROMPT,
    WRITE_POST_SYSTEM_PROMPT,
)
from agents.reflection.graph import graph as reflection_graph
from agents.reflection.state import ReflectionState
from agents.utils import fetch_rules, format_docs, is_valid_url

logger = logging.getLogger(__name__)


async def build_reflections_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration, store: BaseStore
) -> str:
    """Get reflections on the generated post."""
    rules = await fetch_rules(config=config, post_style=state.style)
    if not rules:
        # return empty string if no reflection rules in store
        return ""

    # convert relfections to string with - before each rule
    reflections_string = "\n- ".join(rules)
    return REFLECTIONS_PROMPT.format(reflections=reflections_string)


async def build_rewrite_post_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration, store: BaseStore
) -> str:
    """Get reflections on the generated post."""
    return REWRITE_POST_PROMPT.format(
        reflections_prompt=await build_reflections_prompt(state, config, store),
        original_post=state.post,
    )


examples_by_style = {
    "default": POST_EXAMPLES,
    "news": NEWS_POST_EXAMPLES,
}


def get_examples(state: GeneratePostState, config: GeneratePostConfiguration) -> str:
    """Get post examples."""
    if state.style in examples_by_style:
        return examples_by_style[state.style]
    else:
        return POST_EXAMPLES


instructions_by_style = {
    "default": POST_STRUCTURE_INSTRUCTIONS,
    "news": NEWS_POST_STRUCTURE_INSTRUCTIONS,
}


def get_structure_instructions(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get post structure instructions."""
    if state.style in instructions_by_style:
        if state.style == "news":
            return instructions_by_style[state.style].format(
                commentary=state.commentary
            )
    else:
        return POST_STRUCTURE_INSTRUCTIONS


content_rules_by_style = {
    "default": POST_CONTENT_RULES,
    "news": NEWS_POST_CONTENT_RULES,
}


def get_content_rules(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    if state.style in content_rules_by_style:
        return content_rules_by_style[state.style]
    else:
        return POST_CONTENT_RULES


def build_post_system_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration, store: BaseStore
) -> str:
    """Build the system prompt for generating a post."""
    return WRITE_POST_SYSTEM_PROMPT.format(
        examples=get_examples(state, config),
        structure_instructions=get_structure_instructions(state, config),
        content_rules=get_content_rules(state, config),
        reflections_prompt=build_reflections_prompt(state, config, store),
    )


def build_condense_post_system_prompt(
    state: GeneratePostState,
    config: GeneratePostConfiguration,
    store: BaseStore,
    original_post_length: int,
) -> str:
    """Build the system prompt for generating a post."""
    return CONDENSE_POST_PROMPT.format(
        report=state.report,
        structure_instructions=get_structure_instructions(state, config),
        content_rules=get_content_rules(state, config),
        reflections_prompt=build_reflections_prompt(state, config, store),
        original_post_length=original_post_length,
        max_post_length=config.max_post_length,
    )


def build_report_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Format report of information used to generate a post."""
    return f"""
Here is the report I wrote on the content I'd like posted to LinkedIn:
<report>
{state.report}
</report>

And here is the link to the reference content:
<link>
{state.relevant_links[0]}
</link>
    """


def build_report_system_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get the system prompt for generating a post."""
    if state.style == "news":
        return REPORT_SYSTEM_PROMPT_NEWS
    else:
        return REPORT_SYSTEM_PROMPT_DEFAULT.format(
            content_rules=get_report_content_rules(state, config),
            structure_guidelines=get_report_structure_guidelines(state, config),
        )


def get_report_content_rules(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    return REPORT_CONTENT_RULES


def get_parse_post_request_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get parse request prompt."""
    return PARSE_POST_REQUEST_PROMPT


def get_report_structure_guidelines(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    return REPORT_STRUCTURE_GUIDELINES


def get_unknown_response_desc(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get unknown response."""
    if state.next == "unkown_response" and state.user_response:
        return f"""# <div style="color: red;">UNKNOWN/INVALID RESPONSE RECEIVED: '${state.user_response}'</div>

<div style="color: red;">Please respond with either a request to update/rewrite the post, or a valid priority level or a date to schedule the post.</div>

<div style="color: red;">See the `Schedule Date`, or `Instructions` sections for more information.</div>

<hr />"""
    return ""


def get_interupt_desc_template(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Generate a template string for an interrupt description used in scheduling posts for Twitter/LinkedIn.

    Args:
        state (GeneratePostState): The current state of the post generation process.
        config (GeneratePostConfiguration): Configuration settings for generating the post.

    Returns:
        str: A formatted string containing the interrupt description template.
    """
    return """{unknow_response_desc}
# Schedule post
  
Using these URL(s), a post was generated for Twitter/LinkedIn:
### Relevant URLs:
${relavant_links}

Original URL: ${original_link}

### Post:
```
{post}
```

{image_options_text}

## Instructions

There are a few different actions which can be taken:\n
- **Edit**: If the post is edited and submitted, it will be scheduled for Twitter/LinkedIn.
- **Response**: If a response is sent, it will be sent to a router which can be routed to either
  1. A node which will be used to rewrite the post. Please note, the response will be used as the 'user' message in an LLM call to rewrite the post, so ensure your response is properly formatted.
  2. A node which will be used to update the scheduled date for the post.
  If an unknown/invalid response is sent, nothing will happen, and it will be routed back to the human node.
- **Accept**: If 'accept' is selected, the post will be scheduled for Twitter/LinkedIn.
- **Ignore**: If 'ignore' is selected, this post will not be scheduled, and the thread will end.

## Additional Instructions

### Schedule Date

The date the post will be scheduled for may be edited, but it must follow the format 'MM/dd/yyyy hh:mm a z'. Example: '12/25/2024 10:00 AM PST', _OR_ you can use a priority level:
- **P1**: Saturday/Sunday between 8:00 AM and 10:00 AM PST.
- **P2**: Friday/Monday between 8:00 AM and 10:00 AM PST _OR_ Saturday/Sunday between 11:30 AM and 1:00 PM PST.
- **P3**: Saturday/Sunday between 1:00 PM and 5:00 PM PST.

### Image

{image_instruction}

## Report

Here is the report that was generated for the posts:
{report}
"""


def build_interrupt_desc(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Build interrupt description."""
    image_options_text = ""
    image_instructions = (
        "Text only mode enabled. Image support has been disabled.\n"
        if config.text_only_mode
        else "No image options available."
    )
    if not config.text_only_mode:
        if len(state.image_options) > 0:
            image_list = "\n".join(
                [
                    f"URL: {url}\nImage: <details><summary>Click to view image</summary>\n\n![](${url})\n</details>\n"
                    for url in state.image_options
                ]
            )
            image_options_text = f"""
            ## Image Options
            The following image options are available. Select one by copying and pasting the URL into the 'image' field.
            {image_list}
            """
            image_instructions = """
            If you wish to attach an image to the post, please add a public image URL.
        
            You may remove the image by setting the 'image' field to 'remove', or by removing all text from the field
            To replace the image, simply add a new public image URL to the field.
            MIME types will be automatically extracted from the image.
        
            Supported image types: `image/jpeg` | `image/gif` | `image/png` | `image/webp`
            """
        else:
            image_instructions = "No image options available."
    else:
        image_instructions = (
            "Text only mode enabled. Image support has been disabled.\n"
        )

    return get_interupt_desc_template(state, config).format(
        unknow_response_desc=get_unknown_response_desc(state, config),
        relavant_links="\n- ".join(state.relevant_links),
        original_link=state.links[0],
        post=state.post,
        image_options_text=image_options_text,
        image_instruction=image_instructions,
        report=state.report,
    )


def build_default_date(state, config):
    """Build default date for scheduling post."""
    # may be more elequant way to do type conversion
    default_date = state.schedule_date or get_next_saturday()
    default_date_string = ""
    if default_date == "p1" or default_date == "p2" or default_date == "p3":
        default_date_string = default_date
    else:
        timezone = pytz.timezone(config.timezone)
        default_date = default_date.astimezone(timezone)
        default_date_string = default_date.strftime("%m/%d/%Y %I:%M %p %Z")
    return default_date_string


def parse_date(string: str) -> PostDate:
    """Build default date for scheduling post."""
    # convert string to lowercase and remove leading/trailing whitespace
    cleaned_string = string.strip().lower()

    if cleaned_string in ["p1", "p2", "p3"]:
        # return cast cleaned_string cast as PostDate object
        return cast(PostDate, cleaned_string)

    # if string is a valid date, return the date
    try:
        return datetime.strptime(cleaned_string, "%m/%d/%Y %I:%M %p %Z")
    except ValueError:
        # not valid date
        return None


def build_report_content_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    return f"""
The following text contains summaries, or entire pages from the content I submitted to you. Please review the content and generate a report on it.
{format_docs(state.page_contents)}
    """


def get_next_saturday() -> datetime:
    """Calculate the next Saturday in Pacific Time Zone."""
    pacific = pytz.timezone("America/Los_Angeles")
    now = datetime.now(pacific)

    # Calculate the number of days until the next Saturday
    days_until_saturday = (5 - now.weekday() + 7) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7

    # Calculate the next Saturday date
    next_saturday_date = now + timedelta(days=days_until_saturday)
    next_saturday_date = next_saturday_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    return next_saturday_date


def parse_post(input_string: str) -> str:
    """Extract contents between <post> tags from the input string."""
    match = re.search(r"<post>(.*?)</post>", input_string, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # TODO: log warning
        return input_string


def parse_report(input_string: str) -> str:
    """Extract contents between <report> tags from the input string."""
    match = re.search(r"<report>(.*?)</report>", input_string, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # TODO: log warning
        return input_string


def remove_urls(input_string: str) -> str:
    """Remove all URLs and multi-spaces from the input string."""
    return re.sub(r"\s+", " ", re.sub(r"http[s]?://\S+", "", input_string)).strip()


def calc_scheduled_date(scheduled: PostDate) -> datetime:
    """Calculate the scheduled date."""
    # TODO review how p1-3 are converted to datetime
    if scheduled == "p1":
        return get_next_saturday().replace(hour=8, minute=0)
    elif scheduled == "p2":
        return get_next_saturday().replace(hour=8, minute=0)
    elif scheduled == "p3":
        return get_next_saturday().replace(hour=13, minute=0)
    else:
        return scheduled


async def process_image_input(input: str) -> dict:
    """Process image input."""
    if input and input.lower() == "remove":
        return "remove"
    if is_valid_url(input):
        content_type = await determine_content_type(input)
        # if image type is blacklisted, then don't return it
        if any(
            content_type.startswith(blacklisted)
            for blacklisted in BLACKLISTED_MIME_TYPES
        ):
            return None
        else:
            return {
                "image_url": input,
                "mime_type": content_type,
            }
    else:
        return None


async def image_url_to_buffer(url: str) -> dict[str, Any]:
    """Convert image URL to buffer."""
    if not is_valid_url(url=url):
        raise Exception("Invalid image URL provided")

    response = await aiohttp.ClientSession().get(url=url)
    response.raise_for_status()
    buffer = await response.read()
    content_type = response.headers.get("Content-Type", "image/jpeg")

    return {"buffer": buffer, "content_type": content_type}


async def determine_content_type(url: str) -> str:
    """Determine content type."""
    if not is_valid_url(url=url):
        raise Exception("Invalid image URL provided")

    response = await aiohttp.ClientSession().get(url=url)
    response.raise_for_status()
    await response.read()
    content_type = response.headers.get("Content-Type", "image/jpeg")

    return content_type


def spawn_reflection_graph(state: ReflectionState, config: GeneratePostConfiguration):
    """Spawn a reflection graph."""
    if not config.langgraph_url:
        raise ValueError("No langgraph_url found.")

    if not config.reflection_graph_name:
        logger.warning("Skipping reflections because no reflection graph name found.")
        return

    def invoke_reflection_graph(state: ReflectionState):
        reflection_graph.invoke(state)

    # remote_graph = RemoteGraph(config.reflection_graph_name, url=config.langgraph_url)
    # asyncio.create_task(remote_graph.invoke(input=state))
    thread = threading.Thread(target=invoke_reflection_graph, args=(state,))
    thread.start()
