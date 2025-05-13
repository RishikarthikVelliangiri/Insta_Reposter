import os
import sys
import time
import subprocess
from instagrapi import Client
import yt_dlp

# --- Configuration ---
# Default configurations that can be overridden at runtime
DEFAULT_CAPTION = "Thanks for watching, hit follow for more! 🙏"
FIXED_HASHTAGS = "#reels #instareels #trending #viral #foryou #fyp #repost"
DOWNLOAD_FOLDER = "downloaded_reels"

# Will be prompted during runtime
INSTAGRAM_USERNAME = None
INSTAGRAM_PASSWORD = None

def download_reel(reel_url, download_path):
    """Downloads a reel using yt-dlp."""
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Try to extract ID from Instagram URL
    reel_id = None
    if "instagram.com/reel/" in reel_url:
        reel_id = reel_url.split("/reel/")[1].split("/")[0].split("?")[0]
    elif "instagram.com/p/" in reel_url:
        reel_id = reel_url.split("/p/")[1].split("/")[0].split("?")[0]
    
    if reel_id:
        output_path = os.path.join(download_path, f"{reel_id}.mp4")
    else:
        output_path = os.path.join(download_path, "instagram_video.mp4")
    
    # First clean up any existing files with this ID
    for file in os.listdir(download_path):
        if reel_id and reel_id in file:
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
            ydl.download([reel_url])
        
        if os.path.exists(output_path):
            print(f"Downloaded video: {output_path}")
            return output_path
        else:
            print(f"Video not found at expected location: {output_path}")
            return None
            
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def login_to_instagram(username, password):
    """Logs into Instagram using instagrapi."""
    cl = Client()
    session_file = f"{username}_session.json"
    
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(username, password)
            cl.get_timeline_feed()
            print(f"Logged in successfully using saved session for {username}")
            return cl
        except Exception as e:
            print(f"Could not use saved session: {e}. Trying fresh login.")
    
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)
        print(f"Logged in successfully and saved session for {username}")
        return cl
    except Exception as e:
        print(f"Error logging in: {e}")
        return None

def repost_reel():
    """Main function to repost a reel."""
    global INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
    
    print("Starting Instagram Reel Repost Agent")
    print("------------------------------------")
    
    # Get Instagram credentials if not provided
    if not INSTAGRAM_USERNAME:
        INSTAGRAM_USERNAME = input("Enter Instagram username: ")
    
    if not INSTAGRAM_PASSWORD:
        import getpass
        INSTAGRAM_PASSWORD = getpass.getpass("Enter Instagram password (input will be hidden): ")
        
    reel_url = input("Enter Instagram Reel URL: ")
    if "instagram.com/reel/" not in reel_url and "instagram.com/p/" not in reel_url:
        print("Invalid Instagram URL. Must contain 'reel' or 'p' in the path.")
        return
    
    # Download the reel
    print(f"Downloading reel from: {reel_url}")
    video_path = download_reel(reel_url, DOWNLOAD_FOLDER)
    
    if not video_path or not os.path.exists(video_path):
        print("Failed to download video.")
        return
    
    # Login to Instagram
    print("Logging into Instagram...")
    client = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    
    if not client:
        print("Failed to login to Instagram.")
        return
    
    # Upload the reel
    print("Uploading reel to Instagram...")
    full_caption = f"{FIXED_CAPTION}\n\n{FIXED_HASHTAGS}"
    
    try:
        # First attempt with clip_upload (for Reels)
        try:
            print("Trying clip_upload method...")
            client.clip_upload(
                path=video_path,
                caption=full_caption
            )
            print("Reel uploaded successfully!")
        except Exception as e:
            print(f"clip_upload failed: {e}")
            print("Trying video_upload method...")
            client.video_upload(
                path=video_path,
                caption=full_caption
            )
            print("Video uploaded successfully!")
    except Exception as e:
        print(f"Upload failed: {e}")
        
        # Try to provide specific solutions based on error message
        error_msg = str(e).lower()
        if "moviepy" in error_msg:
            print("\nTroubleshooting:")
            print("1. The error is related to moviepy, which is needed for video processing.")
            print("2. Try these commands in your terminal:")
            print("   pip install moviepy==1.0.3")
            print("   pip install decorator==4.4.2")
            print("3. Make sure ffmpeg is installed and in your PATH.")
        elif "ffmpeg" in error_msg:
            print("\nTroubleshooting:")
            print("1. The error is related to ffmpeg, which is needed for video processing.")
            print("2. Download ffmpeg from: https://ffmpeg.org/download.html")
            print("3. Add ffmpeg to your PATH or set IMAGEIO_FFMPEG_EXE environment variable.")
    finally:
        # Clean up
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"Deleted temp file: {video_path}")
            except:
                pass

if __name__ == "__main__":
    repost_reel()
