import sys
print("---- Python sys.path ----")
for p in sys.path:
    print(p)
print("-------------------------")

print("Attempting to import moviepy directly...")
try:
    import moviepy
    print(f"Successfully imported moviepy, version: {moviepy.__version__}")
except ImportError as e:
    print(f"Failed to import moviepy directly: {e}")
    print("This means the script itself cannot find moviepy in the Python environment.")
except Exception as e:
    print(f"An unexpected error occurred during moviepy import: {e}")
print("-------------------------")
import os
import time
import sys
from instagrapi import Client
import yt_dlp

# Ensure moviepy is imported properly
try:
    import moviepy
    import moviepy.editor
    print(f"Successfully imported moviepy and moviepy.editor, version: {moviepy.__version__}")
except ImportError as e:
    print(f"Failed to import moviepy or moviepy.editor: {e}")
    print("Try reinstalling: pip install moviepy==1.0.3")
except Exception as e:
    print(f"An unexpected error occurred during moviepy import: {e}")

# --- Configuration ---
# REQUIRED: Replace with your Instagram username and password
INSTAGRAM_USERNAME = "dantesclipz"
INSTAGRAM_PASSWORD = "DantesisBest101"

FIXED_CAPTION = "Thanks for watching, hit follow for more! 🙏"
FIXED_HASHTAGS = "#reels #instareels #trending #viral #foryou #fyp #repost" # Add your set hashtags
DOWNLOAD_FOLDER = "downloaded_reels" # A subfolder will be created here

# --- Helper Functions ---
def merge_video_audio(video_file, audio_file, output_file):
    """Merges separate video and audio files using moviepy."""
    try:
        print(f"Merging video {video_file} and audio {audio_file} into {output_file}...")
        video_clip = moviepy.editor.VideoFileClip(video_file)
        audio_clip = moviepy.editor.AudioFileClip(audio_file)
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        video_clip.close()
        audio_clip.close()
        print(f"Successfully merged into {output_file}")
        return output_file
    except Exception as e:
        print(f"Error merging video and audio: {e}")
        return None

def check_for_separate_files(reel_id, download_path):
    """Check if there are separate video and audio files that need to be merged."""
    video_file = None
    audio_file = None
    
    for file in os.listdir(download_path):
        if reel_id in file:
            if file.endswith('.mp4') or 'video' in file:
                video_file = os.path.join(download_path, file)
            elif file.endswith('.m4a') or 'audio' in file:
                audio_file = os.path.join(download_path, file)
    
    if video_file and audio_file:
        print(f"Found separate video ({video_file}) and audio ({audio_file}) files")
        merged_file = os.path.join(download_path, f"{reel_id}_merged.mp4")
        return merge_video_audio(video_file, audio_file, merged_file)
    
    return None

def download_reel(reel_url, download_path):
    """Downloads a reel using yt-dlp, attempting to find pre-merged formats."""
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    output_template = os.path.join(download_path, '%(id)s.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_template,
        # Attempt to get a pre-merged mp4. This prioritizes formats that are already MP4
        # and ideally don't require merging by ffmpeg.
        # 'best[ext=mp4]' tries to get the best quality single file that is an MP4.
        # '/best' is a fallback if no MP4 is directly available.
        'format': 'best[ext=mp4]/best', 
        'quiet': False, 
        'verbose': True, # Keep verbose true to see what yt-dlp is doing
        'ignoreerrors': False,
        # We are intentionally NOT specifying ffmpeg_location or merge_output_format
        # to see if yt-dlp can manage without explicit ffmpeg intervention.
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"yt-dlp attempting to download with options: {ydl_opts}")
            info = ydl.extract_info(reel_url, download=True) # download=True is important
            
            downloaded_file = None
            # yt-dlp version 2023.03.04+ stores filepath in requested_downloads
            if info.get('requested_downloads') and len(info['requested_downloads']) > 0:
                downloaded_file = info['requested_downloads'][0].get('filepath')
            
            # Fallback for older versions or if the above path doesn't yield the file
            if not downloaded_file or not os.path.exists(downloaded_file):
                # Try to construct filename based on info if possible
                # This is less reliable than 'requested_downloads'
                ext = info.get('ext', 'mp4') # Default to mp4 if extension not found
                id_ = info.get('id', 'unknown_id')
                downloaded_file = os.path.join(download_path, f"{id_}.{ext}")

            if downloaded_file and os.path.exists(downloaded_file):
                print(f"Downloaded: {downloaded_file}")
                return downloaded_file
            else:
                print(f"yt-dlp finished, but the expected file was not found at: {downloaded_file if downloaded_file else 'path not determined'}")
                print("Check verbose output. If it mentions merging or separate video/audio streams, ffmpeg is likely needed for this specific reel.")
                # Attempt to find *any* .mp4 file that might have been downloaded if the name doesn't match
                for f_name in os.listdir(download_path):
                    if info.get('id') in f_name and f_name.endswith('.mp4'):
                        potential_file = os.path.join(download_path, f_name)
                        print(f"Found a potential downloaded file: {potential_file}")
                        return potential_file
                return None

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp DownloadError: {e}")
        if "ffmpeg" in str(e).lower():
            print("This error likely means ffmpeg is required for this video format and was not found.")
        return None
    except Exception as e:
        print(f"General error during downloading reel: {e}")
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
            
