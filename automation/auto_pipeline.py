"""
YouTube Shorts Generator v10 - AI-Powered
- OpenCode API for script generation
- Stable Diffusion for AI-generated images
- edge-tts for natural audio
- FFmpeg for professional video with Ken Burns
"""

import os
import sys
import json
import random
import subprocess
import requests
import asyncio
import re
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

# Pre-defined topic categories (for AI to generate scripts from)
TOPIC_CATEGORIES = {
    "facts": "Interesting facts about science, nature, history, or the world",
    "kerala": "Facts about Kerala, India - culture, history, food, places",
    "travel": "Amazing places, unusual destinations, travel facts",
    "quotes": "Motivational quotes with explanations",
    "food": "Food history, interesting food facts from around the world",
}

# Image prompts for Stable Diffusion
IMAGE_STYLES = [
    "cinematic lighting, high quality, dramatic",
    "beautiful lighting, professional photography",
    "vibrant colors, detailed, 4k quality",
    "stunning composition, epic scenery",
    "clean design, minimalist, elegant"
]

def get_openai_key():
    """Get OpenAI API key from environment or file"""
    # Check environment variables (set these in GitHub Secrets)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        return api_key

    # Check local file
    key_file = BASE_DIR / "youtube" / "openai_key.txt"
    if key_file.exists():
        return key_file.read_text().strip()

    return None

def get_stable_diffusion_key():
    """Get Stable Diffusion API key"""
    api_key = os.environ.get("STABILITY_API_KEY", "")
    if api_key:
        return api_key

    # Check local file
    key_file = BASE_DIR / "youtube" / "sd_key.txt"
    if key_file.exists():
        return key_file.read_text().strip()

    return None

def generate_script_with_openai(topic_category, topic):
    """Use OpenCode/OpenAI API to generate a compelling script"""
    try:
        api_key = get_openai_key()
        if not api_key:
            print("  No OpenAI key - using fallback script")
            return None

        system_prompt = """You are a YouTube Shorts script writer. Create engaging, fast-paced scripts for short videos.

Rules:
1. Script must have a HOOK in the first sentence (curiosity gap)
2. 6-8 sentences total
3. Each sentence should be 10-15 words
4. Total script should be 45-60 seconds when read aloud
5. End with a memorable takeaway or call to action
6. Use simple, conversational language
7. NO hashtags, emojis in the script itself

Format your response EXACTLY like this (no other text):
HOOK: [your hook sentence]
SCRIPT: [sentence 1] | [sentence 2] | [sentence 3] | [sentence 4] | [sentence 5] | [sentence 6] | [sentence 7]"""

        user_prompt = f"Write a script about: {TOPIC_CATEGORIES.get(topic_category, topic_category)} - specifically about: {topic}"

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.8
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            # Parse the response
            hook = ""
            sentences = []

            for line in content.split('\n'):
                if line.startswith('HOOK:'):
                    hook = line.replace('HOOK:', '').strip()
                elif line.startswith('SCRIPT:'):
                    script_part = line.replace('SCRIPT:', '').strip()
                    sentences = [s.strip() for s in script_part.split('|')]

            if hook and sentences:
                return {
                    "topic": topic,
                    "hook": hook,
                    "sentences": [(s, f"{topic.lower()} {topic_category}") for s in sentences]
                }
    except Exception as e:
        print(f"  OpenAI error: {e}")

    return None

