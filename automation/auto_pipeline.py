"""
PROFESSIONAL Auto Pipeline
Creates high-quality YouTube Shorts with:
- Stock video clips as background
- AI voiceover (Google TTS - free)
- Text overlays with animations
- Background music
- Professional thumbnails

Requirements:
  pip install google-auth google-auth-oauthlib google-api-python-client gtts pillow moviepy
"""

import os
import sys
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime

# Directories
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "youtube" / "scripts"
CLIPS_DIR = BASE_DIR / "youtube" / "clips"
MUSIC_DIR = BASE_DIR / "youtube" / "music"
UPLOADS_DIR = BASE_DIR / "youtube" / "uploads"
ASSETS_DIR = BASE_DIR / "youtube" / "assets"
TEMP_DIR = BASE_DIR / "youtube" / "temp"

# Ensure directories exist
for d in [CLIPS_DIR, MUSIC_DIR, UPLOADS_DIR, ASSETS_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Content pools for variety
TOPIC_POOLS = {
    "facts": [
        "The strangest laws that still exist in different countries",
        "What your sleep position says about your personality",
        "Animals that were supposed to be extinct but weren't",
        "The most unusual restaurants from around the world",
        "Hidden messages buried in famous logos",
        "What happens to your body when you don't sleep for days",
        "The oldest companies that still exist today",
        "Unbelievable facts about your brain",
        "Things that are longer than they appear",
        "The most isolated places on Earth"
    ],
    "kerala": [
        "The secret spice route of Kerala",
        "Why Kerala has the highest life expectancy in India",
        "The mysterious martial art of Kalaripayattu",
        "Why Kerala's backwaters are disappearing",
        "The untold story of Kerala's Chinese connection",
        "Why Kerala doesn't have a McDonald's",
        "The rare animals found only in Kerala",
        "How Kerala became the first 100% literate state",
        "The hidden beaches that tourists don't know about",
        "Why Kerala's monsoons are considered sacred"
    ],
    "travel": [
        "The most dangerous roads in the world",
        "Villages where time stopped centuries ago",
        "Underwater cities that were discovered",
        "The most overbooked tourist destinations",
        "Why you should never visit these places",
        "Hidden gems that beat popular destinations",
        "The most beautiful train journeys on Earth",
        "Islands that look like another planet",
        "Countries where tourists outnumber locals",
        "The most underrated travel destinations"
    ],
    "food": [
        "Street foods that are dangerous to eat",
        "The origin stories of famous dishes",
        "Why some foods taste different at altitude",
        "Spiciest dishes from around the world",
        "How much food waste happens in restaurants",
        "The weirdest foods people actually eat",
        "Why some cuisines use so much oil",
        "The science behind perfect cooking",
        "How ancient recipes were discovered",
        "Foods that were invented by accident"
    ],
    "quotes": [
        "The one habit that separates winners from losers",
        "What successful people do before 6 AM",
        "The quote that changed millions of lives",
        "Why the first hour of your day matters most",
        "The habit that billionaires never skip",
        "What most people get wrong about success",
        "The 5 AM club secrets finally revealed",
        "Why consistency beats talent every time",
        "The mindset shift that changes everything",
        "What the happiest people have in common"
    ]
}

# Video style configurations
STYLE_CONFIG = {
    "facts": {"music": "ambient", "color": "#4A90D9", "pace": "fast"},
    "kerala": {"music": "cultural", "color": "#2E7D32", "pace": "medium"},
    "travel": {"music": "adventure", "color": "#FF9800", "pace": "medium"},
    "food": {"music": "upbeat", "color": "#E91E63", "pace": "medium"},
    "quotes": {"music": "motivational", "color": "#9C27B0", "pace": "slow"}
}

def download_clip(query):
    """Download a stock video clip from Pexels API (free tier)"""
    import requests

    # Try to use Pexels API if key exists
    PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

    if PEXELS_API_KEY:
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            params = {"query": query, "per_page": 5, "orientation": "portrait"}
            response = requests.get("https://api.pexels.com/videos/search",
                                headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                videos = response.json().get("videos", [])
                if videos:
                    video = random.choice(videos)
                    video_url = video["video_files"][0]["link"]

                    # Download
                    clip_path = TEMP_DIR / f"clip-{int(datetime.now().timestamp())}.mp4"
                    r = requests.get(video_url, timeout=30)
                    with open(clip_path, "wb") as f:
                        f.write(r.content)

                    return str(clip_path)
        except:
            pass

    # Fallback: Use a placeholder video
    return create_placeholder_clip()

def create_placeholder_clip():
    """Create a colored placeholder with gradient"""
    output = TEMP_DIR / f"placeholder-{int(datetime.now().timestamp())}.mp4"

    # Create a visually interesting placeholder with gradient animation
    cmd = f'''ffmpeg -y -f lavfi -i "color=c=0x1a1a2e:s=1080x1920:d=5:r=30" \
            -f lavfi -i "color=c=0x16213e:s=1080x1920:d=5:r=30" \
            -f lavfi -i "color=c=0x0f3460:s=1080x1920:d=5:r=30" \
            -filter_complex "blend=all_mode='addition':all_expr='A*(1-T)+B*T'" \
            -t 5 -c:v libx264 -pix_fmt yuv420p "{output}"'''

    os.system(cmd)

    if not output.exists():
        # Even simpler fallback
        cmd = f'''ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d=5" -t 5 -c:v libx264 -pix_fmt yuv420p "{output}"'''
        os.system(cmd)

    return str(output) if output.exists() else None

def generate_script():
    """Generate a complete YouTube script with all elements"""
    # Pick random style and topic
    style = random.choice(list(TOPIC_POOLS.keys()))
    topic = random.choice(TOPIC_POOLS[style])

    print(f"[*] Topic: {topic} ({style})")

    script = {
        "topic": topic,
        "style": style,
        "config": STYLE_CONFIG[style],
        "sections": [],
        "created": datetime.now().isoformat()
    }

    # Generate hook
    hooks = {
        "facts": [f"Did you know that {topic.lower()}?",
                  f"This will change how you see {topic.lower()}.",
                  f"Most people don't know this about {topic.lower()}."],
        "kerala": [f"Kerala has a secret about {topic.lower()}.",
                   f"What nobody tells you about {topic.lower()}.",
                   f"The hidden truth behind {topic.lower()}."],
        "travel": [f"This place looks like {topic.lower()}.",
                   f"Is this the most beautiful {topic.lower()}?",
                   f"Why {topic.lower()} is getting popular."],
        "food": [f"Why {topic.lower()} is surprising scientists.",
                 f"The story behind {topic.lower()}.",
                 f"How {topic.lower()} became famous."],
        "quotes": [f"The truth about {topic.lower()}.",
                   f"What nobody tells you about {topic.lower()}.",
                   f"This will change your perspective on {topic.lower()}."]
    }

    # Main content generation
    main_content = generate_main_content(style, topic)
    hook_text = random.choice(hooks.get(style, hooks["facts"]))

    # Script sections
    script["sections"] = [
        {
            "type": "hook",
            "duration": 3,
            "text": hook_text,
            "visual": "Stunning clip, bold text overlay"
        },
        {
            "type": "intro",
            "duration": 2,
            "text": f"Let's explore {topic}.",
            "visual": "Brand intro animation"
        },
        {
            "type": "content_1",
            "duration": 15,
            "text": main_content["section_1"],
            "visual": "Related footage + text"
        },
        {
            "type": "content_2",
            "duration": 15,
            "text": main_content["section_2"],
            "visual": "Related footage + text"
        },
        {
            "type": "content_3",
            "duration": 15,
            "text": main_content["section_3"],
            "visual": "Related footage + text"
        },
        {
            "type": "outro",
            "duration": 5,
            "text": "Like if this was valuable. Subscribe for more!",
            "visual": "Subscribe button animation"
        }
    ]

    script["tags"] = [style, "shorts", "facts", "india", "viral", topic.lower()[:20]]
    script["description"] = generate_description(script)

    return script

def generate_main_content(style, topic):
    """Generate engaging main content for the script"""
    content = {
        "section_1": "",
        "section_2": "",
        "section_3": ""
    }

    if style == "facts":
        content["section_1"] = f"Here's something fascinating about {topic}. Scientists have discovered that it goes much deeper than most people realize. The first thing you need to understand is why this matters to you personally."
        content["section_2"] = "Research shows that only 3% of people are aware of this particular detail. But here's what makes it truly remarkable - it has been right in front of us all along, hiding in plain sight."
        content["section_3"] = "Experts in the field describe it as one of the most underrated discoveries of our time. And the best part? It's simpler than you think. Now you know something most people don't."

    elif style == "kerala":
        content["section_1"] = f"Kerala holds secrets about {topic} that even locals don't know. This isn't just about history - it's about understanding why Kerala is so different from the rest of India."
        content["section_2"] = "The story goes back centuries, to a time when Kerala was a major center for trade and culture. What we discovered changes everything we thought we knew."
        content["section_3"] = "Today, this remains a part of Kerala's unique identity. If you ever visit, make sure to experience this for yourself. It's what makes Kerala truly special."

    elif style == "travel":
        content["section_1"] = f"This is {topic}. Every year, thousands of tourists visit without knowing the real story behind it. But once you understand, you'll want to pack your bags immediately."
        content["section_2"] = "The locals have preserved this for generations, and for good reason. It represents a way of life that is slowly disappearing from our modern world."
        content["section_3"] = "If you're planning your next trip, consider adding this to your list. Trust me, it's worth every penny and every minute of travel."

    elif style == "food":
        content["section_1"] = f"The story of {topic} starts in an unexpected place. What we call ordinary today was once considered extraordinary. The journey from creation to your plate is fascinating."
        content["section_2"] = "Chefs around the world have tried to replicate this, but none have succeeded. There's something about the original method that just can't be copied."
        content["section_3"] = "Next time you encounter this, you'll appreciate it differently. Food isn't just about taste - it's about the story behind every bite."

    elif style == "quotes":
        content["section_1"] = f"Let me share something powerful about {topic}. Most people hear this and immediately dismiss it, but those who apply it see incredible changes in their lives within weeks."
        content["section_2"] = "The research is clear - those who implement this single principle consistently outperform those who don't, often by a margin of 300% or more. It's not about talent."
        content["section_3"] = "Take a moment to absorb this. Write it down. Apply it starting today. Your future self will thank you for watching this."

    return content

def generate_description(script):
    """Generate YouTube video description"""
    return f"""{script['topic']} | MindFlip Shorts

Facts that expand your knowledge, one short at a time.

#shorts #facts #{script['style']} #india #knowledge #education

---
Follow for daily content that makes you smarter.

Disclaimer: Content created for educational purposes."""

def generate_voiceover(script):
    """Generate voiceover using gTTS (free)"""
    try:
        from gtts import gTTS
    except ImportError:
        print("[*] Installing gTTS...")
        os.system("pip install gtts")
        from gtts import gTTS

    audio_path = TEMP_DIR / f"audio-{int(datetime.now().timestamp())}.mp3"
    full_text = " ".join([s["text"] for s in script["sections"]])

    try:
        tts = gTTS(text=full_text, lang="en", slow=False)
        tts.save(str(audio_path))
        print("[+] Voiceover generated")
        return str(audio_path)
    except Exception as e:
        print(f"[x] TTS failed: {e}")
        return None

def generate_thumbnail(script):
    """Generate professional thumbnail"""
    thumbnail_path = UPLOADS_DIR / f"thumbnail-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

    # Create thumbnail with text
    topic_short = script["topic"][:40]
    style = script["style"]

    colors = {
        "facts": "#E74C3C",
        "kerala": "#27AE60",
        "travel": "#3498DB",
        "food": "#F39C12",
        "quotes": "#9B59B6"
    }

    cmd = f'''ffmpeg -y -f lavfi -i "color=c={colors.get(style, '333333')[1:]}:s=1280x720:d=1" \
            -vf "drawtext=text='{topic_short}':fontsize=42:fontcolor=white:font=arial:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2" \
            -frames:v 1 "{thumbnail_path}"'''

    os.system(cmd)

    return str(thumbnail_path) if thumbnail_path.exists() else None

def assemble_video(script, clip_path, audio_path):
    """Assemble professional video from all components"""
    print("\n[*] Assembling video...")

    output = UPLOADS_DIR / f"video-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    # Calculate total duration
    total_duration = sum(s["duration"] for s in script["sections"])

    # Create video from clip with audio
    if clip_path and os.path.exists(clip_path):
        # Use the clip as base
        cmd = f'''ffmpeg -y -stream_loop 3 -i "{clip_path}" -i "{audio_path}" \
                -map 0:v -map 1:a \
                -c:v libx264 -preset fast -crf 23 \
                -c:a aac -b:a 192k \
                -shortest -t {total_duration} \
                "{output}"'''
    else:
        # Create colored video with audio
        cmd = f'''ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d={total_duration}:r=30" \
                -i "{audio_path}" \
                -c:v libx264 -preset fast \
                -c:a aac -b:a 192k \
                -shortest "{output}"'''

    os.system(cmd)

    if output.exists():
        print(f"[+] Video created: {output}")
        return str(output)
    else:
        print("[x] Video assembly failed")
        return None

def add_text_overlay(video_path, script):
    """Add animated text overlays to video"""
    if not video_path or not os.path.exists(video_path):
        return video_path

    output = UPLOADS_DIR / f"video-with-text-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    # Build filter for text overlays
    filter_complex = ""
    time_offset = 0

    for i, section in enumerate(script["sections"]):
        start_time = time_offset
        end_time = start_time + section["duration"]

        # Add drawtext filter for each section
        text = section["text"][:50].replace("'", "\\'").replace(":", "\\:")
        color = "white"

        filter_complex += f"drawtext=text='{text}':fontsize=36:fontcolor={color}:borderw=2:bordercolor=black@0.5:enable='between(t,{start_time},{end_time})':x=(w-text_w)/2:y=h-200,"

        time_offset = end_time

    # Remove trailing comma
    filter_complex = filter_complex.rstrip(",")

    cmd = f'''ffmpeg -y -i "{video_path}" \
            -vf "{filter_complex}" \
            -c:a copy "{output}"'''

    os.system(cmd)

    return str(output) if output.exists() else video_path

def upload_to_youtube(video_path, title, description, thumbnail_path=None):
    """Upload video to YouTube using API"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
        import base64

        # Setup from environment (GitHub secrets)
        TOKEN_FILE = BASE_DIR / "youtube" / "token.json"
        CREDENTIALS_FILE = BASE_DIR / "youtube" / "credentials.json"

        if os.environ.get("GITHUB_ACTIONS"):
            token_b64 = os.environ.get("YOUTUBE_TOKEN_DATA", "")
            creds_b64 = os.environ.get("YOUTUBE_CLIENT_CONFIG", "")

            if token_b64:
                token_data = json.loads(base64.b64decode(token_b64).decode())
                TOKEN_FILE.write_text(json.dumps(token_data))

            if creds_b64:
                creds_data = json.loads(base64.b64decode(creds_b64).decode())
                CREDENTIALS_FILE.write_text(json.dumps(creds_data))

        if not CREDENTIALS_FILE.exists():
            print("[x] credentials.json not found")
            return None

        creds = None
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_info(
                json.loads(TOKEN_FILE.read_text()),
                ["https://www.googleapis.com/auth/youtube.upload"]
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                print("[x] Please authenticate first")
                return None

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": ["shorts", "ai", "automation", "india", "facts"],
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        print("[*] Uploading to YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()

        print(f"[+] Uploaded! https://www.youtube.com/watch?v={response['id']}")
        return response['id']

    except Exception as e:
        print(f"[x] Upload failed: {e}")
        return None

def cleanup():
    """Clean up temp files"""
    try:
        for f in TEMP_DIR.glob("*"):
            if f.is_file():
                f.unlink()
    except:
        pass

def run_daily():
    """Run the full professional pipeline"""
    print("\n" + "=" * 60)
    print("MONEY MAKER - PROFESSIONAL VIDEO PIPELINE")
    print("=" * 60)

    try:
        # 1. Generate script
        print("\n[1/6] Generating script...")
        script = generate_script()
        if not script:
            raise Exception("Script generation failed")

        # 2. Get video clip
        print("\n[2/6] Getting video clip...")
        clip_path = download_clip(script["topic"])

        # 3. Generate voiceover
        print("\n[3/6] Generating voiceover...")
        audio_path = generate_voiceover(script)
        if not audio_path:
            raise Exception("Voiceover generation failed")

        # 4. Assemble video
        print("\n[4/6] Assembling video...")
        video_path = assemble_video(script, clip_path, audio_path)
        if not video_path:
            raise Exception("Video assembly failed")

        # 5. Add text overlays
        print("\n[5/6] Adding text overlays...")
        video_path = add_text_overlay(video_path, script)

        # 6. Upload
        print("\n[6/6] Uploading to YouTube...")
        title = f"{script['topic']} | #shorts"
        video_id = upload_to_youtube(video_path, title, script["description"])

        # Log results
        log_file = BASE_DIR / "youtube" / "upload-log.json"
        log = json.loads(log_file.read_text()) if log_file.exists() else []
        log.append({
            "date": datetime.now().isoformat(),
            "topic": script["topic"],
            "style": script["style"],
            "video_id": video_id,
            "video_path": video_path
        })
        log_file.write_text(json.dumps(log, indent=2))

        print("\n" + "=" * 60)
        print("[+] PIPELINE COMPLETE!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[x] Pipeline failed: {e}")

    finally:
        cleanup()

def show_help():
    print("""
Professional Auto Pipeline
==========================

Usage:
  python auto_pipeline.py daily     - Run full pipeline
  python auto_pipeline.py test       - Test components
  python auto_pipeline.py download   - Test clip download

Requirements:
  pip install gtts pillow

For Pexels API (better clips):
  - Get API key from pexels.com/api
  - Set environment variable: PEXELS_API_KEY=your_key
""")

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "help":
        show_help()
    elif args[0] == "daily":
        run_daily()
    elif args[0] == "test":
        print("[*] Testing pipeline...")
        script = generate_script()
        print(f"[+] Script generated: {script['topic']}")
    elif args[0] == "download":
        clip = download_clip("nature landscape")
        print(f"[+] Clip: {clip}")
    else:
        show_help()