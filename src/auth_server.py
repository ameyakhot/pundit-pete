import os
import urllib.parse
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from dotenv import load_dotenv

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback")

if not CLIENT_ID or not CLIENT_SECRET:
    logger.error("Missing Client ID or Secret in environment variables.")

app = FastAPI()


@app.get("/")
def home():
    logger.info(f"Home accessed. Redirect URI configured as: {REDIRECT_URI}")
    return HTMLResponse(
        f"""
        <h1>LinkedIn Auth Server</h1>
        <p>Configured Redirect URI: <code>{REDIRECT_URI}</code></p>
        <p><a href="/login">Login with LinkedIn</a></p>
    """
    )


@app.get("/login")
def login():
    """Redirects the user to LinkedIn's OAuth authorization page."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "random_string_for_security",
        "scope": "openid profile w_member_social w_organization_social email",
    }
    url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"

    logger.info(f"Redirecting to LinkedIn Auth URL: {url}")
    logger.info(f"Using Client ID: {CLIENT_ID[:5]}... | Redirect URI: {REDIRECT_URI}")

    return RedirectResponse(url)


@app.get("/callback")
def callback(code: str = None, error: str = None):
    """Handles the callback from LinkedIn and exchanges the code for tokens."""
    if error:
        logger.error(f"LinkedIn returned error: {error}")
        return HTMLResponse(f"Error: {error}")

    if not code:
        logger.error("No code received in callback.")
        return HTMLResponse("Error: No code received.")

    logger.info(f"Received authorization code: {code[:10]}...")

    # Exchange authorization code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    logger.info("Exchanging code for tokens...")
    response = requests.post(token_url, data=payload, headers=headers)

    if response.status_code == 200:
        logger.info("Token exchange successful!")
        data = response.json()

        # Log the full response for debugging (UNMASKED)
        logger.info(f"Full Token Response: {data}")

        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        expires_in = data.get("expires_in")

        # Save to .env automatically
        env_path = ".env"
        try:
            # Read existing lines
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    lines = f.readlines()

            # Prepare new lines
            new_lines = []
            keys_to_remove = ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_REFRESH_TOKEN"]

            # Filter out old tokens
            for line in lines:
                if not any(line.startswith(key) for key in keys_to_remove):
                    new_lines.append(line)

            # Add new tokens
            if access_token:
                new_lines.append(f"\nLINKEDIN_ACCESS_TOKEN={access_token}\n")
            if refresh_token:
                new_lines.append(f"LINKEDIN_REFRESH_TOKEN={refresh_token}\n")

            # Write back
            with open(env_path, "w") as f:
                f.writelines(new_lines)

            logger.info("Successfully saved tokens to .env file")
            save_msg = "<p style='color: green'><strong>SUCCESS: Tokens have been automatically saved to your .env file!</strong></p>"
        except Exception as e:
            logger.error(f"Failed to save to .env: {e}")
            save_msg = f"<p style='color: red'><strong>ERROR: Could not save to .env. Please copy manually.</strong></p>"

        # In a real app, you'd save these securely. For now, we display them to copy to .env
        content = f"""
        <h1>Login Successful!</h1>
        {save_msg}
        <p><strong>Access Token:</strong> {access_token[:20]}...</p>
        <p><strong>Expires In:</strong> {expires_in} seconds</p>
        <p><strong>Refresh Token:</strong> {refresh_token}</p>
        <hr>
        """
        return HTMLResponse(content)
    else:
        return HTMLResponse(f"Error fetching token: {response.text}")


if __name__ == "__main__":
    import uvicorn

    print("Starting server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
