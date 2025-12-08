import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN")

def get_access_token():
    """
    Exchanges the Refresh Token for a fresh Access Token.
    """
    if not REFRESH_TOKEN:
        print("[ERROR] No Refresh Token found in environment variables.")
        return None

    url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")
    except Exception as e:
        print(f"[ERROR] Failed to refresh token: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return None

def get_user_urn(access_token):
    """
    Fetches the authenticated user's URN (ID).
    """
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # sub is the unique user ID in OpenID Connect
        return f"urn:li:person:{data['sub']}"
    except Exception as e:
        print(f"[ERROR] Failed to get user info: {e}")
        return None

def post_to_linkedin(text, article_url=None, article_title=None):
    """
    Publishes a text post (share) to LinkedIn.
    """
    access_token = get_access_token()
    if not access_token:
        return False

    author_urn = get_user_urn(access_token)
    if not author_urn:
        return False

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # Construct the share content
    share_content = {
        "shareCommentary": {
            "text": text
        },
        "shareMediaCategory": "NONE"
    }

    # If there is an article, attach it
    if article_url:
        share_content["shareMediaCategory"] = "ARTICLE"
        share_content["media"] = [
            {
                "status": "READY",
                "description": {
                    "text": article_title or "News Article"
                },
                "originalUrl": article_url,
                "title": {
                    "text": article_title or "Read more"
                }
            }
        ]

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": share_content
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"[SUCCESS] Posted to LinkedIn! ID: {response.json().get('id')}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    # Test (will fail without real tokens)
    print("Test run requires valid tokens in .env")

