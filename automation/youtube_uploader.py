"""
YouTube Uploader - Automated video upload to YouTube
Requires one-time OAuth setup via Google Cloud Console

Setup Steps:
1. Go to console.cloud.google.com
2. Create project > Enable YouTube Data API v3
3. Create OAuth credentials (Desktop app)
4. Download credentials.json to this folder
5. Run: python youtube_uploader.py setup

After setup, upload with:
  python youtube_uploader.py upload path/to/video.mp4 "Title" "Description"
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Third-party libraries needed:
# pip install google-auth google-auth-oauthlib google-api-python-client

# Configuration
CWD = Path(__file__).parent.parent
CREDENTIALS_FILE = CWD / "youtube" / "credentials.json"
TOKEN_FILE = CWD / "youtube" / "token.json"
UPLOADS_DIR = CWD / "youtube" / "uploads"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """Authenticate and return YouTube API service"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError:
        print("\n[x] Missing dependencies!")
        print("    Run: pip install google-auth google-auth-oauthlib google-api-python-client")
        return None

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_FILE.read_text()),
            SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("\n[x] credentials.json not found!")
                print("    1. Go to console.cloud.google.com")
                print("    2. Create project > Enable YouTube Data API v3")
                print("    3. Credentials > Create OAuth Client ID > Desktop app")
                print("    4. Download JSON, rename to credentials.json")
                print("    5. Place in: " + str(CREDENTIALS_FILE))
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            TOKEN_FILE.write_text(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def setup_oauth():
    """Guide user through OAuth setup"""
    print("\n[*] YouTube OAuth Setup")
    print("=" * 40)
    print("\nStep 1: Create Google Cloud Project")
    print("  1. Go to: console.cloud.google.com")
    print("  2. Click 'Select Project' > 'New Project'")
    print("  3. Name it: 'MoneyMaker'")
    print("  4. Wait for project creation")

    print("\nStep 2: Enable YouTube Data API")
    print("  1. In sidebar: 'APIs & Services' > 'Library'")
    print("  2. Search: 'YouTube Data API v3'")
    print("  3. Click it > 'Enable'")

    print("\nStep 3: Create OAuth Credentials")
    print("  1. 'APIs & Services' > 'Credentials'")
    print("  2. 'Create Credentials' > 'OAuth Client ID'")
    print("  3. Application type: 'Desktop app'")
    print("  4. Name it: 'YouTube Uploader'")
    print("  5. Download JSON")
    print("  6. Rename to 'credentials.json'")
    print("  7. Place here: " + str(CREDENTIALS_FILE))

    print("\nStep 4: Run authentication")
    print("  python youtube_uploader.py auth")

    print("\n" + "=" * 40)

def authenticate():
    """Run OAuth flow to get tokens"""
    print("\n[*] Starting authentication...")

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("\n[x] Install dependencies first:")
        print("    pip install google-auth google-auth-oauthlib google-api-python-client")
        return False

    if not CREDENTIALS_FILE.exists():
        print("\n[x] credentials.json not found!")
        setup_oauth()
        return False

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_FILE.parent.mkdir(exist_ok=True)
    TOKEN_FILE.write_text(creds.to_json())

    print("\n[+] Authentication successful!")
    print("    Token saved to: " + str(TOKEN_FILE))
    return True

def upload_video(video_path, title, description, tags=None, privacy="public"):
    """Upload video to YouTube"""
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError

    if not os.path.exists(video_path):
        print(f"\n[x] Video not found: {video_path}")
        return None

    youtube = get_authenticated_service()
    if not youtube:
        return None

    tags = tags or ["automation", "ai", "facts", "india"]
    body = {
        "snippet": {
            "title": title[:100],  # Max 100 chars
            "description": description[:5000],  # Max 5000 chars
            "tags": tags[:30],  # Max 30 tags
            "categoryId": "22",  # People & Blogs
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": privacy,  # public, private, unlisted
            "selfDeclaredMadeForKids": False
        },
        "recordingDetails": {
            "location": {"latitude": 10.85, "longitude": 76.27},  # Kerala
            "recordingDate": datetime.now().isoformat() + "Z"
        }
    }

    try:
        print(f"\n[*] Uploading: {title}")
        print(f"    File: {video_path}")

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status,recordingDetails",
            body=body,
            media_body=media
        )

        # Progress callback
        def progress_callback(chunk, bytes_so_far):
            pct = (bytes_so_far * 100) // os.path.getsize(video_path)
            print(f"\r    Progress: {pct}%", end="", flush=True)

        response = None
        while response is None:
            status, response = request.next_chunk(event_callback=progress_callback)

        print("\n\n[+] Upload complete!")
        print(f"    Video ID: {response['id']}")
        print(f"    URL: https://www.youtube.com/watch?v={response['id']}")
        return response['id']

    except HttpError as e:
        print(f"\n[x] YouTube API error: {e}")
        return None
    except Exception as e:
        print(f"\n[x] Upload failed: {e}")
        return None

def upload_folder():
    """Upload all videos in uploads folder"""
    if not UPLOADS_DIR.exists():
        print(f"\n[x] Uploads folder not found: {UPLOADS_DIR}")
        return

    videos = list(UPLOADS_DIR.glob("*.mp4"))
    if not videos:
        print("\n[x] No videos found in uploads folder")
        return

    print(f"\n[*] Found {len(videos)} videos to upload\n")

    for i, video in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] Processing: {video.name}")

        # Extract title from filename
        title = video.stem.replace("-", " ").replace("_", " ").title()

        # Default description
        description = f"""Video generated with AI automation.

#shorts #ai #automation #india #facts

---
Uploaded automatically via Money Maker system."""

        tags = ["automation", "ai", "facts", "india", "kerala"]

        video_id = upload_video(str(video), title, description, tags)

        if video_id:
            # Move to uploaded folder
            uploaded_dir = UPLOADS_DIR / "uploaded"
            uploaded_dir.mkdir(exist_ok=True)
            video.rename(uploaded_dir / video.name)

        print()

def show_help():
    print("""
YouTube Uploader - Automated Video Upload
========================================

Commands:
  setup          - Show OAuth setup instructions
  auth           - Run OAuth authentication
  upload [file] [title] [desc] - Upload single video
  folder         - Upload all videos in uploads folder

Examples:
  python youtube_uploader.py setup
  python youtube_uploader.py auth
  python youtube_uploader.py upload "video.mp4" "My Video Title" "Description here"
  python youtube_uploader.py folder

First-time setup:
  1. python youtube_uploader.py setup
  2. Follow instructions to get credentials.json
  3. python youtube_uploader.py auth
  4. Done! Now uploads are automatic

Requires:
  pip install google-auth google-auth-oauthlib google-api-python-client
""")

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "help":
        show_help()
        sys.exit()

    cmd = args[0]

    if cmd == "setup":
        setup_oauth()

    elif cmd == "auth":
        if authenticate():
            print("\n[+] You can now upload videos automatically!")

    elif cmd == "upload":
        if len(args) < 4:
            print("\nUsage: python youtube_uploader.py upload [file] [title] [description]")
        else:
            upload_video(args[1], args[2], args[3])

    elif cmd == "folder":
        upload_folder()

    else:
        show_help()