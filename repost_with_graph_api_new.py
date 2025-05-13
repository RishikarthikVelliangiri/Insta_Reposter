#!/usr/bin/env python3
"""
Instagram Repost Tool using Graph API for authentication
"""

import os
import sys
import time
import argparse
from urllib.parse import urlparse
import yt_dlp
from instagram_graph_api import load_token, refresh_token, auth_flow, upload_reel, TOKEN_FILE

# --- Configuration ---
DEFAULT_CAPTION = "Thanks for watching, hit follow for more! 🙏"
HASHTAGS = "#reels #instareels #trending #viral #foryou #fyp #repost"
DOWNLOAD_FOLDER = "downloaded_reels"

def extract_video_id(url):
    """Extract video ID from Instagram or YouTube URL."""
    video_id = None
    
    # Instagram patterns
    if "instagram.com/reel/" in url:
        video_id = url.split("/reel/")[1].split("/")[0].split("?")[0]
    elif "instagram.com/p/" in url:
        video_id = url.split("/p/")[1].split("/")[0].split("?")[0]
    # YouTube Shorts patterns
    elif "youtube.com/shorts/" in url:
        video_id = url.split("/shorts/")[1].split("?")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    
    return video_id or "video_" + str(int(time.time()))

def determine_source(url):
    """Determine the source platform of the video URL."""
    if "instagram.com" in url:
        return "instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    else:
        return "unknown"

def download_video(url, output_folder):
    """Download a video using yt-dlp."""
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Extract video ID for filename
    video_id = extract_video_id(url)
    output_path = os.path.join(output_folder, f"{video_id}.mp4")
    
    # Clean up any existing files with this ID
    for file in os.listdir(output_folder):
        if video_id in file:
            try:
                os.remove(os.path.join(output_folder, file))
                print(f"Removed previous file: {file}")
            except Exception as e:
                print(f"Failed to remove file: {e}")
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': False,
        'no_warnings': False
    }
    
    # Download the video
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return output_path
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

def authenticate_instagram():
    """Authenticate with Instagram Graph API."""
    # Check for existing token
    token_data = load_token()
    
    if token_data:
        print(f"Found existing authentication for {token_data.get('username', 'unknown user')}")
        
        # Refresh token if needed
        token_data = refresh_token(token_data)
        return token_data
    else:
        # Start authentication flow
        print("No stored authentication. Starting Instagram login flow...")
        auth_flow()
        return load_token()

def repost_with_graph_api():
    """Main function to repost content using Instagram Graph API."""
    print("\nInstagram Repost Tool (Graph API)")
    print("=================================\n")
    
    # Step 1: Authenticate with Instagram Graph API
    print("Step 1: Authenticating with Instagram...")
    token_data = authenticate_instagram()
    
    if not token_data:
        print("Authentication failed. Please try again.")
        return
    
    print(f"Successfully authenticated as {token_data.get('username', 'unknown user')}!")
    
    # Step 2: Get video URL from user
    video_url = input("\nStep 2: Enter Instagram Reel or YouTube Shorts URL: ")
    if not video_url:
        print("No URL provided.")
        return
    
    # Validate URL
    source = determine_source(video_url)
    if source == "unknown":
        print("Invalid URL. Please provide a valid Instagram or YouTube URL.")
        return
    elif source == "instagram" and "instagram.com/reel/" not in video_url and "instagram.com/p/" not in video_url:
        print("Invalid Instagram URL. Please provide a valid Instagram Reel or Post URL.")
        return
    
    # Step 3: Download the video
    print(f"\nStep 3: Downloading {source} video...")
    video_path = download_video(video_url, DOWNLOAD_FOLDER)
    
    if not video_path or not os.path.exists(video_path):
        print("Failed to download video.")
        return
    
    # Step 4: Custom caption
    print("\nStep 4: Prepare caption")
    use_default = input("Use default caption? (y/n): ").lower() == 'y'
    if use_default:
        caption = f"{DEFAULT_CAPTION}\n\n{HASHTAGS}"
    else:
        custom_caption = input("Enter your custom caption: ")
        include_hashtags = input("Include default hashtags? (y/n): ").lower() == 'y'
        if include_hashtags:
            caption = f"{custom_caption}\n\n{HASHTAGS}"
        else:
            caption = custom_caption
    
    # Step 5: Upload to Instagram
    print("\nStep 5: Uploading to Instagram...")
    success = upload_reel(video_path, caption, token_data)
    
    if success:
        print("\n✅ Successfully reposted content to Instagram!")
    else:
        print("\n❌ Failed to post to Instagram.")
    
    # Clean up
    if os.path.exists(video_path):
        try:
            os.remove(video_path)
            print(f"Deleted temporary file: {video_path}")
        except:
            pass

if __name__ == "__main__":
    repost_with_graph_api()
