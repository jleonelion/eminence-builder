"""
This example illustrates a basic example of the oauth authorization code flow.

Pre-requisites:
1. Add CLIENT_ID, CLIENT_SECRET, and OAUTH2_REDIRECT_URL variables to the top-level .env file.
The OAUTH2_REDIRECT_URL should be set to "http://localhost:3000/oauth".
2. The associated developer app you are using should have access to r_liteprofile, which can be
obtained through requesting the self-serve Sign In With LinkedIn API product on the LinkedIn
Developer Portal.
3. Set your developer app's OAuth redirect URL to "http://localhost:3000/oauth" from the Developer Portal

Steps:
1. Run script: `python3 oauth-member-auth-redirect.py`
2. Navigate to localhost:3000
3. Login as LinkedIn member and authorize application
4. View member profile data
"""
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, redirect, request
from dotenv import load_dotenv, find_dotenv
from linkedin_api.clients.auth.client import AuthClient
from linkedin_api.clients.restli.client import RestliClient
from pymongo import MongoClient
from datetime import datetime

load_dotenv(find_dotenv())

def convert_to_unicode_bold(text):
    # Unicode bold character mappings
    unicode_bold = {
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠',
        'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧',
        'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭', 'u': '𝐮',
        'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆',
        'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍',
        'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔',
        'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙'
    }
    
    # Split text by bold markers
    parts = text.split('**')
    result = []
    
    # Convert alternating parts
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Bold sections
            bold_text = ''.join(unicode_bold.get(c, c) for c in part)
            result.append(bold_text)
        else:  # Regular text
            result.append(part)
            
    return ''.join(result)

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
OAUTH2_REDIRECT_URL = os.getenv("OAUTH2_REDIRECT_URL")

app = Flask(__name__)

access_token = None

auth_client = AuthClient(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_url=OAUTH2_REDIRECT_URL
)
restli_client = RestliClient()
restli_client.session.hooks["response"].append(lambda r: r.raise_for_status())

@app.route("/", methods=["GET"])
def main():
    global access_token
    if access_token == None:
        return redirect(auth_client.generate_member_auth_url(scopes=["profile", "w_member_social", "openid", "email"]))
    else:
        return restli_client.get(resource_path="/userinfo", access_token=access_token).entity
        # return restli_client.get(resource_path="/me", access_token=access_token).entity

@app.route("/dailypost", methods=["GET"])
def dailypost():
    global access_token
    if access_token == None:
        return redirect(auth_client.generate_member_auth_url(scopes=["profile", "w_member_social", "openid", "email"]))
    me_response = restli_client.get(resource_path="/me", access_token=access_token).entity


    client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))
    db = client[os.getenv("MONGODB_DATABASE", "social-media")]
    collection = db[os.getenv("MONGODB_COLLECTION_LINKEDIN", "linkedin-posts")]
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

    if pending_posts is not None:
        # get the first post
        post = pending_posts[0]
        post['post'] = convert_to_unicode_bold(post['post'])
        # TODO: update status to queued

        # update the status to posted
        if '_id' in post:
            del post['_id']

        return post
    
    posts = []
    for post in pending_posts:
        
        posts.append(post)

    return {"posts": posts}

@app.route("/oauth", methods=["GET"])
def oauth():
    global access_token

    args = request.args
    auth_code = args.get("code")

    if auth_code:
        token_response = auth_client.exchange_auth_code_for_access_token(auth_code)
        access_token = token_response.access_token
        print(f"Access token: {access_token}")
        return redirect("/")


if __name__ == "__main__":
    app.run(host="localhost", port=3000)