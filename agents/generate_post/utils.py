from datetime import datetime, timedelta
import pytz
import re

from agents.generate_post.configuration import GeneratePostConfiguration
from agents.generate_post.state import GeneratePostState
from agents.prompts import *
from agents.utils import *

# TODO: Implement the following functions
async def get_reflections_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get reflections on the generated post."""
    return ""

def get_examples(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get post examples."""
    return POST_EXAMPLES

def get_structure_instructions(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get post structure instructions."""
    return POST_STRUCTURE_INSTRUCTIONS

def get_content_rules(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    return POST_CONTENT_RULES

def build_post_system_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Build the system prompt for generating a post."""
    return POST_SYSTEM_PROMPT.format(
            examples=get_examples(state, config),
            structure_instructions=get_structure_instructions(state, config),
            content_rules=get_content_rules(state, config),
            reflections_prompt=get_reflections_prompt(state, config)
    )

def build_condense_post_system_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration, original_post_length: int
) -> str:
    """Build the system prompt for generating a post."""
    return CONDENSE_POST_PROMPT.format(
            report=state.report,
            link="\n".join(state.relevant_links), # Concatenate multiple links with newline
            structure_instructions=get_structure_instructions(state, config),
            content_rules=get_content_rules(state, config),
            reflections_prompt=get_reflections_prompt(state, config),
            original_post_length=original_post_length,
            max_post_length=config.max_post_length
    )

def build_report_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Format report of information used to generate a post."""
    return """
Here is the report I wrote on the content I'd like posted to LinkedIn:
<report>
{report}
</report>

And here is the link to the content I'd like promoted:
<link>
{link}
</link>
    """.format(report=state.report, link=state.relevant_links[0])

def build_report_system_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get the system prompt for generating a post."""
    return REPORT_SYSTEM_PROMPT.format(
        content_rules=get_report_content_rules(state, config),
        structure_guidelines=get_report_structure_guidelines(state, config)
    )

def get_report_content_rules(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    return REPORT_CONTENT_RULES

def get_report_structure_guidelines(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    return REPORT_STRUCTURE_GUIDELINES

def build_report_content_prompt(
    state: GeneratePostState, config: GeneratePostConfiguration
) -> str:
    """Get content rules."""
    return """
The following text contains summaries, or entire pages from the content I submitted to you. Please review the content and generate a report on it.
{content}
    """.format(content=format_docs(state.page_contents))

def get_next_saturday() -> datetime:
    """Calculate the next Saturday in Pacific Time Zone."""
    pacific = pytz.timezone('America/Los_Angeles')
    now = datetime.now(pacific)
    
    # Calculate the number of days until the next Saturday
    days_until_saturday = (5 - now.weekday() + 7) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    
    # Calculate the next Saturday date
    next_saturday_date = now + timedelta(days=days_until_saturday)
    next_saturday_date = next_saturday_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return next_saturday_date

def parse_post(input_string: str) -> str:
    """Extract contents between <post> tags from the input string."""
    match = re.search(r'<post>(.*?)</post>', input_string, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # TODO: log warning
        return input_string
        
def parse_report(input_string: str) -> str:
    """Extract contents between <report> tags from the input string."""
    match = re.search(r'<report>(.*?)</report>', input_string, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # TODO: log warning
        return input_string

def remove_urls(input_string: str) -> str:
    """Remove all URLs and multi-spaces from the input string."""
    return re.sub(r'\s+', ' ', re.sub(r'http[s]?://\S+', '', input_string)).strip()
    
