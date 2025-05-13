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
from instagram_graph_api import load_token, refresh_token, auth_flow, upload_reel

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
    elif "youtube.com/watch" in url:
        parsed_url = urlparse(url)
        query_params = {k: v[0] for k, v in [p.split('=') for p in parsed_url.query.split('&')]}
        video_id = query_params.get('v', None)
    
    return video_id or f"video_{int(time.time())}"

def download_video(video_url, download_path):
    """Downloads a video using yt-dlp."""
    print(f"Downloading video from: {video_url}")
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Extract video ID
    video_id = extract_video_id(video_url)
    output_path = os.path.join(download_path, f"{video_id}.mp4")
    
    # First clean up any existing files with this ID
    for file in os.listdir(download_path):
        if video_id in file:
            try:
                os.remove(os.path.join(download_path, file))
                print(f"Removed previous file: {file}")
            except:
                pass

    # Use yt-dlp to download the video as MP4
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'best[ext=mp4]',  # Force mp4 format
        'merge_output_format': 'mp4',  # Force merging to mp4
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        if os.path.exists(output_path):
            print(f"Downloaded video: {output_path}")
            return output_path
        else:
            print(f"Video not found at expected location: {output_path}")
            return None
            
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def repost_with_graph_api():
    """Main function to repost a video using the Graph API."""
    print("Instagram Repost Tool (Graph API Version)")
    print("========================================")
    
    # First, authenticate with Instagram Graph API
    print("Authenticating with Instagram...")
    access_token = authenticate()
    
    if not access_token:
        print("Authentication failed. Could not get access token.")
        return
    
    # Get Instagram accounts
    instagram_accounts = get_user_instagram_accounts(access_token)
    
    if not instagram_accounts:
        print("No Instagram business accounts found. Make sure:")
        print("1. You've connected your Instagram account to a Facebook Page")
        print("2. Your Instagram account is a Professional account")
        print("3. You've authorized the correct permissions for your app")
        return
    
    # Let user select Instagram account if multiple
    selected_account = None
    if len(instagram_accounts) > 1:
        print("Select Instagram account to use:")
        for idx, account in enumerate(instagram_accounts, 1):
            print(f"{idx}. {account.get('username', 'Unknown')}")
        
        choice = int(input("Enter account number: "))
        if 1 <= choice <= len(instagram_accounts):
            selected_account = instagram_accounts[choice-1]
    else:
        selected_account = instagram_accounts[0]
    
    if not selected_account:
        print("No account selected.")
        return
    
    print(f"Using Instagram account: {selected_account.get('username', 'Unknown')}")
    
    # Get video URL
    video_url = input("Enter Instagram Reel or YouTube Short URL: ")
    if not video_url:
        print("No URL provided.")
        return
    
    # Download the video
    video_path = download_video(video_url, DOWNLOAD_FOLDER)
    
    if not video_path or not os.path.exists(video_path):
        print("Failed to download video.")
        return
    
    # Custom caption
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
    
    # Upload to Instagram
    print("Uploading to Instagram...")
    success = upload_media(
        selected_account.get('id'),
        video_path,
        caption,
        access_token
    )
    
    if success:
        print("Successfully reposted content to Instagram!")
    else:
        print("Failed to post to Instagram.")
    
    # Clean up
    if os.path.exists(video_path):
        try:
            os.remove(video_path)
            print(f"Deleted temporary file: {video_path}")
        except:
            pass

if __name__ == "__main__":
    repost_with_graph_api()
