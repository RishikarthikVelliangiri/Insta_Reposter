import os
import sys
import time
import json
import argparse
import re
from instagrapi import Client
import yt_dlp

# --- Configuration ---
INSTAGRAM_USERNAME = "dantesclipz"
INSTAGRAM_PASSWORD = "DantesisBest101"
DEFAULT_CAPTION = "Thanks for watching, hit follow for more! 🙏"
DEFAULT_HASHTAGS = "#reels #instareels #trending #viral #foryou #fyp #repost"
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

def download_video(video_url, download_path, source="instagram"):
    """Downloads a video using yt-dlp from either Instagram or YouTube."""
    print(f"Downloading {source} video from: {video_url}")
    print("STEP_MARKER: DOWNLOAD_STARTED")
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Extract video ID
    video_id = extract_video_id(video_url)
    output_path = os.path.join(download_path, f"{video_id}.mp4")
    
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
    print("Logging into Instagram...")
    
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
        print(f"Error: Failed to login: {e}")
        return None

def repost_video(video_url, source="instagram", custom_caption=None, custom_hashtags=None):
    """Main function to repost a video (Instagram reel or YouTube short)."""
    if not video_url:
        print("Error: No video URL provided")
        return False
        
    # Validate URL based on source
    is_valid = False
    if source == "instagram" and ("instagram.com/reel/" in video_url or "instagram.com/p/" in video_url):
        is_valid = True
    elif source == "youtube" and ("youtube.com/shorts/" in video_url or "youtu.be/" in video_url):
        is_valid = True
        
    if not is_valid:
        print(f"Error: Invalid {source} URL")
        return False
    
    # STEP 1: Download phase
    print("STEP_MARKER: DOWNLOAD_STARTED")
    print("Downloading reel from: " + reel_url)
    video_path = download_reel(reel_url, DOWNLOAD_FOLDER)
    
    if not video_path or not os.path.exists(video_path):
        print("Error: Failed to download video.")
        return False
    
    # Mark download complete
    print("STEP_MARKER: DOWNLOAD_COMPLETED")
    print("Downloaded video: " + video_path)
    
    # Wait a moment to ensure status is updated
    time.sleep(1)
    
    # STEP 2: Login phase
    print("STEP_MARKER: LOGIN_STARTED")
    print("Logging into Instagram...")
    client = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    
    if not client:
        print("Error: Failed to login to Instagram.")
        if os.path.exists(video_path):
            os.remove(video_path)
        return False
        
    # Mark login complete
    print("STEP_MARKER: LOGIN_COMPLETED")
    
    # Wait a moment to ensure status is updated
    time.sleep(1)
      # Use custom caption and hashtags if provided, otherwise use defaults
    caption_text = custom_caption if custom_caption else DEFAULT_CAPTION
    hashtags_text = custom_hashtags if custom_hashtags else DEFAULT_HASHTAGS
    
    # STEP 3: Upload phase - mark with clear step marker
    print("STEP_MARKER: UPLOAD_STARTED")
    print("Uploading reel to Instagram...")
    full_caption = f"{caption_text}\n\n{hashtags_text}"
    success = False
    
    try:
        # First attempt with clip_upload (for Reels)
        try:
            print("Trying clip_upload method...")
            client.clip_upload(
                path=video_path,
                caption=full_caption
            )
            print("STEP_MARKER: UPLOAD_COMPLETED")
            print("Reel uploaded successfully!")
            success = True
        except Exception as e:
            print(f"clip_upload failed: {e}")
            print("Trying video_upload method...")
            client.video_upload(
                path=video_path,
                caption=full_caption
            )
            print("STEP_MARKER: UPLOAD_COMPLETED")
            print("Video uploaded successfully!")
            success = True
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
    
    return success

# Format a result for the API
def format_api_result(success, message="", status="completed", steps=None):
    if steps is None:
        steps = []
    
    result = {
        "success": success,
        "message": message,
        "status": status,
        "steps": steps
    }
    
    return json.dumps(result)

# For use with API
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Repost Instagram Reels')
    parser.add_argument('url', help='Instagram reel URL to repost')
    parser.add_argument('--caption', help='Custom caption for the repost')
    parser.add_argument('--hashtags', help='Custom hashtags for the repost')
    
    args = parser.parse_args()
    
    if args.url:
        success = repost_reel(args.url, args.caption, args.hashtags)
        if success:
            print(format_api_result(True, "Reel uploaded successfully"))
        else:
            print(format_api_result(False, "Failed to upload reel"))
    else:
        print(format_api_result(False, "Error: No Instagram URL provided"))
