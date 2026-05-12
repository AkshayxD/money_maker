"""
YouTube Shorts Generator v11 - OpenCode + Gemini AI Pipeline
- OpenCode API for script generation
- Gemini TTS for natural voice
- FFmpeg for video with Ken Burns
- Trending topics for maximum views
"""

import os
import sys
import json
import random
import subprocess
import requests
import asyncio
import wave
import struct
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "youtube" / "images"
UPLOADS_DIR = BASE_DIR / "youtube" / "uploads"
TEMP_DIR = BASE_DIR / "youtube" / "temp"

for d in [IMAGES_DIR, UPLOADS_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

CHANNEL_NAME = "MindFlip"

# OpenCode API endpoint (use your configured endpoint)
OPENCODE_API_URL = os.environ.get("OPENCODE_API_URL", "https://api.opencode.ai/v1/chat/completions")
OPENCODE_API_KEY = os.environ.get("OPENCODE_API_KEY", "")

# Gemini API for audio (free tier available)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def get_opencode_key():
    """Get OpenCode API key from environment"""
    if OPENCODE_API_KEY:
        return OPENCODE_API_KEY

    key_file = BASE_DIR / "youtube" / "opencode_key.txt"
    if key_file.exists():
        return key_file.read_text().strip()

    # Check for common env vars
    for var in ["OPENAI_API_KEY", "OPENROUTER_API_KEY", "API_KEY"]:
        val = os.environ.get(var, "")
        if val:
            return val

    return None

def get_gemini_key():
    """Get Gemini API key from environment"""
    if GEMINI_API_KEY:
        return GEMINI_API_KEY

    key_file = BASE_DIR / "youtube" / "gemini_key.txt"
    if key_file.exists():
        return key_file.read_text().strip()

    return None

def generate_script_with_opencode(topic, category):
    """Generate script using OpenCode API"""
    try:
        api_key = get_opencode_key()
        if not api_key:
            print("  No OpenCode key - using fallback script")
            return None

        system_prompt = """You are a YouTube Shorts script writer for viral content. Create engaging, fast-paced scripts.

Rules:
1. Start with a HOOK that creates curiosity (first sentence only)
2. 5-7 sentences total
3. Each sentence: 10-15 words
4. Total read time: 45-60 seconds
5. Conversational, punchy, no filler
6. End with memorable statement
7. No emojis, hashtags in script

Output format:
HOOK: [your hook]
SCRIPT: [sentence 1] | [sentence 2] | [sentence 3] | [sentence 4] | [sentence 5] | [sentence 6]"""

        user_prompt = f"""Create a viral YouTube Short script about: {topic}

Category: {category}
Make it surprising, educational, or emotionally impactful.
Include specific facts and numbers where possible."""

        response = requests.post(
            OPENCODE_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "opencode",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.85
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            hook = ""
            sentences = []

            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('HOOK:'):
                    hook = line.replace('HOOK:', '').strip()
                elif line.startswith('SCRIPT:'):
                    script_part = line.replace('SCRIPT:', '').strip()
                    sentences = [s.strip() for s in script_part.split('|') if s.strip()]

            if hook and len(sentences) >= 5:
                print(f"  AI generated script: {hook[:40]}...")
                return {
                    "topic": topic,
                    "hook": hook,
                    "sentences": [(s, topic) for s in sentences]
                }
        else:
            print(f"  OpenCode API error: {response.status_code}")

    except Exception as e:
        print(f"  OpenCode error: {e}")

    return None

def generate_audio_with_gemini(script_text):
    """Generate natural audio using Gemini TTS"""
    try:
        api_key = get_gemini_key()
        if not api_key:
            return None

        output = TEMP_DIR / f"voice-{int(datetime.now().timestamp())}.wav"

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=script_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Kore',  # Natural, clear voice
                        )
                    )
                ),
            )
        )

        if response.candidates:
            audio_data = response.candidates[0].content.parts[0].inline_data.data

            with wave.open(str(output), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(audio_data)

            print(f"  Gemini TTS: {len(script_text.split())} words")
            return str(output)

    except Exception as e:
        print(f"  Gemini TTS error: {e}")

    return None

async def generate_audio_edge_tts(text, output_path):
    """Fallback: Generate audio using edge-tts"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
        await communicate.save(str(output_path))
        return True
    except:
        return False

def generate_audio_fallback(script_text):
    """Fallback audio generation using edge-tts"""
    output = TEMP_DIR / f"voice-{int(datetime.now().timestamp())}.mp3"

    async def main():
        await generate_audio_edge_tts(script_text, str(output))

    try:
        asyncio.run(main())
        if output.exists():
            print(f"  Edge-TTS fallback: {len(script_text.split())} words")
            return str(output)
    except Exception as e:
        print(f"  Audio error: {e}")

    return None

def get_audio_duration(audio_path):
    """Get audio duration using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
             'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except:
        return 0

def download_image_from_pexels(query, idx, timestamp):
    """Download free image from Pexels"""
    try:
        output = TEMP_DIR / f"img-{timestamp}-{idx}.jpg"

        # Use Pexels API with free key if available
        pexels_key = os.environ.get("PEXELS_API_KEY", "")

        if pexels_key:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": pexels_key}
            params = {"query": query, "per_page": 5, "orientation": "portrait"}

            r = requests.get(url, headers=headers, params=params, timeout=15)
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    photo = random.choice(photos)
                    img_url = photo["src"]["large"]
                    img_response = requests.get(img_url, timeout=30)
                    if img_response.status_code == 200:
                        with open(output, "wb") as f:
                            f.write(img_response.content)
                        if output.exists() and output.stat().st_size > 5000:
                            print(f"  Pexels: {query[:25]}...")
                            return str(output)
        else:
            # Use free image source without API key
            url = f"https://source.unsplash.com/720x1280/?{quote(query.replace(' ', ','))}"
            r = requests.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 5000:
                with open(output, "wb") as f:
                    f.write(r.content)
                if output.exists():
                    print(f"  Image: {query[:25]}...")
                    return str(output)

    except Exception as e:
        print(f"  Image error: {e}")

    return None

def create_video_segment(image_path, duration, output_path, index):
    """Create video segment with Ken Burns effect"""
    output_path = Path(output_path)

    if not image_path or not Path(image_path).exists():
        # Fallback gradient
        colors = ["0x667eea", "0x764ba2", "0xf093fb", "0x4facfe", "0x00f2fe"]
        color = colors[index % len(colors)]

        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'color=0x{color[2:]}:s=720x1280:d={duration}:r=30',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-pix_fmt', 'yuv420p', str(output_path)
        ]
        subprocess.run(cmd, capture_output=True)
        return output_path.exists()

    # Calculate Ken Burns parameters
    zoom_start = 1.0
    zoom_end = 1.12
    pan_x = random.choice([-3, 0, 3])
    pan_y = random.choice([-2, 0, 2])

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', image_path,
        '-t', str(duration),
        '-vf', (
            f"scale=1440:2560:force_original_aspect_ratio=increase,"
            f"crop=1440:2560,"
            f"zoompan=z='min(zoom+0.0008,{zoom_end})':d=1:"
            f"x='iw/2-(iw/zoom/2)+{pan_x}':y='ih/2-(ih/zoom/2)+{pan_y}',"
            f"crop=720:1280"
        ),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-pix_fmt', 'yuv420p', '-r', '30',
        '-frames:v', str(int(duration * 30)),
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True)

    # If zoompan fails, use simple scale
    if not output_path.exists() or output_path.stat().st_size < 1000:
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', image_path,
            '-t', str(duration),
            '-vf', 'scale=1440:2560:force_original_aspect_ratio=increase,crop=720:1280',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-pix_fmt', 'yuv420p', '-r', '30',
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True)

    return output_path.exists()

