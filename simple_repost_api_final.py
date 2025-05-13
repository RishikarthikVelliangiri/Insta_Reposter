import os
import sys
import time
import json
import argparse
from instagrapi import Client
import yt_dlp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD", "")
DEFAULT_CAPTION = "Thanks for watching, hit follow for more! 🙏"
DEFAULT_HASHTAGS = "#reels #instareels #trending #viral #foryou #fyp #repost"
DOWNLOAD_FOLDER = "downloaded_reels"

def safe_print_error(message, error):
    """Print errors safely without Unicode issues"""
    error_str = str(error)
    # Replace problematic characters instead of using backslash in f-string
    safe_error = error_str.encode('ascii', 'replace').decode('ascii')
    print(f"{message}: {safe_error}")

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
        if video_id and video_id in file:
            try:
                os.remove(os.path.join(download_path, file))
                print(f"Removed previous file: {file}")
            except Exception as e:
                safe_print_error("Error removing file", e)
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
            print("STEP_MARKER: DOWNLOAD_COMPLETED")
            return output_path
        else:
            print(f"Video not found at expected location: {output_path}")
            return None
            
    except Exception as e:
        safe_print_error("Error downloading video", e)
        return None

def login_to_instagram(username, password):
    """Logs into Instagram using instagrapi."""
    print("Logging into Instagram...")
    print("STEP_MARKER: LOGIN_STARTED")
    
    cl = Client()
    session_file = f"{username}_session.json"
    
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(username, password)
            cl.get_timeline_feed()
            print(f"Logged in successfully using saved session for {username}")
            print("STEP_MARKER: LOGIN_COMPLETED")
            return cl
        except Exception as e:
            safe_print_error("Could not use saved session", e)
    
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)
        print(f"Logged in successfully and saved session for {username}")
        print("STEP_MARKER: LOGIN_COMPLETED")
        return cl
    except Exception as e:
        safe_print_error("Error: Failed to login", e)
        return None

