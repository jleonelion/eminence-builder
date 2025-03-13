"""Prompts for the agent."""

from typing import Any

from langchain_core.prompts import SystemMessagePromptTemplate

from agents.blog.configuration import BlogConfiguration
from agents.blog.state import BlogState
from agents.utils import format_docs

RESEARCH_DETAILS = """
Examine the user message to provide details that will focus research activities for a blog page.
"""


def build_research_details_prompt(**kwargs: Any) -> SystemMessagePromptTemplate:
    """Build the research prompt."""
    return SystemMessagePromptTemplate.from_template(RESEARCH_DETAILS)


BLOG_PLANNER = """You are an expert technical writer, helping to plan a fun, engaging, and informative blog post.
Your goal is to generate an outline of the post by defining the general structure and identifying each section of the post.
Do not write the content for any section.

All posts should begin with a TL;DR section that summarizes key content of the entire post.
After the TL;DR section, there are various sections which dive deeper into the topic and represent the majority of the post content.
All posts should end with a conclusion section the concisely reiterates major points and leaves the reader with a call to action.
Section names should engage the reader by being light-hearted and not follow the typical academic tone.

Use this example as inspiration for the post sections:
<examples>
This post was focused on Azure's mandate to enable Multi-Factor Authentication (MFA).

The sections were:
1. TL;DR 
- Description - Attention grabbing summary of actions to take to enable MFA in Azure
- Research - False

2. This is Just the Beginning:
- Description - Overview of the timelines and coming security mandates for Azure
- Research - True

3. What is an Entra tenant:
- Description - Explaination of an Entra tenant and how it relates to MFA
- Research - True

4. Which Kind of Accounts are Impacted?:
- Description - Description of the Entra accounts types being impacted and how they are impacted by the MFA mandate
- Research - True

5. Which Kind of Accounts are Not Impacted?:
- Description - Description of the Entra accounts types being not being impacted
- Research - True

6. But How Do I Address Potential Problems?:
- Description - Identify the different problems that MFA can cause different account types and advice on various tactics to address those problems
- Research - True

7. In Closing:
- Description - Brief reiteration of key points discussed and call to action for the reader.
- Research - True
</examples>


The main topic of the post you are working on is:
<topic>
{topic}
</topic>

Reflect on the information in these reference documents to plan sections of the post:
{context}

Each section should have the following fields:
- Name - Name for this section of the report.
- Description - Brief overview of the main topics and concepts to be covered in this section.
- Research - Whether to perform web research for this section of the report.
- Content - The content of the section.  You will leave this blank.

Consider which sections require web research. For example, TL;DR, introduction, and conclusion sections will not require research because they will distill information from other sections of the post.

Take into account these general instructions when planning sections for the post:
{instructions}

Now, generate the sections of the post.
"""


def build_blog_planner_prompt(state: BlogState, config: BlogConfiguration) -> str:
    """Build the prompt."""
    topic = state.blog_request.main_topic
    content = format_docs(state.reference_content)
    instructions = state.blog_request.message
    return BLOG_PLANNER.format(topic=topic, context=content, instructions=instructions)
