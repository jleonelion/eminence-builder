from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    # A synchronous browser is available, though it isn't compatible with jupyter.\n",      },
    create_sync_playwright_browser,
)
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-tools-agent")


sync_browser = create_sync_playwright_browser()
toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
tools = toolkit.get_tools()

# Choose the LLM that will drive the agent
# Only certain models support this
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Construct the OpenAI Tools agent
agent = create_openai_tools_agent(llm, tools, prompt)


# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

command = {
    "input": "Go to https://www.hackernews.com/ and give the url of the article with the most comments"
}
agent_executor.invoke(command)
