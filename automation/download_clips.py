"""
Download sample clips for testing
Uses Pexels free API (get key from pexels.com/api)
Or uses Pixabay free videos
"""

import os
import requests
from pathlib import Path

CLIPS_DIR = Path(__file__).parent.parent / "youtube" / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

# Sample searches for diverse content
SAMPLE_SEARCHES = [
    "nature", "city", "ocean", "mountains", "forest",
    "sunset", "clouds", "waterfall", "beach", "sky",
    "road", "train", "travel", "food", "culture"
]

def download_from_pixabay(query):
    """Download free video from Pixabay (no API key needed for search)"""
    # Pixabay API - free with attribution
    url = f"https://pixabay.com/api/videos/?key=47895777-cd4f4f8f91e37f8c69e01b4bb&q={query}&video_type=film&per_page=3"

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            if hits:
                video = hits[0]
                # Get HD video URL
                for v in video.get("videos", {}).values():
                    if v and isinstance(v, dict) and v.get("url"):
                        return v["url"]
    except Exception as e:
        print(f"Pixabay error: {e}")
    return None

def download_from_pexels(query, api_key):
    """Download free video from Pexels (requires API key)"""
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": 3, "orientation": "portrait"}

    try:
        response = requests.get("https://api.pexels.com/videos/search",
                              headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            videos = response.json().get("videos", [])
            if videos:
                # Get smallest HD video
                for video in videos:
                    for file in video.get("video_files", []):
                        if file.get("quality") == "hd" and file.get("width", 0) >= 720:
                            return file.get("link")
    except Exception as e:
        print(f"Pexels error: {e}")
    return None

def download_clip(url, filename):
    """Download video clip to file"""
    try:
        print(f"  Downloading: {filename}")
        response = requests.get(url, timeout=60, stream=True)
        if response.status_code == 200:
            path = CLIPS_DIR / filename
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"  Saved: {path}")
            return True
    except Exception as e:
        print(f"  Failed: {e}")
    return False

def main():
    print("\n" + "=" * 50)
    print("CLIP DOWNLOADER - Free Stock Videos")
    print("=" * 50)

    # Check for API keys
    pexels_key = os.environ.get("PEXELS_API_KEY")
    use_pexels = bool(pexels_key)

    if use_pexels:
        print("\n[*] Using Pexels API")
    else:
        print("\n[*] Using Pixabay (no API key needed)")

    print(f"[*] Saving to: {CLIPS_DIR}")

    # Download sample clips
    print("\n[*] Downloading sample clips...\n")

    for i, search in enumerate(SAMPLE_SEARCHES[:10], 1):
        print(f"[{i}/10] {search}...")

        url = None
        if use_pexels:
            url = download_from_pexels(search, pexels_key)
        else:
            url = download_from_pixabay(search)

        if url:
            filename = f"{search}-{int(__import__('time').time())}.mp4"
            download_clip(url, filename)
        else:
            print(f"  No video found for: {search}")

        print()

    print("=" * 50)
    print("[+] Done! Check the clips folder.")
    print("\nTo get better clips:")
    print("1. Get free Pexels API key: pexels.com/api")
    print("2. Set: export PEXELS_API_KEY=your_key")
    print("3. Run this script again")

if __name__ == "__main__":
    main()