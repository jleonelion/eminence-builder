from langchain import hub

"""Default prompts."""

# fetch from langsmith
ROUTER_SYSTEM_PROMPT = (
    hub.pull(
        "langchain-ai/chat-langchain-router-prompt").messages[0].prompt.template
)
GENERATE_QUERIES_SYSTEM_PROMPT = (
    hub.pull("generate-queries").messages[0].prompt.template
)
MORE_INFO_SYSTEM_PROMPT = (
    hub.pull(
        "langchain-ai/chat-langchain-more-info-prompt").messages[0].prompt.template
)
RESEARCH_PLAN_SYSTEM_PROMPT = (
    hub.pull("research-planner").messages[0].prompt.template
)
GENERAL_SYSTEM_PROMPT = (
    hub.pull(
        "langchain-ai/chat-langchain-general-prompt").messages[0].prompt.template
)
BLOGGER_SYSTEM_PROMPT = (
    hub.pull("blog-writer").messages[0].prompt.template
)