def concatenate_segments(segments, output_path):
    """Concatenate video segments"""
    if not segments:
        return False

    output_path = Path(output_path)
    list_file = TEMP_DIR / "concat.txt"
    with open(list_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")

    cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_file),
           '-c', 'copy', str(output_path)]
    subprocess.run(cmd, capture_output=True)

    return output_path.exists()

def create_final_video(video_path, audio_path, output_path, topic, hook):
    """Create final video with text overlay"""

    # Get audio duration for exact sync
    audio_dur = get_audio_duration(audio_path)

    # Clean text for FFmpeg
    hook_clean = hook[:60].replace("'", "").replace('"', '').replace(':', '').replace('\\', '')
    topic_clean = topic[:40].replace("'", "").replace('"', '').replace(':', '').replace('\\', '')

    temp_output = TEMP_DIR / "temp_final.mp4"

    # Combine video and audio
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-i', str(audio_path),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-t', str(audio_dur),  # Match exact audio duration
        '-shortest',
        str(temp_output)
    ]
    subprocess.run(cmd, capture_output=True)

    if not temp_output.exists():
        return False

    # Add text overlay
    cmd = [
        'ffmpeg', '-y',
        '-i', str(temp_output),
        '-vf', (
            f"drawtext=text='{hook_clean}':fontsize=28:fontcolor=white:borderw=3:bordercolor=black@0.8:"
            f"x=(w-text_w)/2:y=h-140:enable='between(t,0,{audio_dur})',"
            f"drawtext=text='{topic_clean}':fontsize=22:fontcolor=yellow:borderw=2:bordercolor=black@0.7:"
            f"x=(w-text_w)/2:y=50:enable='between(t,0,{audio_dur})'"
        ),
        '-c:a', 'copy',
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True)

    output_path = Path(output_path)

    # If text overlay fails, copy without overlay
    if not output_path.exists():
        import shutil
        shutil.copy(str(temp_output), str(output_path))

    return output_path.exists()

