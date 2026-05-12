"""
PROFESSIONAL YouTube Shorts Generator v3
- Multiple video clips per short (3-4 clips combined)
- Voiceover exactly timed to fit video duration
- Scripts optimized for 45-50 second shorts
- Uses Pexels for real video clips
- Fallback: Animated images if no clips available

Voiceover timing: ~150 words per minute = ~2.5 words per second
For 50 second video: ~125 words max
"""

import os
import sys
import json
import random
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CLIPS_DIR = BASE_DIR / "youtube" / "clips"
UPLOADS_DIR = BASE_DIR / "youtube" / "uploads"
TEMP_DIR = BASE_DIR / "youtube" / "temp"
SCRIPTS_DIR = BASE_DIR / "youtube" / "scripts"

for d in [CLIPS_DIR, UPLOADS_DIR, TEMP_DIR, SCRIPTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Channel name - CHANGE THIS
CHANNEL_NAME = "AutoTube"

# Optimized script templates for 45-50 second shorts
SHORT_SCRIPTS = {
    "facts": [
        {
            "topic": "The oldest living thing on Earth",
            "hook": "This tree is older than the pyramids.",
            "script": "Meet the oldest living thing on Earth. This ancient organism has survived for over 5,000 years. It witnessed the rise and fall of empires while remaining virtually unchanged. Scientists study it to understand how life can persist for millennia. Imagine what stories this silent witness could tell if it could speak.",
            "visual_prompts": ["ancient tree", "nature forest", "oak tree"]
        },
        {
            "topic": "Why cats can see in the dark",
            "hook": "Here's why cats see better than you in complete darkness.",
            "script": "Cats have superpowers at night. Their eyes contain a special layer called tapetum lucidum. This reflects light back through their retina, giving them a second chance to detect it. That's why their eyes glow in the dark. Plus, they have more rod cells than humans, making them perfect nighttime hunters.",
            "visual_prompts": ["cat eyes glowing", "cat in darkness", "cat night vision"]
        },
        {
            "topic": "The ocean contains more gold than all governments",
            "hook": "There's more gold in the ocean than all the gold ever mined.",
            "script": "Deep in our oceans lies a fortune beyond imagination. Scientists estimate there are billions of tons of gold dissolved in seawater. Yet it's so spread out that extracting it would cost more than the gold is worth. Every liter of ocean water contains about 13 billionths of a gram. The ocean's secret wealth remains just out of reach.",
            "visual_prompts": ["underwater gold", "ocean depth", "treasure underwater"]
        },
        {
            "topic": "A country where citizens never need to work",
            "hook": "This country pays citizens to do nothing.",
            "script": "Imagine getting money without working. In Alaska, every resident receives an annual dividend from oil revenues. This program, started in 1982, has continued every year since. It provides thousands of dollars to each citizen just for living there. The state believes sharing natural resources benefits everyone.",
            "visual_prompts": ["alaska landscape", "oil platform", "nature mountains"]
        }
    ],
    "kerala": [
        {
            "topic": "Why Kerala has no McDonald's",
            "hook": "The only Indian state without a McDonald's. Here's why.",
            "script": "Kerala stands alone as the only Indian state without a McDonald's. The reason? Kerala's vegetarian population and religious preferences make beef off the menu. McDonald's core products contain beef. Without their signature items, opening a restaurant becomes unviable. Cultural values trump corporate expansion here.",
            "visual_prompts": ["kerala food", "traditional dish", "indian cuisine Kerala"]
        },
        {
            "topic": "The ancient martial art that inspired all others",
            "hook": "This 3,000 year old martial art inspired every action movie.",
            "script": "Kalaripayattu is the mother of all martial arts. Born in Kerala over 3,000 years ago, it combines combat techniques with spiritual practice. Legends say Buddha himself learned from Kerala masters. Bruce Lee studied its principles. Today, it remains alive in Kerala's traditional training centers, keeping ancient wisdom alive.",
            "visual_prompts": ["martial arts pose", "kerala warrior", "traditional combat"]
        },
        {
            "topic": "How Kerala became 100% literate first",
            "hook": "This Indian state achieved 100% literacy before anyone else.",
            "script": "In 1991, Kerala became the first fully literate state in India. The secret? Strong government commitment to education. Even poor families prioritized schooling. Temples became schools. Community groups promoted reading. Today, literacy here exceeds many developed nations. Education became a cultural value, not just a policy.",
            "visual_prompts": ["kerala classroom", "books education", "traditional school"]
        },
        {
            "topic": "The spice that built Kerala's fortune",
            "hook": "This spice made Kerala one of the richest places on Earth.",
            "script": "Pepper built Kerala's ancient wealth. For centuries, it was worth more than gold in Europe. Kings fought wars to control Kerala's pepper trade. The state's monsoons and fertile soil created perfect growing conditions. Even today, Kerala remains one of the world's largest pepper producers. This humble spice shaped global history.",
            "visual_prompts": ["pepper spice", "kerala market", "black pepper harvest"]
        }
    ],
    "travel": [
        {
            "topic": "The most dangerous road on Earth",
            "hook": "This road has killed over 300 people in one year alone.",
            "script": "In Pakistan, the Karakoram Highway passes through territory that defies imagination. Narrow passages carved into cliffs. No guardrails. Sheer drops of thousands of meters. Fog appears without warning. Landslides are common. Yet thousands drive here yearly, drawn by the ultimate test of courage. This is not for the faint of heart.",
            "visual_prompts": ["mountain road dangerous", "cliff road", "highway mountain"]
        },
        {
            "topic": "The island where animals outnumber humans 100 to 1",
            "hook": "On this island, animals outnumber humans by 100 to 1.",
            "script": "Botswana's Savute island hosts one of Earth's last great wildlife spectacles. Lions, zebras, and elephants roam freely. Humans are visitors, not rulers. The region exists in near-pristine condition. Predators hunt using ancient techniques. Nature here operates by its own rules. It's a glimpse of what our planet looked like before human dominance.",
            "visual_prompts": ["safari animals", "elephant africa", "lion wildlife"]
        },
        {
            "topic": "The beach with pink sand you've never seen",
            "hook": "This beach has pink sand and most people don't know it exists.",
            "script": "On the island of Bonaire in the Caribbean, pink sand meets turquoise water. The color comes from crushed coral mixed with white sand. The effect is dreamlike, almost artificial. Yet it's completely natural. This hidden paradise remains uncrowded despite its beauty. Sometimes the best places are the ones nobody knows about.",
            "visual_prompts": ["pink beach caribbean", "tropical beach", "pink sand ocean"]
        }
    ],
    "quotes": [
        {
            "topic": "The 5 AM habit of successful people",
            "hook": "Every successful person shares one morning habit.",
            "script": "Winners wake up before the world starts moving. At 5 AM, distractions are zero. The mind is fresh. Energy is high. This quiet hour becomes a competitive advantage. While others sleep, winners prepare. They read, exercise, plan, and think. By the time others rise, winners have already begun winning the day.",
            "visual_prompts": ["sunrise morning", "person productive", "morning routine"]
        },
        {
            "topic": "Why consistency beats talent every time",
            "hook": "Talent will fail you. Consistency will not.",
            "script": "Every expert was once a beginner. What separates winners from quitters is simple: they showed up every single day. Talent gives you a head start. But consistency finishes the race. The person who practices daily beats the genius who practices occasionally. Your daily showing up is your unfair advantage.",
            "visual_prompts": ["athlete training", "practice consistently", "workout motivation"]
        },
        {
            "topic": "The one thing that separates winners from losers",
            "hook": "Winners and losers have the same opportunities. Here's the difference.",
            "script": "When faced with difficulty, losers make excuses. Winners find ways. The gap between success and failure isn't talent or luck. It's response. Your reaction to failure determines your future. Winners fail and adapt. Losers fail and quit. Success isn't about never falling. It's about getting up every time you fall.",
            "visual_prompts": ["success mindset", "overcoming obstacles", "mountain peak"]
        }
    ],
    "food": [
        {
            "topic": "The pizza invented to feed a poor family",
            "hook": "This pizza was created to help a poor family survive.",
            "script": "Margherita pizza was born in Naples during hard times. A queen visited a poor neighborhood. Nothing fancy was available. The cook made do with what existed: tomatoes, mozzarella, basil. The queen loved it. The humble dish became a symbol of Italian cuisine. Sometimes the simplest creations become the most enduring.",
            "visual_prompts": ["pizza making", "italian kitchen", "tomatoes ingredients"]
        },
        {
            "topic": "Why Indian food is the most diverse on Earth",
            "hook": "Indian food is the most diverse cuisine in the world. Here's why.",
            "script": "India has over 2000 distinct cuisines. Each region speaks a different language and eats different foods. The Himalayas, deserts, coastlines, and jungles all shape what's eaten. Spices here aren't just flavor. They preserve food in heat. Climate, culture, and history created this explosion of tastes. No other country matches this diversity.",
            "visual_prompts": ["indian spices", "variety food", "masala spices"]
        },
        {
            "topic": "The spice that was once worth more than gold",
            "hook": "This spice was once worth more than gold. You use it daily.",
            "script": "Black pepper once cost more than gold in ancient Rome. Emperors paid fortunes for tiny quantities. Kerala was the world's only source for centuries. Explorers sought new routes to find it. Wars were fought over pepper trade. Today it sits in every kitchen, forgotten and humble. But history remembers its true value.",
            "visual_prompts": ["black pepper spice", "pepper trade", "spice market"]
        }
    ]
}

# Target duration: 45-50 seconds
TARGET_DURATION = 48
WORDS_PER_SECOND = 2.5
MAX_WORDS = TARGET_DURATION * WORDS_PER_SECOND

def get_best_script():
    """Select and optimize a script for short format"""
    all_scripts = []
    for style, scripts in SHORT_SCRIPTS.items():
        for script in scripts:
            script["style"] = style
            all_scripts.append(script)

    selected = random.choice(all_scripts)

    # Count words and trim if needed
    words = selected["script"].split()
    if len(words) > MAX_WORDS:
        # Trim to fit timing
        selected["script"] = " ".join(words[:int(MAX_WORDS)])
        # Make sure it ends properly
        sentences = selected["script"].split(".")
        if len(sentences) > 2:
            selected["script"] = ".".join(sentences[:-1]) + "."

    full_text = f"{selected['hook']}. {selected['script']}"
    selected["full_text"] = full_text
    selected["estimated_duration"] = len(full_text.split()) / WORDS_PER_SECOND

    return selected

def download_video_clip(query, api_key):
    """Download video clip from Pexels"""
    if not api_key:
        return None

    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": 5,
        "orientation": "portrait",
        "size": "small"
    }

    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            videos = response.json().get("videos", [])
            if videos:
                # Get a video with good duration
                for video in random.sample(videos, min(3, len(videos))):
                    for file in video.get("video_files", []):
                        if file.get("width", 0) >= 720:
                            if 5 <= file.get("duration", 10) <= 30:
                                url = file.get("link")
                                output = TEMP_DIR / f"clip-{int(datetime.now().timestamp())}-{random.randint(100,999)}.mp4"

                                print(f"  Downloading: {query}")
                                r = requests.get(url, timeout=60, stream=True)
                                if r.status_code == 200:
                                    with open(output, "wb") as f:
                                        for chunk in r.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    if output.exists() and output.stat().st_size > 10000:
                                        return str(output)
    except Exception as e:
        print(f"  Pexels error: {e}")

    return None

