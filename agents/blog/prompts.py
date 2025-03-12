"""Prompts for the agent."""

from typing import Any

from langchain_core.prompts import SystemMessagePromptTemplate

RESEARCH_DETAILS = """
Examine the user message to provide details that will focus research activities for a blog page.
"""


def build_research_details_prompt(**kwargs: Any) -> SystemMessagePromptTemplate:
    """Build the research prompt."""
    return SystemMessagePromptTemplate.from_template(RESEARCH_DETAILS)


BLOG_PLANNER = """You are an expert technical writer, helping to plan a blog post.

The overall topic of the post is:
<topic>
{topic}
</topic>

Your goal is to generate an outline of the post sections, but you do not need to write the content for each section.

All posts should begin with a TL;DR section that summarizes key content of the entire post.
After the TL;DR section, there must be and introduction section and all posts should end with a conclusion section.

Reflect on the information in these documents to plan other sections of the post:
{context}

Now, generate the sections of the post. Each section should have the following fields:
- Name - Name for this section of the report.
- Description - Brief overview of the main topics and concepts to be covered in this section.
- Research - Whether to perform web research for this section of the report.
- Content - The content of the section.  You will leave blank for now; the sections will be written later.

Consider which sections require web research. For example, TL;DR, introduction, and conclusion sections will not require research because they will distill information from other sections of the post.

Be sure to take into account these general instructions for the post when planning the sections, but use your own judgment to determine the best structure for the post:
{instructions}
"""