def generate_image_with_stable_diffusion(prompt, idx, timestamp):
    """Generate image using Stable Diffusion via Replicate or Segmind"""
    output = TEMP_DIR / f"ai-img-{timestamp}-{idx}.jpg"

    # Try Replicate (free tier available)
    try:
        replicate_key = os.environ.get("REPLICATE_API_TOKEN", "")
        if replicate_key:
            import replicate
            output_url = replicate.run(
                "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a93b55790a56c370f2e0e",
                input={
                    "prompt": f"{prompt}, {random.choice(IMAGE_STYLES)}",
                    "width": 768,
                    "height": 1344,  # 9:16 aspect ratio
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5,
                    "negative_prompt": "blurry, low quality, distorted, cartoon, anime"
                }
            )

            # Download the image
            img_response = requests.get(output_url, timeout=60)
            if img_response.status_code == 200:
                with open(output, "wb") as f:
                    f.write(img_response.content)
                if output.exists() and output.stat().st_size > 5000:
                    print(f"  AI Generated: {prompt[:30]}...")
                    return str(output)
    except Exception as e:
        print(f"  Replicate error: {e}")

    # Try Segmind
    try:
        segmind_key = os.environ.get("SEGMIND_API_KEY", "")
        if segmind_key:
            response = requests.post(
                "https://api.segmind.com/v1/sd15",
                headers={"x-api-key": segmind_key},
                json={
                    "prompt": f"{prompt}, {random.choice(IMAGE_STYLES)}",
                    "width": 768,
                    "height": 1344,
                    "steps": 20,
                    "cfg_scale": 7.5,
                    "neg_prompt": "blurry, low quality, distorted"
                },
                timeout=60
            )

            if response.status_code == 200:
                with open(output, "wb") as f:
                    f.write(response.content)
                if output.exists() and output.stat().st_size > 5000:
                    print(f"  AI Generated: {prompt[:30]}...")
                    return str(output)
    except Exception as e:
        print(f"  Segmind error: {e}")

    # Fallback to free images
    return download_freepik_image(prompt, idx, timestamp)

def download_freepik_image(search_term, idx, timestamp):
    """Download free image from various sources"""
    output = TEMP_DIR / f"img-{timestamp}-{idx}.jpg"

    # Try multiple sources
    sources = [
        f"https://source.unsplash.com/768x1344/?{quote(search_term.replace(' ', ','))}",
        f"https://picsum.photos/seed/{search_term.replace(' ', '')[:20]}/768/1344",
    ]

    for url in sources:
        try:
            r = requests.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(output, "wb") as f:
                    f.write(r.content)
                if output.exists():
                    print(f"  Image: {search_term[:30]}...")
                    return str(output)
        except:
            pass

    # Ultimate fallback - gradient with text
    return None

