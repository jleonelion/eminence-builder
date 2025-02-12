import os
import logging
import logging.config
import json
from bson import json_util
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
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

app = FastAPI()

# TODO setup recurring task to check for pending posts
# def scheduled_task():
#     print("This task runs every 10 seconds.")

# scheduler = BackgroundScheduler()
# scheduler.add_job(scheduled_task, "interval", seconds=10)
# scheduler.start()


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


@app.get("/")
async def home():
    return {"message": "Hello, FastAPI!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
