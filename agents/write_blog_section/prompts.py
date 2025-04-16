"""Prompts for the agent."""

from langchain_core.messages import HumanMessage

from agents.blog.schema import Section
from agents.utils import format_docs
from agents.write_blog_section.configuration import BlogWriteSectionConfiguration
from agents.write_blog_section.state import BlogWriteSectionState

SECTION_WRITER_SYSTEM_PROMPT = """You are an expert technical writer crafting one section of a technical blog post.

Guidelines for writing:

1. Technical Accuracy:
- Include specific version numbers
- Reference concrete metrics/benchmarks
- Cite official documentation
- Use technical terminology precisely

2. Length and Style:
- Strict word limit of {word_limit}
- No marketing language
- Technical focus
- Write in simple, clear language
- Start with your most important insight in **bold**
- Use short paragraphs (4-5 sentences max)

3. Structure:
- Use ## for section title (Markdown format)
- Only use ONE structural element IF it helps clarify your point:
  * Either a focused table comparing 2-3 key items (using Markdown table syntax)
  * Or a short list (3-5 items) using proper Markdown list syntax:
    - Use `*` or `-` for unordered lists
    - Use `1.` for ordered lists
    - Ensure proper indentation and spacing
- End with ### Sources that references the below source material formatted as:
  * List each source with title, date, and URL
  * Format: `- Title : URL`

3. Writing Approach:
- Include at least one specific example or case study
- Use concrete details over general statements
- Make every word count
- No preamble prior to creating the section content
- Focus on your single most important point

4. Reference Material:
- Use information in the provided documents to help write the section.  
- If you want more information, use tools to review source and citation links from the provided documents.
- If you still need more information, search the web.  Only search the web after your've reviewed the documents and the citation links, and concluded they are inadequate.
- If you do search the web, limit your web searches to {search_limit}

5. Quality Checks:
- Less than {word_limit} words (excluding title and sources)
- Careful use of only ONE structural element (table or list) and only if it helps clarify your point
- One specific example / case study
- Starts with bold insight
- No preamble prior to creating the section content
- Sources cited at end
"""


def build_section_writer_system_prompt(
    state: BlogWriteSectionState, config: BlogWriteSectionConfiguration
) -> str:
    """Build the prompt."""
    word_limit = state.word_limit
    search_limit = state.search_limit
    return SECTION_WRITER_SYSTEM_PROMPT.format(
        word_limit=word_limit, search_limit=search_limit
    )


SECTION_WRITER_MESSAGE = """
Write about: {section_topic}
Using the following documents as reference context:
{documents}
"""


def build_section_writer_message(
    state: BlogWriteSectionState, config: BlogWriteSectionConfiguration
) -> HumanMessage:
    """Build the prompt."""
    section_topic = (
        state.section.description
        if isinstance(state.section, Section)
        else state.section["description"]
    )
    documents = format_docs(state.reference_content)
    return HumanMessage(
        content=SECTION_WRITER_MESSAGE.format(
            section_topic=section_topic, documents=documents
        )
    )