def download_multiple_clips(script, api_key):
    """Download multiple clips for a single short"""
    clips = []
    queries = script.get("visual_prompts", ["nature", "abstract", "particles"])

    # Download 3-4 clips
    for query in queries[:4]:
        clip = download_video_clip(query, api_key)
        if clip:
            clips.append(clip)

    return clips

def create_video_from_clips(clips, audio_path, script):
    """Create video by combining multiple clips with audio"""
    output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    if not clips:
        # No clips - create animated fallback
        return create_animated_fallback(audio_path, script)

    # Calculate clip duration (divide total by number of clips)
    clip_count = len(clips)
    duration_per_clip = TARGET_DURATION / clip_count

    # Create concat file
    concat_file = TEMP_DIR / "concat.txt"

    # Get duration of each clip and create segments
    segments = []
    for clip in clips:
        segments.append(f"file '{clip}'\n")

    concat_file.write_text("".join(segments))

    # Get audio duration
    import subprocess
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
            capture_output=True, text=True
        )
        audio_duration = float(result.stdout.strip()) if result.stdout.strip() else TARGET_DURATION
    except:
        audio_duration = TARGET_DURATION

    # Concatenate clips
    concat_output = TEMP_DIR / "concat-video.mp4"
    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{concat_output}"'
    os.system(cmd)

    if not concat_output.exists():
        # Fallback to first clip
        concat_output = clips[0]

    # Now add text overlay and audio
    hook = script["hook"][:60].replace("'", "").replace(":", "")
    topic = script["topic"][:40].replace("'", "").replace(":", "")

    filter_str = f"""
    drawtext=text='{hook}':fontsize=32:fontcolor=white:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-280:enable='between(t,0,5)',
    drawtext=text='{topic}':fontsize=24:fontcolor=yellow@0.9:borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=80:enable='between(t,3,{TARGET_DURATION-3})'
    """

    cmd = f'''ffmpeg -y -i "{concat_output}" -i "{audio_path}" \
            -filter_complex "{filter_str}" \
            -map 0:v -map 1:a \
            -c:v libx264 -preset medium -crf 23 \
            -c:a aac -b:a 128k \
            -t {TARGET_DURATION} \
            -shortest \
            "{output}"'''

    os.system(cmd)

    if output.exists() and output.stat().st_size > 50000:
        return str(output)

    return None

