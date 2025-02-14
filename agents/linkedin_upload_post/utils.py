from datetime import datetime
from agents.utils import load_mongo_collection
from agents.linkedin_upload_post.configuration import LinkedInUploadPostConfiguration
from agents.linkedin_upload_post.state import LinkedInUploadPostState

prompt = """
Go to linkedin.com and create a post using the text below. Be sure to submit the post when you are done.
<post>
{post}
</post>
"""

draft_prompt = """
Go to linkedin.com and draft a post, but do not actually submit the post.

First, attach the image from the below location.  Once you have posted the image, do not make any changes using the editor, just click "Next"
If no path is provided, you can ignore this instruction.
<image_path>
{image_path}
</image_path>


After that, use the below copy for the post.
<post>
{post}
</post>
Remember, do not actually submit the post.
"""


def build_browser_instructions_prompt(
    state: LinkedInUploadPostState, config: LinkedInUploadPostConfiguration
) -> str:
    """Build system prompt to upload LinkedIn post via browser_use."""
    image_path = state.post.get("image_path", "")

    if config.draft_mode:
        return draft_prompt.format(post=state.post["post"], image_path=image_path)
    return prompt.format(post=state.post["post"])


def load_next_pending_post(config: LinkedInUploadPostConfiguration):

    collection = load_mongo_collection(config)

    # get all posts in pending state scheduled for now (or earlier)
    filter = {
        "$and": [
            {"status": "pending"},
            {
                "scheduled_date": {
                    "$lte": datetime.now(),
                }
            },
        ]
    }
    pending_posts = collection.find(filter)
    return pending_posts
