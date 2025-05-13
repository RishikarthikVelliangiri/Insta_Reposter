"""
Instagram Graph API Integration for Repost Tool
This module provides functions to authenticate and post content using Instagram Graph API
"""

import os
import requests
import json
import webbrowser
from urllib.parse import urlencode

# Configuration - Values from Meta Developer Dashboard
APP_ID = "1842291649888953"
APP_SECRET = "4315cb405ae229639ec08"
REDIRECT_URI = "https://insta-reposter32.vercel.app/auth/callback"
GRAPH_API_VERSION = "v18.0"  # Update to the latest version
TOKEN_FILE = "instagram_token.json"

# Permission scopes needed
SCOPES = [
    "instagram_basic",        # Basic Instagram account info
    "instagram_content_publish", # Permission to publish content
    "pages_read_engagement",  # Read page engagement metrics
    "pages_show_list"         # Show list of pages user manages
]

def get_authorization_url():
    """Generate the URL to authorize your app with Instagram."""
    base_url = "https://www.facebook.com/{}/dialog/oauth".format(GRAPH_API_VERSION)
    
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": ",".join(SCOPES),
        "response_type": "code",
        "state": "instagram_repost_auth"  # For CSRF protection
    }
    
    auth_url = "{}?{}".format(base_url, urlencode(params))
    return auth_url

def open_auth_page():
    """Open the authorization page in the default web browser."""
    auth_url = get_authorization_url()
    print(f"Opening authorization URL: {auth_url}")
    webbrowser.open(auth_url)
    print("Please authorize the application and copy the code from the redirect URL")

def exchange_code_for_token(auth_code):
    """Exchange the auth code for a long-lived access token."""
    token_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token"
    
    params = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": auth_code
    }
    
    response = requests.get(token_url, params=params)
    
    if response.status_code != 200:
        print(f"Error getting access token: {response.text}")
        return None
        
    token_data = response.json()
    
    # Exchange for long-lived token
    long_lived_token_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token"
    long_lived_params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": token_data.get("access_token")
    }
    
    long_lived_response = requests.get(long_lived_token_url, params=long_lived_params)
    
    if long_lived_response.status_code != 200:
        print(f"Error getting long-lived token: {long_lived_response.text}")
        return token_data
    
    return long_lived_response.json()

def save_token(token_data):
    """Save the token data to a file."""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)
    print(f"Token saved to {TOKEN_FILE}")

def load_token():
    """Load the token data from file."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def get_user_instagram_accounts(access_token):
    """Get all Instagram accounts connected to the user."""
    # First, get user's Facebook pages
    pages_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/accounts"
    params = {"access_token": access_token}
    
    response = requests.get(pages_url, params=params)
    if response.status_code != 200:
        print(f"Error getting user's Facebook pages: {response.text}")
        return []
    
    pages = response.json().get("data", [])
    instagram_accounts = []
    
    # For each page, check if there's a connected Instagram account
    for page in pages:
        page_id = page.get("id")
        instagram_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/instagram_business_account"
        instagram_params = {"access_token": access_token}
        
        instagram_response = requests.get(instagram_url, params=instagram_params)
        if instagram_response.status_code == 200 and "data" in instagram_response.json():
            instagram_account = instagram_response.json().get("data", {})
            if instagram_account:
                instagram_account["page_id"] = page_id
                instagram_account["page_name"] = page.get("name")
                instagram_accounts.append(instagram_account)
    
    return instagram_accounts

def upload_media(instagram_account_id, video_path, caption, access_token):
    """Upload a video to Instagram using Graph API."""
    # Step 1: Create a media container
    container_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{instagram_account_id}/media"
    container_params = {
        "media_type": "REELS",
        "video_url": video_path,
        "caption": caption,
        "access_token": access_token
    }
    
    container_response = requests.post(container_url, data=container_params)
    if container_response.status_code != 200:
        print(f"Error creating media container: {container_response.text}")
        return False
    
    creation_id = container_response.json().get("id")
    
    # Step 2: Publish the container
    publish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{instagram_account_id}/media_publish"
    publish_params = {
        "creation_id": creation_id,
        "access_token": access_token
    }
    
    publish_response = requests.post(publish_url, data=publish_params)
    if publish_response.status_code != 200:
        print(f"Error publishing media: {publish_response.text}")
        return False
    
    print(f"Successfully published media with ID: {publish_response.json().get('id')}")
    return True

def authenticate():
    """Interactive authentication flow."""
    # Check if we already have a token
    token_data = load_token()
    if token_data and "access_token" in token_data:
        print("Found existing token. Testing its validity...")
        # Test token validity by making a simple API call
        test_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me"
        test_params = {"access_token": token_data["access_token"]}
        
        response = requests.get(test_url, params=test_params)
        if response.status_code == 200:
            print("Token is valid!")
            return token_data["access_token"]
        else:
            print("Token has expired. Generating new one...")
    
    # Open auth page and get auth code
    open_auth_page()
    auth_code = input("Enter the code from the redirect URL: ")
    
    # Exchange code for token
    token_data = exchange_code_for_token(auth_code)
    if token_data and "access_token" in token_data:
        save_token(token_data)
        return token_data["access_token"]
    
    return None

if __name__ == "__main__":
    # Test the authentication flow
    access_token = authenticate()
    if access_token:
        instagram_accounts = get_user_instagram_accounts(access_token)
        print(f"Found {len(instagram_accounts)} Instagram accounts:")
        for idx, account in enumerate(instagram_accounts, 1):
            print(f"{idx}. {account.get('username', 'Unknown')}")
    else:
        print("Authentication failed.")