def get_trending_topic():
    """Get trending topic from news API"""
    try:
        # Try NewsAPI (free tier)
        news_key = os.environ.get("NEWS_API_KEY", "")
        if news_key:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                if articles:
                    article = random.choice(articles[:5])
                    return {
                        "topic": article.get("title", "").split(" - ")[0][:60],
                        "description": article.get("description", ""),
                        "category": "facts"
                    }
    except:
        pass

    # Fallback to curated trending topics
    return None

# Curated high-engagement scripts
FALLBACK_SCRIPTS = [
    {
        "topic": "The oldest living thing on Earth",
        "hook": "This tree is older than the pyramids.",
        "sentences": [
            ("Meet the oldest living thing on Earth.", "ancient tree bristlecone pine"),
            ("This bristlecone pine is over 5,000 years old.", "old ancient tree nature"),
            ("It was alive when the pyramids were built.", "egypt pyramids ancient world"),
            ("Scientists study it to understand aging.", "scientist research laboratory"),
            ("Every ring in its trunk is one year of history.", "tree rings texture closeup"),
            ("It survived ice ages and world wars.", "winter snow cold nature"),
            ("This tree is still growing today.", "tree forest peaceful nature"),
        ]
    },
    {
        "topic": "Why cats see in darkness",
        "hook": "Cats see better than you at night.",
        "sentences": [
            ("Cats have superpowers after dark.", "cat night eyes glowing"),
            ("Their eyes have a special reflective layer.", "cat eyes closeup portrait"),
            ("Light passes through their retina twice.", "cat animal mysterious dark"),
            ("That's why their eyes appear to glow.", "glowing cat eyes yellow green"),
            ("While you stumble, cats navigate easily.", "cat night predator hunter"),
            ("Their pupils expand to three times human size.", "cat eyes dramatic dilated"),
            ("This made cats expert hunters.", "cat hunting predator wild"),
        ]
    },
    {
        "topic": "The ocean has more gold than governments",
        "hook": "There's more gold in the ocean than ever mined.",
        "sentences": [
            ("Deep in our oceans lies hidden fortune.", "deep ocean underwater mysterious"),
            ("Scientists found 20 billion tons of gold.", "gold bars treasure wealth"),
            ("That's enough for everyone to have pounds.", "gold coins money wealth"),
            ("Yet it's spread so thin it's worthless.", "ocean waves beach calm"),
            ("Extraction costs exceed the gold's value.", "underwater ocean blue sea"),
            ("The ocean keeps its golden secrets forever.", "ocean depth mysterious dark"),
        ]
    },
    {
        "topic": "The 5 AM habit of successful people",
        "hook": "Every successful person shares one habit.",
        "sentences": [
            ("Winners wake up before the world moves.", "sunrise morning early beautiful"),
            ("At five AM, distractions are at zero.", "quiet morning peaceful sunrise"),
            ("The mind is fresh and uncluttered.", "meditation peaceful calm zen"),
            ("This quiet hour becomes an advantage.", "sunrise success achievement"),
            ("While others sleep, winners are ahead.", "early morning city productivity"),
            ("They use this time for exercise and planning.", "workout gym morning fitness"),
            ("Take back control of your mornings.", "sunrise success achievement victory"),
        ]
    },
    {
        "topic": "Why consistency beats talent",
        "hook": "Talent fails. Consistency does not.",
        "sentences": [
            ("Every expert was once a beginner.", "athlete beginner young training"),
            ("What separates winners is consistency.", "athlete training discipline dedicated"),
            ("They showed up every single day.", "daily workout gym discipline"),
            ("Talent gives a head start only.", "runner race starting line speed"),
            ("Effort creates skills talent cannot match.", "training practice improvement progress"),
            ("Small steps accumulate into success.", "mountain peak summit achievement"),
            ("Talent is a gift. Consistency is a choice.", "determination success achievement"),
        ]
    },
    {
        "topic": "Why Kerala has no McDonald's",
        "hook": "The only Indian state without McDonald's.",
        "sentences": [
            ("Kerala stands alone without a McDonald's.", "india street food colorful market"),
            ("The reason lies in cultural values.", "india temple spiritual ancient"),
            ("Many residents are vegetarian.", "indian food curry healthy veg"),
            ("Beef is off the menu for religious reasons.", "india religious spiritual temple"),
            ("McDonald's struggled to operate profitably.", "restaurant closed empty tables"),
            ("Cultural values won over corporate expansion.", "india traditional market bustling"),
        ]
    },
    {
        "topic": "The beach with pink sand",
        "hook": "This beach has pink sand.",
        "sentences": [
            ("On Bonaire island in the Caribbean.", "caribbean tropical island aerial"),
            ("The sand has a distinctive pink color.", "pink beach sand closeup texture"),
            ("Red coral mixes with white sand.", "coral reef underwater colorful"),
            ("Crystal turquoise waters meet the pink sand.", "turquoise water beach caribbean"),
            ("A dreamlike landscape.", "paradise beach tropical beautiful"),
            ("This unknown paradise remains uncrowded.", "empty beach peaceful serene"),
            ("Nature's artistry at its finest.", "sunset beach beautiful orange"),
        ]
    },
    {
        "topic": "The spice once worth more than gold",
        "hook": "This spice was worth more than gold.",
        "sentences": [
            ("Black pepper once cost more than gold.", "black pepper spice heap pile"),
            ("Emperors paid fortunes for tiny amounts.", "roman emperor ancient wealthy"),
            ("Kerala was the world's only source.", "india kerala spice plantation pepper"),
            ("The spice traveled dangerous routes.", "silk road caravan ancient trade"),
            ("It shaped the history of global trade.", "trade ships ocean voyage discovery"),
            ("This small berry changed everything.", "peppercorn spice market colorful"),
        ]
    },
]