def create_animated_fallback(audio_path, script):
    """Create animated visual when no clips available"""
    output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    hook = script["hook"][:60].replace("'", "").replace(":", "")
    topic = script["topic"][:40].replace("'", "").replace(":", "")

    colors = ["#1a1a2e", "#16213e", "#0f3460", "#533483", "#e94560"]
    color = random.choice(colors)

    filter_str = f"""
    drawtext=text='{hook}':fontsize=36:fontcolor=white:borderw=4:bordercolor=black@0.8:x=(w-text_w)/2:y=h-300:enable='between(t,0,5)',
    drawtext=text='{topic}':fontsize=28:fontcolor=yellow:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=100:enable='between(t,3,{TARGET_DURATION-3})'
    """

    cmd = f'''ffmpeg -y -f lavfi -i "color=c=0x{color[1:]}:s=1080x1920:d={TARGET_DURATION}:r=30" \
            -i "{audio_path}" \
            -filter_complex "{filter_str}" \
            -c:v libx264 -preset medium -crf 23 \
            -c:a aac -b:a 128k \
            -t {TARGET_DURATION} \
            -shortest \
            "{output}"'''

    os.system(cmd)

    return str(output) if output.exists() else None

def generate_voiceover(text):
    """Generate voiceover using gTTS (works without API keys)"""
    try:
        from gtts import gTTS

        output = TEMP_DIR / f"voice-{int(datetime.now().timestamp())}.mp3"

        # Add slight pause between sentences
        text_with_pauses = text.replace(". ", ". ")
        for _ in range(3):
            text_with_pauses = text_with_pauses.replace(".", "...").replace("...", ".", 1)

        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(str(output))

        print(f"  Voiceover generated ({len(text.split())} words)")
        return str(output)

    except Exception as e:
        print(f"  Voiceover error: {e}")
        return None

