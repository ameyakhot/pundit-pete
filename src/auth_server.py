import os
import urllib.parse
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback")

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse('<a href="/login">Login with LinkedIn</a>')

@app.get("/login")
def login():
    """Redirects the user to LinkedIn's OAuth authorization page."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "random_string_for_security",
        "scope": "openid profile w_member_social email",
    }
    url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@app.get("/callback")
def callback(code: str = None, error: str = None):
    """Handles the callback from LinkedIn and exchanges the code for tokens."""
    if error:
        return HTMLResponse(f"Error: {error}")
    
    if not code:
        return HTMLResponse("Error: No code received.")

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
    
    response = requests.post(token_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        expires_in = data.get("expires_in")
        
        # In a real app, you'd save these securely. For now, we display them to copy to .env
        content = f"""
        <h1>Login Successful!</h1>
        <p><strong>Access Token:</strong> {access_token[:20]}...</p>
        <p><strong>Expires In:</strong> {expires_in} seconds</p>
        <p><strong>Refresh Token:</strong> {refresh_token}</p>
        <hr>
        <h3>Action Required:</h3>
        <p>Copy the <strong>Refresh Token</strong> above and add it to your <code>.env</code> file as <code>LINKEDIN_REFRESH_TOKEN</code>.</p>
        """
        return HTMLResponse(content)
    else:
        return HTMLResponse(f"Error fetching token: {response.text}")

if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)