# --- Main Agent Logic ---
def repost_reel_agent(reel_link_to_repost):
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    print(f"Attempting to download: {reel_link_to_repost}")
    video_path = download_reel(reel_link_to_repost, DOWNLOAD_FOLDER)

    # Extract the reel_id from the URL
    reel_id = None
    if "instagram.com/reel/" in reel_link_to_repost:
        reel_id = reel_link_to_repost.split("/reel/")[1].split("/")[0].split("?")[0]
    elif "instagram.com/p/" in reel_link_to_repost:
        reel_id = reel_link_to_repost.split("/p/")[1].split("/")[0].split("?")[0]
    
    # Check if we have separate files to merge
    if reel_id:
        merged_path = check_for_separate_files(reel_id, DOWNLOAD_FOLDER)
        if merged_path and os.path.exists(merged_path):
            video_path = merged_path
            print(f"Using merged video file: {video_path}")
    
    if not video_path or not os.path.exists(video_path):
        print("Failed to download or merge video. Exiting.")
        return

    print("Logging into Instagram...")
    client = login_to_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    if not client:
        print("Failed to log in to Instagram. Exiting.")
        if os.path.exists(video_path):
            os.remove(video_path)
        return

    # Verify that moviepy is correctly installed before uploading
    try:
        import moviepy
        import moviepy.editor
        print(f"Verified moviepy installation before upload: {moviepy.__version__}")
    except ImportError:
        print("Error: moviepy not properly installed. Please run: pip install moviepy==1.0.3")
        return

    full_caption = f"{FIXED_CAPTION}\n\n{FIXED_HASHTAGS}"
    print(f"Uploading {video_path} with caption: \n{full_caption}")

    try:
        # First try clip_upload which is for Reels
        try:
            print("Attempting to upload as a Reel (clip_upload)...")
            client.clip_upload(
                path=video_path,
                caption=full_caption
            )
            print("Reel uploaded successfully!")
        except Exception as e:
            print(f"clip_upload failed: {e}")
            print("Trying alternative video_upload method...")
            client.video_upload(
                path=video_path,
                caption=full_caption
            )
            print("Video uploaded successfully!")

    except Exception as e:
        print(f"Error uploading reel: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Cleaned up {video_path}")

# --- How to run it ---
if __name__ == "__main__":
    if INSTAGRAM_USERNAME == "YOUR_INSTAGRAM_USERNAME" or INSTAGRAM_PASSWORD == "YOUR_INSTAGRAM_PASSWORD":
        print("IMPORTANT: Please update INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in the script.")
    else:
        reel_url_from_user = input("Enter the Instagram Reel URL to repost: ")
        if "instagram.com/reel/" not in reel_url_from_user and "instagram.com/p/" not in reel_url_from_user:
            print("Invalid Instagram Reel or Post URL.")
        else:
            repost_reel_agent(reel_url_from_user)
            print("Waiting for 60 seconds before next potential operation...")
            time.sleep(60)