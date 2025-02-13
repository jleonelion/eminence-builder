import os
import logging
import logging.config
import json
import httpx
import asyncio
from bson import json_util
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from agents.linkedin_upload_post.configuration import LinkedInUploadPostConfiguration
from agents.linkedin_upload_post.utils import *
from agents.linkedin_upload_post.state import LinkedInUploadPostState
from agents.linkedin_upload_post.graph import graph

# Load logging configuration from file
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "logging.conf")
logging.config.fileConfig(config_file_path)
logger = logging.getLogger(__name__)
logger.info(f"Logging setup complete")

HOST = "127.0.0.1"
PORT = 8000
SELF_URL = f"http://{HOST}:{PORT}"
TIMEOUT_SECONDS = 5 * 60.0 # 5 minutes
INTERVAL_MINUTES = 60 # 1 hour

# call the now endpoint
async def call_now():
    logger.info("Invoking call to /now endpoint.")
    async with httpx.AsyncClient() as client:
        timeout = httpx.Timeout(TIMEOUT_SECONDS)
        response = await client.get(f"{SELF_URL}/now", timeout=timeout)
        logger.debug(f"Response from /now endpoint: {response.json()}")


# APScheduler does not support async functions, so we need to run the async function in a sync function
def call_now_sync():
    asyncio.run(call_now())


# define schedule to call the now endpoint
scheduler = BackgroundScheduler()
scheduler.add_job(call_now_sync, "interval", minutes=INTERVAL_MINUTES)
# scheduler.add_job(call_now_sync, "interval", seconds=15)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get(
    "/next",
    summary="Get the next scheduled post.",
    description="Get the details of the next scheduled post.",
)
async def next():
    config = LinkedInUploadPostConfiguration()
    posts = load_next_pending_post(config)
    if posts is None:
        return {"message": "No posts found."}
    else:
        return json.loads(json_util.dumps(posts[0]))


@app.get(
    "/now",
    summary="Upload next post to LinkedIn.",
    description="Manually triggers process to upload next post to LinkedIn.",
)
async def now():
    config = LinkedInUploadPostConfiguration()
    state = LinkedInUploadPostState()
    result = await graph.ainvoke(
        input=state
    )  # TODO figure out what to pass, config=config)
    return json.loads(json_util.dumps(result))


@app.get("/", summary="Liveliness probe")
async def home():
    return {"message": "Hello, FastAPI!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
