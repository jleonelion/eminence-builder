import asyncio  # noqa: D100
import logging
import os
import sys
from pathlib import Path

import anyio
from browser_use import Agent, Controller
from browser_use.agent.views import ActionResult
from browser_use.browser import BrowserProfile, BrowserSession
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


load_dotenv()

logger = logging.getLogger(__name__)

# Initialize browser and controller
browser_profile = BrowserProfile(
    headless=False,
    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)
controller = Controller()


@controller.action(
    "Upload file to interactive element with file path ",
)
async def upload_file(  # noqa: D103
    index: int,
    path: str,
    browser_session: BrowserSession,
    available_file_paths: list[str],
):
    if path not in available_file_paths:
        return ActionResult(error=f"File path {path} is not available")

    if not os.path.exists(path):
        return ActionResult(error=f"File {path} does not exist")

    dom_el = await browser_session.get_dom_element_by_index(index)

    file_upload_dom_el = dom_el.get_file_upload_element()

    if file_upload_dom_el is None:
        msg = f"No file upload element found at index {index}"
        logger.info(msg)
        return ActionResult(error=msg)

    file_upload_el = await browser_session.get_locate_element(file_upload_dom_el)

    if file_upload_el is None:
        msg = f"No file upload element found at index {index}"
        logger.info(msg)
        return ActionResult(error=msg)

    try:
        await file_upload_el.set_input_files(path)
        msg = f"Successfully uploaded file to index {index}"
        logger.info(msg)
        return ActionResult(extracted_content=msg, include_in_memory=True)
    except Exception as e:
        msg = f"Failed to upload file to index {index}: {str(e)}"
        logger.info(msg)
        return ActionResult(error=msg)


@controller.action("Read the file content of a file given a path")
async def read_file(path: str, available_file_paths: list[str]):  # noqa: D103
    if path not in available_file_paths:
        return ActionResult(error=f"File path {path} is not available")

    async with await anyio.open_file(path, "r") as f:
        content = await f.read()
    msg = f"File content: {content}"
    logger.info(msg)
    return ActionResult(extracted_content=msg, include_in_memory=True)


def create_file(file_type: str = "txt"):  # noqa: D103
    with open(f"tmp.{file_type}", "w") as f:
        f.write("test")
    file_path = Path.cwd() / f"tmp.{file_type}"
    logger.info(f"Created file: {file_path}")
    return str(file_path)


def create_model(fully_specified_name: str = "ollama/qwen3:8b"):
    """Create a chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = ""
        model = fully_specified_name

    model_kwargs = {"temperature": 0}

    return init_chat_model(model, model_provider=provider, model_kwargs=model_kwargs)


llm = create_model("openai/gpt-4o")
# llm = create_model()


async def upload_task():  # noqa: D103
    # This sort of works
    # task = 'Go to kayak.com and find the cheapest one-way flight from Zurich to San Francisco in 3 weeks.'
    # this does not work
    task = "Go to https://kzmpmkh2zfk1ojnpxfn1.lite.vusercontent.net/ and - read the file content and upload them to fields"
    available_file_paths = [create_file("txt"), create_file("pdf"), create_file("csv")]

    browser_session = BrowserSession(browser_profile=browser_profile)
    await browser_session.start()
    agent = Agent(
        task=task,
        llm=llm,
        controller=controller,
        browser_session=browser_session,
        available_file_paths=available_file_paths,
    )

    await agent.run()

    await browser_session.stop()

    input("Press Enter to close...")

    await agent.run()


async def simple_task():  # noqa: D103
    task = "Go to kayak.com and find the cheapest one-way flight from Zurich to San Francisco in 3 weeks."

    agent = Agent(
        task=task,
        llm=llm,
    )

    await agent.run()


if __name__ == "__main__":
    asyncio.run(simple_task())