def upload_to_youtube(video_path, script):
    """Upload video to YouTube as Short"""
    try:
        import base64
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        TOKEN_FILE = BASE_DIR / "youtube" / "token.json"
        CREDENTIALS_FILE = BASE_DIR / "youtube" / "credentials.json"

        # Load from GitHub secrets
        if os.environ.get("GITHUB_ACTIONS"):
            token_b64 = os.environ.get("YOUTUBE_TOKEN_DATA", "")
            creds_b64 = os.environ.get("YOUTUBE_CLIENT_CONFIG", "")

            if token_b64:
                TOKEN_FILE.write_text(json.dumps(json.loads(base64.b64decode(token_b64).decode())))
            if creds_b64:
                CREDENTIALS_FILE.write_text(json.dumps(json.loads(base64.b64decode(creds_b64).decode())))

        if not CREDENTIALS_FILE.exists():
            print("  [x] No credentials")
            return None

        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_FILE.read_text()),
            ["https://www.googleapis.com/auth/youtube.upload"]
        )

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": f"[SHORT] {script['topic'][:80]}",
                "description": f"""🎯 {script['topic']}

Follow for daily content that expands your knowledge!

#shorts #{script['style']} #india #facts #knowledge

📺 {CHANNEL_NAME} - Your daily dose of interesting facts

🔔 Subscribe for more!""",
                "tags": ["shorts", script["style"], "facts", "india", "knowledge", CHANNEL_NAME.lower()],
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

        print("  Uploading...")
        response = None
        while response is None:
            status, response = request.next_chunk()

        video_id = response['id']
        print(f"  [+] Done! https://www.youtube.com/shorts/{video_id}")
        return video_id

    except Exception as e:
        print(f"  [x] Upload failed: {e}")
        return None