def get_best_script():
    """Get a script - try AI first, then fallback"""
    # Try to get trending topic
    trending = get_trending_topic()

    if trending:
        # Try AI generation with trending topic
        ai_script = generate_script_with_opencode(trending["topic"], trending.get("category", "facts"))
        if ai_script:
            return ai_script

    # Try AI with random engaging topic
    engaging_topics = [
        ("Science discoveries that will blow your mind", "facts"),
        ("History facts they don't teach in school", "facts"),
        ("Unbelievable facts about your body", "facts"),
        ("Animals with incredible superpowers", "facts"),
        ("Places that look like other planets", "travel"),
        ("Food history that will surprise you", "food"),
        ("Motivational insights for success", "quotes"),
    ]

    topic, category = random.choice(engaging_topics)
    ai_script = generate_script_with_opencode(topic, category)
    if ai_script:
        return ai_script

    # Use curated fallback
    script = random.choice(FALLBACK_SCRIPTS)
    script["style"] = "facts"
    return script

def upload_to_youtube(video_path, script):
    """Upload to YouTube as Short"""
    try:
        import base64
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        TOKEN_FILE = BASE_DIR / "youtube" / "token.json"
        CREDENTIALS_FILE = BASE_DIR / "youtube" / "credentials.json"

        if os.environ.get("GITHUB_ACTIONS"):
            token_b64 = os.environ.get("YOUTUBE_TOKEN_DATA", "")
            creds_b64 = os.environ.get("YOUTUBE_CLIENT_CONFIG", "")
            if token_b64:
                TOKEN_FILE.write_text(json.dumps(json.loads(base64.b64decode(token_b64).decode())))
            if creds_b64:
                CREDENTIALS_FILE.write_text(json.dumps(json.loads(base64.b64decode(creds_b64).decode())))

        if not CREDENTIALS_FILE.exists():
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

