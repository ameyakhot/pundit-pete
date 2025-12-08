import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN")
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")  # Direct access token support
ORG_ID = os.getenv("LINKEDIN_ORG_ID")  # Organization ID for Company Page


def check_token_scopes(access_token):
    """
    Checks what scopes the current access token has.
    """
    try:
        # Try to get user info which will show available scopes in headers or response
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        # LinkedIn sometimes returns scopes in the response or we can infer from what works
        print(f"[DEBUG] Token validation - Status: {response.status_code}")

        # Check if we can access organization endpoints
        org_url = "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee"
        org_headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        org_response = requests.get(org_url, headers=org_headers)

        if org_response.status_code == 200:
            print("[INFO] Token HAS w_organization_social scope ✓")
            return True
        elif org_response.status_code == 403:
            print("[WARNING] Token MISSING w_organization_social scope ✗")
            print(
                "[ACTION REQUIRED] Re-authenticate to get new token with organization permissions"
            )
            return False
        else:
            print(f"[DEBUG] Organization endpoint returned: {org_response.status_code}")
            return False
    except Exception as e:
        print(f"[DEBUG] Could not check token scopes: {e}")
        return False


def get_access_token():
    """
    Returns a valid Access Token.
    1. Checks LINKEDIN_ACCESS_TOKEN first.
    2. If missing, exchanges LINKEDIN_REFRESH_TOKEN for a new one.
    """
    # Priority 1: Direct Access Token (Valid for 60 days)
    if ACCESS_TOKEN:
        return ACCESS_TOKEN

    # Priority 2: Refresh Token Flow
    if not REFRESH_TOKEN:
        print("[ERROR] No LINKEDIN_ACCESS_TOKEN or LINKEDIN_REFRESH_TOKEN found.")
        return None

    print("[INFO] Refreshing access token...")
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
        try:
            print(f"Response: {response.text}")
        except:
            pass
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


def get_organization_urn(access_token, org_id=None):
    """
    Gets the Organization URN for posting to a Company Page.
    If org_id is provided in env, uses it. Otherwise, fetches user's organizations.
    """
    # If org_id is provided in env, use it directly
    if org_id:
        return f"urn:li:organization:{org_id}"

    # Otherwise, try to fetch the user's organizations
    # Note: This requires the 'w_organization_social' scope
    url = "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Find organizations where user is an admin
        if "elements" in data:
            for element in data["elements"]:
                org_urn = element.get("organizationalTarget")
                if org_urn:
                    print(f"[INFO] Found organization: {org_urn}")
                    return org_urn

        print(
            "[WARNING] No organizations found. Using provided ORG_ID or falling back to personal profile."
        )
        return None
    except Exception as e:
        print(f"[WARNING] Could not fetch organizations: {e}")
        print("[INFO] Please set LINKEDIN_ORG_ID in .env file")
        return None


def verify_organization_access(access_token, org_id):
    """
    Verifies that the user has admin access to post on behalf of the organization.
    Returns True if access is verified, False otherwise.
    """
    # Try the organizationalEntityAcls endpoint
    url = f"https://api.linkedin.com/v2/organizationalEntityAcls?q=organizationalTarget&organizationalTarget=urn:li:organization:{org_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG] Organization access response: {data}")
            if "elements" in data and len(data["elements"]) > 0:
                for element in data["elements"]:
                    role = element.get("role", "")
                    state = element.get("state", "")
                    print(f"[DEBUG] Found role: {role}, state: {state}")
                    # Check if user has any admin-related role (be flexible with role names)
                    if "ADMIN" in role.upper() or role.upper() in [
                        "ADMINISTRATOR",
                        "CONTENT_ADMIN",
                        "ADMIN",
                    ]:
                        print(f"[INFO] Verified admin access with role: {role}")
                        return True
                print("[WARNING] User does not have admin role for this organization.")
                print(
                    "[DEBUG] Available roles:",
                    [e.get("role") for e in data.get("elements", [])],
                )
                # If we got a response but no admin role, still return False
                return False
            else:
                print("[WARNING] No access records found for this organization.")
                return False
        elif response.status_code == 403:
            print("[WARNING] 403 Forbidden when checking organization access.")
            print(
                "[INFO] This might mean the token doesn't have w_organization_social scope."
            )
            print("[INFO] Response:", response.text)
            # Return False but don't block - let the actual post attempt handle it
            return False
        else:
            print(
                f"[WARNING] Unexpected status code {response.status_code} when checking access"
            )
            return False
    except Exception as e:
        print(f"[WARNING] Could not verify organization access: {e}")
        # Don't block on verification failure - let the actual post attempt be the real test
        return False


def post_to_linkedin(text, article_url=None, article_title=None, use_company_page=True):
    """
    Publishes a text post (share) to LinkedIn.
    If use_company_page is True, posts to the Company Page (QFoundry).
    Otherwise, posts to personal profile.
    """
    access_token = get_access_token()
    if not access_token:
        print("[ERROR] Could not obtain a valid access token. Aborting.")
        return False

    # Check token scopes if posting to company page
    if use_company_page:
        print("[INFO] Checking token permissions...")
        if not check_token_scopes(access_token):
            print("[ERROR] Token does not have required w_organization_social scope.")
            print("[ACTION] Please re-authenticate:")
            print("  1. Run: uv run python src/auth_server.py")
            print("  2. Go to http://localhost:8000 and login")
            print("  3. Approve the 'Post on behalf of your organization' permission")
            return False

    # Determine author URN
    if use_company_page:
        if not ORG_ID:
            print("[ERROR] LINKEDIN_ORG_ID not set in .env")
            return False

        # Verify user has access to the organization (non-blocking - just a warning)
        if not verify_organization_access(access_token, ORG_ID):
            print(
                "[WARNING] Could not verify admin access, but attempting post anyway..."
            )
            print("[INFO] If this fails, make sure you:")
            print("  1. Are an admin of the QFoundry page")
            print("  2. Have re-authenticated with w_organization_social scope")
            # Don't return False - let the actual API call determine if we have access

        author_urn = f"urn:li:organization:{ORG_ID}"
        print(f"[INFO] Posting as organization: {author_urn}")
    else:
        author_urn = get_user_urn(access_token)
        if not author_urn:
            print("[ERROR] Could not fetch user URN. Aborting.")
            return False
        print(f"[INFO] Posting as user: {author_urn}")

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Construct the share content
    share_content = {"shareCommentary": {"text": text}, "shareMediaCategory": "NONE"}

    # If there is an article, attach it
    if article_url:
        share_content["shareMediaCategory"] = "ARTICLE"
        share_content["media"] = [
            {
                "status": "READY",
                "description": {"text": article_title or "News Article"},
                "originalUrl": article_url,
                "title": {"text": article_title or "Read more"},
            }
        ]

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": share_content},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        # Debug: Log the payload (masking sensitive data)
        debug_payload = payload.copy()
        print(f"[DEBUG] Posting with author: {debug_payload['author']}")
        print(f"[DEBUG] Visibility: {debug_payload['visibility']}")

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"[SUCCESS] Posted to LinkedIn! ID: {response.json().get('id')}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to post: {e}")
        try:
            print(f"Response: {response.text}")
            if response.status_code == 403:
                print("\n[DEBUG] 403 Forbidden usually means:")
                print(
                    "1. Token doesn't have w_organization_social scope - RE-AUTHENTICATE"
                )
                print("2. User is not an admin of the organization")
                print("3. Organization ID is incorrect")
        except:
            pass
        return False


if __name__ == "__main__":
    # Test (will fail without real tokens)
    print("Test run requires valid tokens in .env")