async def generate_audio_edge(text, output_path):
    """Generate natural audio using edge-tts"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        print(f"  Edge-TTS error: {e}")
        return False

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

def create_ken_burns_video(image_path, duration, output_path):
    """Create video with Ken Burns zoom effect"""
    if not image_path or not Path(image_path).exists():
        # Fallback gradient
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'color=0x1a1a2e:s=1080x1920:d={duration}:r=30',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-pix_fmt', 'yuv420p', str(output_path)
        ]
        subprocess.run(cmd, capture_output=True)
        return output_path.exists()

    # Ken Burns: slow zoom and pan
    zoom_start = 1.0
    zoom_end = 1.15
    pan_x_start = 0
    pan_y_start = 0
    pan_x_end = random.choice([-5, 5])
    pan_y_end = random.choice([-3, 3])

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', image_path,
        '-t', str(duration),
        '-vf', (
            f"scale=1920:1920:force_original_aspect_ratio=increase,"
            f"crop=1920:1920,"
            f"zoompan=z='min(zoom+0.001,{zoom_end})':d=1:x='iw/2-(iw/zoom/2)+{pan_x_start}':y='ih/2-(ih/zoom/2)+{pan_y_start}',"
            f"setsar=1,"
            f"crop=1080:1920"
        ),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-pix_fmt', 'yuv420p', '-r', '30',
        '-frames:v', str(int(duration * 30)),
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True)

    # If zoompan failed, use simple scale
    if not output_path.exists() or output_path.stat().st_size < 1000:
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', image_path,
            '-t', str(duration),
            '-vf', 'scale=1920:1920:force_original_aspect_ratio=increase,crop=1080:1920',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-pix_fmt', 'yuv420p', '-r', '30',
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True)

    return output_path.exists()

def concatenate_segments(segments, output_path, is_video=True):
    """Concatenate video or audio segments"""
    if not segments:
        return False

    list_file = TEMP_DIR / f"{'video' if is_video else 'audio'}_concat.txt"
    with open(list_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")

    if is_video:
        cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_file),
               '-c', 'copy', str(output_path)]
    else:
        cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_file),
               '-c', 'copy', str(output_path)]

    subprocess.run(cmd, capture_output=True)
    return output_path.exists()

def create_final_video(video_path, audio_path, output_path, topic, hook):
    """Create final video with audio and text overlay"""

    # First, combine video and audio
    temp_output = TEMP_DIR / "temp_combined.mp4"
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-i', str(audio_path),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-shortest',
        str(temp_output)
    ]
    subprocess.run(cmd, capture_output=True)

    if not temp_output.exists():
        return False

    # Get actual duration
    duration = get_audio_duration(str(audio_path))

    # Add text overlay
    hook_short = hook[:50].replace("'", "").replace('"', '').replace(':', '').replace(',', '')
    topic_short = topic[:35].replace("'", "").replace('"', '').replace(':', '').replace(',', '')

    cmd = [
        'ffmpeg', '-y',
        '-i', str(temp_output),
        '-vf', (
            f"drawtext=text='{hook_short}':fontsize=36:fontcolor=white:borderw=4:bordercolor=black@0.9:"
            f"x=(w-text_w)/2:y=h-180:enable='between(t,0,{duration})',"
            f"drawtext=text='{topic_short}':fontsize=28:fontcolor=yellow:borderw=3:bordercolor=black@0.8:"
            f"x=(w-text_w)/2:y=60:enable='between(t,0,{duration})'"
        ),
        '-c:a', 'copy',
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True)

    # If text overlay failed, just copy temp
    if not output_path.exists():
        import shutil
        shutil.copy(str(temp_output), str(output_path))

    return output_path.exists()

def get_best_script():
    """Get script - try AI first, then fallback"""
    all_scripts = []
    for style, scripts in SHORT_SCRIPTS.items():
        for script in scripts:
            script["style"] = style
            all_scripts.append(script)

    return random.choice(all_scripts)

# Fallback scripts with per-sentence images
SHORT_SCRIPTS = {
    "facts": [
        {"topic": "The oldest living thing on Earth", "hook": "This tree is older than the pyramids.", "sentences": [
            ("Meet the oldest living thing on Earth.", "ancient bristlecone pine forest mountains"),
            ("This tree has been growing for over five thousand years.", "ancient old tree bark texture"),
            ("It was already old when pyramids were built.", "egypt pyramids ancient monuments"),
            ("Scientists study it to understand longevity.", "scientist research nature conservation"),
            ("Every ring represents a year of incredible history.", "tree rings cross section macro"),
            ("It survived ice ages and world wars.", "winter snow forest cold"),
            ("This silent witness still grows today.", "tree forest peaceful nature"),
        ]},
        {"topic": "Why cats see in darkness", "hook": "Cats see better than you at night.", "sentences": [
            ("Cats have superpowers after dark.", "cat night eyes glowing mysterious"),
            ("Their eyes contain a special reflective layer.", "cat closeup eyes portrait"),
            ("This layer reflects light back through the retina.", "cat animal eyes yellow"),
            ("That's why their eyes appear to glow.", "glowing cat eyes darkness mysterious"),
            ("While you stumble, cats navigate with ease.", "cat night predator hunter"),
            ("Their pupils dilate to three times human size.", "cat eyes macro closeup feline"),
            ("This made them expert hunters.", "cat hunting predator wild"),
        ]},
        {"topic": "The ocean has more gold than all governments", "hook": "There's more gold in the ocean.", "sentences": [
            ("Deep in our oceans lies a hidden fortune.", "deep ocean underwater mysterious dark"),
            ("Scientists estimate twenty billion tons of gold.", "gold treasure wealth bars"),
            ("Enough for everyone on Earth to have pounds.", "gold coins money wealth"),
            ("Yet it's impossibly spread out.", "ocean waves coast beach"),
            ("Extraction costs exceed the gold's value.", "ocean depth blue sea"),
            ("The ocean keeps its golden secrets.", "underwater coral reef colorful"),
        ]},
    ],
    "kerala": [
        {"topic": "Why Kerala has no McDonald's", "hook": "The only Indian state without McDonald's.", "sentences": [
            ("Kerala stands alone without a McDonald's.", "india street food market colorful"),
            ("The reason lies in unique cultural values.", "india traditional culture heritage"),
            ("Many residents are vegetarian.", "indian vegetarian food curry healthy"),
            ("Beef is off the menu for religious reasons.", "india temple spiritual worship"),
            ("McDonald's struggled to operate profitably.", "restaurant empty tables closed"),
            ("Cultural values won over corporate expansion.", "india traditional market bustling"),
        ]},
        {"topic": "The martial art that inspired all others", "hook": "This 3000 year old art inspired action movies.", "sentences": [
            ("Kalaripayattu is the mother of martial arts.", "martial arts warrior combat stance"),
            ("Born in Kerala three thousand years ago.", "india kerala traditional ancient"),
            ("It combines combat with spiritual practice.", "yoga meditation spiritual peaceful"),
            ("Movements look almost dance-like.", "martial arts fluid movement dance"),
            ("Legends say Buddha learned from Kerala masters.", "buddha spiritual meditation peaceful"),
            ("This ancient art influenced traditions across Asia.", "asian martial arts warrior china"),
            ("Kalaripayattu is experiencing a modern revival.", "martial arts training practice"),
        ]},
        {"topic": "How Kerala achieved 100% literacy", "hook": "This Indian state achieved 100% literacy first.", "sentences": [
            ("In 1991, Kerala became fully literate.", "books library education knowledge"),
            ("No other Indian state had done this before.", "student reading books happy"),
            ("The secret was government commitment to education.", "government building india parliament"),
            ("Even poor families prioritized schooling.", "children school books studying"),
            ("Education became part of the culture.", "books education knowledge library"),
            ("Women led grassroots literacy efforts.", "women education empowerment success"),
            ("Kerala proved universal education was possible.", "graduation success achievement education"),
        ]},
    ],
    "travel": [
        {"topic": "The most dangerous road on Earth", "hook": "This road has killed hundreds of people.", "sentences": [
            ("The Karakoram Highway passes through terrifying territory.", "pakistan mountain road himalayas extreme"),
            ("Built during the 1970s by three countries.", "mountain road engineering construction"),
            ("Narrow passages hang above deadly valleys.", "mountain cliff edge dangerous sheer"),
            ("There are no guardrails.", "mountain road edge no barrier"),
            ("Landslides and rockfalls are common.", "landslide rocks falling mountain danger"),
            ("Yet thousands of trucks use it yearly.", "truck highway mountain transport"),
            ("The most dangerous highway on Earth.", "dangerous road mountain extreme scary"),
        ]},
        {"topic": "Animals that outnumber humans", "hook": "Animals outnumber humans by 100 to 1 here.", "sentences": [
            ("In Botswana, wildlife roams freely.", "africa safari elephants majestic"),
            ("Lions, zebras, and elephants live here.", "safari lions zebras together wildlife"),
            ("Humans are merely visitors.", "safari jeep watching wildlife"),
            ("Part of Chobe National Park.", "africa national park beautiful scenery"),
            ("Thousands witness animal migrations yearly.", "elephant migration africa savanna"),
            ("Nature operates by its own rules.", "wilderness nature africa beautiful"),
            ("A glimpse of the ancient world.", "africa sunset wilderness beautiful"),
        ]},
        {"topic": "The beach with pink sand", "hook": "This beach has pink sand.", "sentences": [
            ("On Bonaire in the Caribbean.", "caribbean tropical island aerial view"),
            ("The sand has a distinctive pink color.", "pink beach sand closeup"),
            ("Red coral mixes with white sand.", "coral reef underwater colorful beautiful"),
            ("Crystal turquoise waters meet pink sand.", "turquoise water beach caribbean paradise"),
            ("A dreamlike landscape.", "paradise beach tropical beautiful serene"),
            ("This unknown paradise remains uncrowded.", "empty beach peaceful tropical serene"),
            ("Nature's artistry at its finest.", "sunset beach beautiful orange sky"),
        ]},
    ],
    "quotes": [
        {"topic": "The 5 AM habit of successful people", "hook": "Every successful person shares one morning habit.", "sentences": [
            ("Winners wake up before the world moves.", "sunrise morning early beautiful orange"),
            ("At five AM, distractions are zero.", "quiet morning peaceful sunrise calm"),
            ("The mind is fresh and uncluttered.", "meditation peaceful calm morning"),
            ("This quiet hour becomes an advantage.", "sunrise success achievement motivation"),
            ("While others sleep, winners are ahead.", "early morning city sunrise productivity"),
            ("They use this time wisely.", "workout gym morning exercise fitness"),
            ("Take control of your mornings.", "sunrise success achievement victory"),
        ]},
        {"topic": "Why consistency beats talent", "hook": "Talent will fail you. Consistency will not.", "sentences": [
            ("Every expert was once a beginner.", "athlete beginner training young"),
            ("What separates winners is consistency.", "athlete training discipline determined"),
            ("They showed up every single day.", "daily workout gym discipline"),
            ("Talent gives a head start only.", "runner race starting block speed"),
            ("Effort creates skills talent cannot match.", "training gym practice improvement"),
            ("Small steps accumulate into success.", "mountain peak summit achievement"),
            ("Talent is a gift. Consistency is a choice.", "determination willpower success achievement"),
        ]},
    ],
    "food": [
        {"topic": "The pizza created to feed a poor family", "hook": "This pizza helped a poor family.", "sentences": [
            ("The Margherita pizza was born in Naples.", "italian pizza restaurant authentic"),
            ("Queen Margherita visited a poor neighborhood.", "queen royal palace elegant italy"),
            ("Chefs had nothing fancy available.", "simple kitchen cooking basic"),
            ("The local cook improvised brilliantly.", "pizza being made fresh ingredients"),
            ("The queen loved it.", "delicious food happy satisfied smile"),
            ("That humble creation became world-famous.", "famous pizza restaurant busy italy"),
            ("Simple beginnings can lead to fame.", "success achievement humble beginning"),
        ]},
        {"topic": "The spice once worth more than gold", "hook": "This spice was once worth more than gold.", "sentences": [
            ("Black pepper once cost more than gold.", "black pepper spice pile heap"),
            ("Emperors paid fortunes for tiny amounts.", "roman emperor ancient wealth gold"),
            ("Kerala was the world's only source.", "india kerala spice plantation pepper"),
            ("The spice traveled dangerous routes.", "silk road caravan trade ancient"),
            ("It shaped the history of global trade.", "trade ships ocean voyage discovery"),
            ("This small berry changed everything.", "peppercorn spice market colorful"),
        ]},
    ]
}

def upload_to_youtube(video_path, script):
    """Upload to YouTube"""
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

#shorts #{script['style']} #facts

📺 {CHANNEL_NAME} - Daily interesting facts

🔔 Subscribe for more!""",
                "tags": ["shorts", script["style"], "facts", CHANNEL_NAME.lower()],
                "categoryId": "22",
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        print("  Uploading...")
        response = None
        while response is None:
            status, response = request.next_chunk()

        video_id = response['id']
        print(f"  [+] Done! https://www.youtube.com/shorts/{video_id}")
        return video_id

    except Exception as e:
        print(f"  [x] Error: {e}")
        return None