{script.get('hook', '')}

#shorts #{script.get('style', 'facts')} #trending #facts

📺 {CHANNEL_NAME} - Daily interesting facts

🔔 Subscribe for more!""",
                "tags": ["shorts", "trending", script.get('style', 'facts'), CHANNEL_NAME.lower()],
                "categoryId": "22",
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        print("  Uploading to YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()

        video_id = response['id']
        print(f"  [+] SUCCESS! https://youtube.com/shorts/{video_id}")
        return video_id

    except Exception as e:
        print(f"  [x] Upload error: {e}")
        return None

def run_daily():
    print("\n" + "=" * 60)
    print(f"{CHANNEL_NAME} - SHORT CREATOR v11 (OpenCode + Gemini)")
    print("=" * 60)

    timestamp = int(datetime.now().timestamp())

    try:
        # 1. Script
        print("\n[1/5] Creating script...")
        script = get_best_script()
        print(f"  Topic: {script['topic']}")
        print(f"  Sentences: {len(script['sentences'])}")

        # 2. Generate audio
        print("\n[2/5] Creating audio...")
        full_text = script['hook'] + ' ' + ' '.join([s[0] for s in script['sentences']])

        # Try Gemini TTS first, then edge-tts
        audio = generate_audio_with_gemini(full_text)
        if not audio:
            audio = generate_audio_fallback(full_text)

        if not audio:
            raise Exception("Audio generation failed")

        audio_duration = get_audio_duration(audio)
        print(f"  Audio duration: {audio_duration:.1f}s")

        # 3. Download images
        print("\n[3/5] Downloading images...")
        images = []
        for idx, (sentence, query) in enumerate(script['sentences']):
            img = download_image_from_pexels(query, idx, timestamp)
            images.append(img)
            print(f"  [{idx+1}] {sentence[:40]}...")

        valid_images = [i for i in images if i]
        print(f"  Downloaded {len(valid_images)} images")

        # 4. Create video with synced segments
        print("\n[4/5] Building video...")

        # Calculate duration per segment
        num_segments = len(script['sentences'])
        segment_duration = audio_duration / num_segments

        video_segments = []
        for idx in range(num_segments):
            seg = TEMP_DIR / f"seg-{timestamp}-{idx}.mp4"
            img = images[idx] if idx < len(images) else None

            if create_video_segment(img, segment_duration, str(seg), idx):
                video_segments.append(str(seg))

        if not video_segments:
            raise Exception("No video segments created")

        # Concatenate video
        concat_video = TEMP_DIR / f"concat-{timestamp}.mp4"
        concatenate_segments(video_segments, str(concat_video))

        if not concat_video.exists():
            raise Exception("Video concatenation failed")

        # 5. Final output
        print("\n[5/5] Creating final video...")
        output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

        if create_final_video(str(concat_video), str(audio), str(output),
                             script['topic'], script['hook']):
            final_duration = get_audio_duration(str(output))
            print(f"  Video: {final_duration:.1f}s, {output.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            raise Exception("Final video creation failed")

        # Upload
        video_id = upload_to_youtube(str(output), script)

        print("\n" + "=" * 60)
        print(f"[+] DONE! https://youtube.com/shorts/{video_id}" if video_id else "[+] Done!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[x] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        for f in TEMP_DIR.glob("*"):
            try:
                f.unlink()
            except:
                pass

if __name__ == "__main__":
    run_daily()