"""
Helper script to find your LinkedIn Organization ID for Company Page posting.
Run this to see all organizations you manage, then copy the ID to your .env file.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    print("[ERROR] LINKEDIN_ACCESS_TOKEN not found in .env")
    exit(1)

url = "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    print("=" * 60)
    print("Your Managed Organizations:")
    print("=" * 60)
    
    if 'elements' in data and len(data['elements']) > 0:
        for i, element in enumerate(data['elements'], 1):
            org_urn = element.get('organizationalTarget', 'N/A')
            role = element.get('role', 'N/A')
            
            # Extract numeric ID from URN (e.g., "urn:li:organization:123456" -> "123456")
            org_id = org_urn.split(':')[-1] if ':' in org_urn else org_urn
            
            print(f"\n{i}. Organization URN: {org_urn}")
            print(f"   Organization ID: {org_id}")
            print(f"   Your Role: {role}")
            
            # Try to get organization name
            try:
                org_url = f"https://api.linkedin.com/v2/organizations/{org_id}"
                org_response = requests.get(org_url, headers=headers)
                if org_response.status_code == 200:
                    org_data = org_response.json()
                    name = org_data.get('name', 'N/A')
                    print(f"   Name: {name}")
            except:
                pass
        
        print("\n" + "=" * 60)
        print("ACTION: Copy the Organization ID (numeric) for QFoundry")
        print("and add it to your .env file as: LINKEDIN_ORG_ID=123456")
        print("=" * 60)
    else:
        print("No organizations found. Make sure you have admin access to a Company Page.")
        
except Exception as e:
    print(f"[ERROR] Failed to fetch organizations: {e}")
    if hasattr(e, 'response') and e.response:
        print(f"Response: {e.response.text}")