def run_daily():
    """Run full pipeline"""
    print("\n" + "=" * 60)
    print(f"{CHANNEL_NAME} - YOUTUBE SHORTS GENERATOR v3")
    print("=" * 60)

    try:
        # 1. Get optimized script
        print("\n[1/5] Creating optimized script...")
        script = get_best_script()
        print(f"  Topic: {script['topic']}")
        print(f"  Words: {len(script['full_text'].split())}")
        print(f"  Est. duration: {script['estimated_duration']:.0f}s")

        # 2. Download video clips
        print("\n[2/5] Downloading video clips...")
        PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
        clips = download_multiple_clips(script, PEXELS_KEY)

        if clips:
            print(f"  Got {len(clips)} video clips")
        else:
            print("  No clips (will use animated fallback)")

        # 3. Generate voiceover
        print("\n[3/5] Creating voiceover...")
        audio = generate_voiceover(script["full_text"])

        if not audio:
            raise Exception("Voiceover failed")

        # 4. Create final video
        print("\n[4/5] Building video...")
        video = create_video_from_clips(clips, audio, script)

        if not video:
            raise Exception("Video creation failed")

        print(f"  Video: {os.path.basename(video)}")

        # 5. Upload
        print("\n[5/5] Uploading to YouTube...")
        video_id = upload_to_youtube(video, script)

        # Log
        log_file = BASE_DIR / "youtube" / "upload-log.json"
        log = json.loads(log_file.read_text()) if log_file.exists() else []
        log.append({
            "date": datetime.now().isoformat(),
            "topic": script["topic"],
            "style": script["style"],
            "video_id": video_id
        })
        log_file.write_text(json.dumps(log, indent=2))

        print("\n" + "=" * 60)
        print("[+] SHORT CREATED AND UPLOADED!")
        if video_id:
            print(f"    https://www.youtube.com/shorts/{video_id}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[x] Error: {e}")
    finally:
        # Cleanup
        for f in TEMP_DIR.glob("*"):
            if f.is_file():
                try:
                    f.unlink()
                except:
                    pass

def test_script():
    """Test script generation"""
    script = get_best_script()
    print(f"Topic: {script['topic']}")
    print(f"Hook: {script['hook']}")
    print(f"Script: {script['script']}")
    print(f"Words: {len(script['full_text'].split())}")
    print(f"Est. duration: {script['estimated_duration']:.0f}s")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "test" in args:
        test_script()
    else:
        run_daily()