def repost_video(video_url, custom_caption=None, custom_hashtags=None, source="instagram"):
    """Main function to repost a video from Instagram or YouTube to Instagram."""
    success = False  # Initialize success flag
    upload_success = False  # Initialize upload success flag
    video_path = None  # Initialize video path
    
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
    
    try:
        # STEP 1: Download phase
        video_path = download_video(video_url, DOWNLOAD_FOLDER, source)
        
        if not video_path or not os.path.exists(video_path):
            print("Error: Failed to download video.")
            return False
        
        # Wait a moment to ensure status is updated
        time.sleep(1)
        
        # STEP 2: Login phase
        client = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        
        if not client:
            print("Error: Failed to login to Instagram.")
            if os.path.exists(video_path):
                os.remove(video_path)
            return False
        
        # Wait a moment to ensure status is updated
        time.sleep(1)
        
        # Use custom caption and hashtags if provided, otherwise use defaults
        # Explicitly check if they're None or empty strings
        caption_text = DEFAULT_CAPTION
        hashtags_text = DEFAULT_HASHTAGS
        
        print("Processing caption and hashtags...")
        
        # Only use custom caption if it's not None and not empty
        if custom_caption and isinstance(custom_caption, str) and custom_caption.strip():
            caption_text = custom_caption.strip()
            print("Using custom caption")
        else:
            print("Using default caption")
        
        # Only use custom hashtags if it's not None and not empty
        if custom_hashtags and isinstance(custom_hashtags, str) and custom_hashtags.strip():
            # Make sure hashtags start with #
            hashtags_text = custom_hashtags.strip()
            
            # If hashtags don't start with # and there are spaces, add # to each word
            if not hashtags_text.startswith("#") and " " in hashtags_text:
                words = hashtags_text.split()
                hashtags_text = " ".join([f"#{w}" if not w.startswith("#") else w for w in words])
            # If there's just one word without #, add it
            elif not hashtags_text.startswith("#"):
                hashtags_text = f"#{hashtags_text}"
                
            print("Using custom hashtags")
        else:
            print("Using default hashtags")
        
        # STEP 3: Upload phase
        print("STEP_MARKER: UPLOAD_STARTED")
        print(f"Uploading {source} video to Instagram...")
        full_caption = f"{caption_text}\n\n{hashtags_text}"
        print("Caption and hashtags prepared")
        
        try:
            print("Starting upload attempt...")
            # First attempt with clip_upload (for Reels)
            try:
                print("Trying clip_upload method...")
                client.clip_upload(
                    path=video_path,
                    caption=full_caption
                )
                upload_success = True
                print("Reel uploaded successfully!")
                print("STEP_MARKER: UPLOAD_COMPLETED")  # Add marker here too
            except Exception as e:
                safe_print_error("clip_upload failed", e)
                print("Trying video_upload method...")
                # Second attempt with video_upload (for regular videos)
                try:
                    client.video_upload(
                        path=video_path,
                        caption=full_caption
                    )
                    upload_success = True
                    print("Video uploaded successfully!")
                    print("STEP_MARKER: UPLOAD_COMPLETED")  # Add marker here too
                except Exception as inner_e:
                    safe_print_error("video_upload also failed", inner_e)
                    raise inner_e
        except Exception as e:
            safe_print_error("Upload failed", e)
            print("STEP_MARKER: UPLOAD_FAILED")
            
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
            # Make sure to leave the process in a failed state
            return False
    except Exception as e:
        safe_print_error("Unexpected error during repost process", e)
        print("STEP_MARKER: UPLOAD_FAILED")
        return False
    finally:
        # Check if upload was successful and mark accordingly
        if upload_success:
            # Ensure this marker is printed for the backend to detect
            print("STEP_MARKER: UPLOAD_COMPLETED")
            print("Upload completed successfully!")
            success = True
        
        # Clean up
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"Deleted temp file: {video_path}")
            except Exception:
                pass
        
        # Final status message for the backend to detect
        if success:
            print("FINAL_STATUS: SUCCESS")
        else:
            print("FINAL_STATUS: FAILED")
    
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
    # Configure sys.stdout to handle Unicode characters properly
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    parser = argparse.ArgumentParser(description='Repost Videos to Instagram')
    parser.add_argument('url', help='Instagram reel or YouTube shorts URL to repost')
    parser.add_argument('--caption', help='Custom caption for the repost')
    parser.add_argument('--hashtags', help='Custom hashtags for the repost')
    parser.add_argument('--source', help='Source platform (instagram or youtube)', default='instagram')
    
    args = parser.parse_args()
    
    # Print arguments safely without encoding issues
    try:
        print("Received arguments:")
        print(f"URL: {args.url}")
        print(f"Source: {args.source}")
        
        # Handle caption and hashtags more carefully
        if args.caption:
            print("Caption provided (content not shown to avoid encoding issues)")
        if args.hashtags:
            print("Hashtags provided (content not shown to avoid encoding issues)")
    except Exception as e:
        safe_print_error("Error printing arguments", e)
      
    if args.url:
        try:
            print("Starting video repost process...")
            success = repost_video(args.url, args.caption, args.hashtags, args.source)
            
            # Always output a clear status marker
            if success:
                print("STEP_MARKER: UPLOAD_COMPLETED")  # First to ensure it's not missed
                print("Upload successful!")
                print(format_api_result(True, f"{args.source.capitalize()} video uploaded successfully"))
                # Print it again in case the earlier ones are lost
                print("STEP_MARKER: UPLOAD_COMPLETED")
            else:
                print("STEP_MARKER: UPLOAD_FAILED")
                print("Upload failed!")
                print(format_api_result(False, f"Failed to upload {args.source} video"))
        except Exception as e:
            safe_print_error("Unexpected error", e)
            print("STEP_MARKER: UPLOAD_FAILED")  # Clear marker for failure
            print(format_api_result(False, "Error occurred during processing"))
    else:
        print(format_api_result(False, "Error: No video URL provided"))
