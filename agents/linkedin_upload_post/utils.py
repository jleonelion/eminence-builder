from datetime import datetime
from pymongo import MongoClient
from agents.linkedin_upload_post.configuration import LinkedInUploadPostConfiguration
from agents.linkedin_upload_post.state import LinkedInUploadPostState

prompt = """
Go to linkedin.com and create a post using the text below. Be sure to submit the post when you are done.
<post>
{post}
</post>
"""

draft_prompt = """
Go to linkedin.com and draft a post using the text below. Do not actually submit the post.
<post>
{post}
</post>
"""


def build_browser_instructions_prompt(
    state: LinkedInUploadPostState, config: LinkedInUploadPostConfiguration
) -> str:
    """Get the system prompt for generating a post."""
    if config.draft_mode:
        return draft_prompt.format(post=state.post["post"])
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

def load_mongo_collection(config):
    client = MongoClient(config.mongo_url)
    db = client[config.mongo_db]
    collection = db[config.mongo_collection_linkedin_posts]
    return collection