def run_daily():
    print("\n" + "=" * 60)
    print(f"{CHANNEL_NAME} - SHORT CREATOR v10 (AI-Powered)")
    print("=" * 60)

    timestamp = int(datetime.now().timestamp())

    try:
        # 1. Script - Try AI first
        print("\n[1/5] Creating script...")
        script = get_best_script()

        # Try AI script generation if API key available
        ai_script = generate_script_with_openai(script["style"], script["topic"])
        if ai_script:
            script = ai_script
            print(f"  AI Generated script: {script['topic']}")
        else:
            print(f"  Using curated script: {script['topic']}")

        print(f"  Sentences: {len(script['sentences'])}")

        # 2. Generate AI images and audio per sentence
        print("\n[2/5] Creating audio and images...")
        audio_segments = []
        image_segments = []
        total_audio_duration = 0

        for idx, (text, image_prompt) in enumerate(script['sentences']):
            # Generate audio
            audio_seg = TEMP_DIR / f"audio-{timestamp}-{idx}.mp3"
            success = asyncio.run(generate_audio_edge(text, str(audio_seg)))

            if success and audio_seg.exists():
                dur = get_audio_duration(str(audio_seg))
                audio_segments.append(str(audio_seg))
                print(f"  [{idx+1}] Audio: {text[:35]}... ({dur:.1f}s)")
                total_audio_duration += dur
            else:
                audio_segments.append(None)

            # Generate AI image
            img = generate_image_with_stable_diffusion(image_prompt, idx, timestamp)
            if not img:
                img = download_freepik_image(image_prompt, idx, timestamp)
            image_segments.append(img)

        if not audio_segments or all(not a for a in audio_segments):
            raise Exception("No audio generated")

        print(f"  Total duration: {total_audio_duration:.1f}s")

        # 3. Combine audio
        print("\n[3/5] Combining audio...")
        full_audio = TEMP_DIR / f"full-audio-{timestamp}.mp3"
        valid_audio = [a for a in audio_segments if a and Path(a).exists()]

        if len(valid_audio) == 1:
            Path(valid_audio[0]).rename(full_audio)
        elif len(valid_audio) > 1:
            concatenate_segments(valid_audio, str(full_audio), is_video=False)

        if not full_audio.exists():
            raise Exception("Audio combination failed")

        final_duration = get_audio_duration(str(full_audio))

        # 4. Create video segments
        print("\n[4/5] Building video with Ken Burns effect...")

        video_segments = []
        segment_durations = []

        # Calculate durations
        for idx, audio_seg in enumerate(audio_segments):
            if audio_seg and Path(audio_seg).exists():
                dur = get_audio_duration(audio_seg)
            else:
                remaining = final_duration - sum(segment_durations)
                silent_count = sum(1 for a in audio_segments[idx:] if not a or not Path(a).exists())
                dur = remaining / silent_count if silent_count > 0 else 3.0

            segment_durations.append(dur)

            seg = TEMP_DIR / f"seg-{timestamp}-{idx}.mp4"
            img = image_segments[idx]

            if create_ken_burns_video(img, dur, str(seg)):
                video_segments.append(str(seg))

        if not video_segments:
            raise Exception("No video segments created")

        # Concatenate video
        concat_video = TEMP_DIR / f"concat-{timestamp}.mp4"
        concatenate_segments(video_segments, str(concat_video), is_video=True)

        if not concat_video.exists():
            raise Exception("Video concatenation failed")

        # 5. Final output
        print("\n[5/5] Creating final video...")
        output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

        if create_final_video(str(concat_video), str(full_audio), str(output),
                             script['topic'], script['hook']):
            print(f"  Video created: {output.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            raise Exception("Final video creation failed")

        # Upload
        video_id = upload_to_youtube(str(output), script)

        print("\n" + "=" * 60)
        print(f"[+] SUCCESS! https://www.youtube.com/shorts/{video_id}" if video_id else "[+] Done!")
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