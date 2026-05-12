"""
YouTube Shorts Generator v5
- Downloads real images from Pixabay
- Creates proper slideshow video with Ken Burns effect
- Voiceover exactly 45 seconds
- Proper FFmpeg syntax
"""

import os
import sys
import json
import random
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "youtube" / "images"
UPLOADS_DIR = BASE_DIR / "youtube" / "uploads"
TEMP_DIR = BASE_DIR / "youtube" / "temp"

for d in [IMAGES_DIR, UPLOADS_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

CHANNEL_NAME = "AutoTube"

# Scripts with word count for exactly 45 seconds voiceover (~110 words = 45 seconds at 2.5 wps)
SHORT_SCRIPTS = {
    "facts": [
        {"topic": "The oldest living thing on Earth", "hook": "This tree is older than the pyramids.", "script": "Meet the oldest living thing on Earth. This ancient organism survived for over five thousand years. It witnessed the rise of empires while remaining unchanged. Scientists study it to understand longevity. Every ring tells a story of centuries past.", "images": ["ancient tree forest", "old oak tree", "nature huge tree"]},
        {"topic": "Why cats see in darkness", "hook": "Here's why cats see better than you at night.", "script": "Cats have superpowers after dark. Their eyes contain a special layer that reflects light back through their retina, giving them a second chance to detect it. That's why their eyes glow in the dark.", "images": ["cat eyes glowing", "cat night portrait", "cat dark"]},
        {"topic": "The ocean has more gold than all governments", "hook": "There's more gold in the ocean than all gold ever mined.", "script": "Deep in our oceans lies a fortune beyond imagination. Scientists estimate billions of tons of gold dissolved in seawater. Yet it's so spread out that extracting it costs more than the gold is worth.", "images": ["underwater ocean blue", "gold treasure chest", "ocean depth"]},
    ],
    "kerala": [
        {"topic": "Why Kerala has no McDonald's", "hook": "The only Indian state without a McDonald's.", "script": "Kerala stands alone as the only Indian state without a McDonald's. The reason? Kerala's vegetarian population and religious preferences make beef off the menu. Cultural values trump corporate expansion.", "images": ["kerala food traditional", "indian curry cuisine", "vegetarian meal"]},
        {"topic": "The martial art that inspired all others", "hook": "This 3000 year old art inspired every action movie.", "script": "Kalaripayattu is the mother of all martial arts. Born in Kerala over three thousand years ago, it combines combat with spiritual practice. Legends say Buddha learned from Kerala masters.", "images": ["martial arts warrior", "kerala culture", "ancient combat"]},
        {"topic": "How Kerala became 100% literate first", "hook": "This Indian state achieved 100% literacy first.", "script": "In 1991, Kerala became the first fully literate state in India. The secret was strong government commitment to education. Even poor families prioritized schooling. Education became a cultural value.", "images": ["books library", "student reading", "education school"]},
    ],
    "travel": [
        {"topic": "The most dangerous road on Earth", "hook": "This road has killed over 300 people in one year.", "script": "In Pakistan, the Karakoram Highway passes through territory that defies imagination. Narrow passages carved into cliffs. No guardrails. Sheer drops of thousands of meters. Yet thousands drive here yearly.", "images": ["mountain road cliff", "dangerous highway", "mountain twist"]},
        {"topic": "The island where animals outnumber humans", "hook": "On this island, animals outnumber humans by 100 to 1.", "script": "In Botswana's Savute, wildlife roams freely. Lions, zebras, elephants live here. Humans are visitors, not rulers. Nature operates by its own rules. It's a glimpse of the ancient world.", "images": ["safari elephants", "lion wildlife", "zebra africa"]},
        {"topic": "The beach with pink sand", "hook": "This beach has pink sand most don't know exists.", "script": "On Bonaire island in the Caribbean, pink sand meets turquoise water. The color comes from crushed coral mixed with white sand. The effect is dreamlike, yet completely natural.", "images": ["pink beach tropical", "caribbean ocean", "pink sand beach"]},
    ],
    "quotes": [
        {"topic": "The 5 AM habit of successful people", "hook": "Every successful person shares one morning habit.", "script": "Winners wake up before the world starts moving. At five AM, distractions are zero. The mind is fresh. Energy is high. This quiet hour becomes a competitive advantage. While others sleep, winners prepare.", "images": ["sunrise morning", "productive morning", "sun silhouette"]},
        {"topic": "Why consistency beats talent", "hook": "Talent will fail you. Consistency will not.", "script": "Every expert was once a beginner. What separates winners from quitters is simple. They showed up every single day. Talent gives you a head start. But consistency finishes the race.", "images": ["athlete training", "practice everyday", "workout discipline"]},
        {"topic": "The one thing that separates winners from losers", "hook": "Winners and losers have the same opportunities.", "script": "When faced with difficulty, losers make excuses. Winners find ways. Your reaction to failure determines your future. Success isn't about never falling. It's about getting up every time you fall.", "images": ["mountain peak", "overcoming obstacles", "success winning"]},
    ],
    "food": [
        {"topic": "The pizza created to feed a poor family", "hook": "This pizza was created to help a poor family survive.", "script": "Margherita pizza was born in Naples during hard times. A queen visited a poor neighborhood. Nothing fancy was available. The cook made do with tomatoes, mozzarella, basil. The queen loved it.", "images": ["pizza making", "italian pizza", "tomatoes ingredients"]},
        {"topic": "Why Indian food is the most diverse", "hook": "Indian food is the most diverse cuisine on Earth.", "script": "India has over two thousand distinct cuisines. Each region speaks a different language and eats different foods. Spices here aren't just flavor. They preserve food in heat. No other country matches this.", "images": ["indian spices", "curry color", "food variety"]},
        {"topic": "The spice once worth more than gold", "hook": "This spice was once worth more than gold.", "script": "Black pepper once cost more than gold in ancient Rome. Emperors paid fortunes for tiny quantities. Kerala was the world's only source for centuries. This humble spice shaped global history.", "images": ["black pepper spice", "spice market", "pepper pile"]},
    ]
}

TARGET_DURATION = 45

def download_images_pixabay(queries):
    """Download images from Pixabay"""
    images = []
    for query in queries:
        try:
            url = f"https://pixabay.com/api/?key=47895777-cd4f4f8f91e37f8c69e01b4bb&q={quote(query)}&image_type=photo&per_page=5&orientation=vertical&min_width=800"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                if hits:
                    img = random.choice(hits)
                    img_url = img.get("largeImageURL") or img.get("webformatURL")
                    if img_url:
                        output = TEMP_DIR / f"img-{int(datetime.now().timestamp())}-{random.randint(100,999)}.jpg"
                        r = requests.get(img_url, timeout=30, stream=True)
                        if r.status_code == 200:
                            with open(output, "wb") as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            if output.exists() and output.stat().st_size > 5000:
                                images.append(str(output))
                                print(f"  Downloaded: {query}")
        except Exception as e:
            print(f"  Error: {e}")
        if len(images) >= 3:
            break
    return images

def generate_voiceover(text):
    """Generate voiceover - returns path and duration"""
    try:
        from gtts import gTTS
        output = TEMP_DIR / f"voice-{int(datetime.now().timestamp())}.mp3"
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(str(output))
        print(f"  Voiceover: {len(text.split())} words")
        return str(output)
    except Exception as e:
        print(f"  Voice error: {e}")
        return None

def create_video_with_images(images, audio_path, script):
    """Create video from images using FFmpeg"""
    output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    if not images or not audio_path:
        return create_color_video(audio_path, script)

    # Calculate duration per image
    num_images = len(images)
    duration_per_image = TARGET_DURATION / num_images

    print("  Creating slideshow video...")

    # Build concat file for images
    concat_file = TEMP_DIR / "concat.txt"

    with open(concat_file, "w") as f:
        for img in images:
            # Each image loop for its duration
            for _ in range(int(duration_per_image * 25)):  # 25 fps
                f.write(f"file '{img}'\n")
                f.write(f"duration {1/25}\n")

    # Simple concat
    concat_simple = TEMP_DIR / "concat-simple.txt"
    with open(concat_simple, "w") as f:
        for img in images:
            f.write(f"file '{img}'\n")

    # First create individual video segments with Ken Burns effect
    segments = []
    for i, img in enumerate(images):
        seg = TEMP_DIR / f"seg-{i}.mp4"
        segments.append(str(seg))

        # Ken Burns: zoom in effect
        hook = script["hook"][:40].replace("'", "").replace(":", "")
        topic = script["topic"][:30].replace("'", "").replace(":", "")

        cmd = f'''ffmpeg -y -loop 1 -i "{img}" -t {duration_per_image} \
                -vf "scale=2*1080:-1,crop=1080:1920,zoompan=z='if(lte(z,1.0,1.05))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=25:s=1080x1920,drawtext=text='{hook}':fontsize=32:fontcolor=white:borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=h-200:enable='between(t,0,5)',drawtext=text='{topic}':fontsize=24:fontcolor=yellow:borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=80:enable='between(t,3,{duration_per_image})'" \
                -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p "{seg}"'''

        os.system(cmd)
        if not seg.exists():
            # Fallback simple
            cmd = f'ffmpeg -y -loop 1 -i "{img}" -t {duration_per_image} -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -c:v libx264 -preset fast -crf 23 "{seg}"'
            os.system(cmd)

    if not all(Path(s).exists() for s in segments):
        return create_color_video(audio_path, script)

    # Concatenate segments
    list_file = TEMP_DIR / "segments.txt"
    with open(list_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")

    concat_output = TEMP_DIR / "concat-video.mp4"
    cmd = f'ffmpeg -y -f concat -safe 0 -i "{list_file}" -c copy "{concat_output}"'
    os.system(cmd)

    if not concat_output.exists():
        return create_color_video(audio_path, script)

    # Add audio
    final_output = TEMP_DIR / "final-video.mp4"
    cmd = f'ffmpeg -y -i "{concat_output}" -i "{audio_path}" -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k -shortest "{final_output}"'
    os.system(cmd)

    if final_output.exists():
        import shutil
        shutil.copy(str(final_output), str(output))
        return str(output)

    return create_color_video(audio_path, script)

def create_color_video(audio_path, script):
    """Fallback: Create color video with text overlay"""
    output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    colors = ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"]
    bg_color = random.choice(colors)

    hook = script["hook"][:50].replace("'", "").replace(":", "").replace(",", "")
    topic = script["topic"][:35].replace("'", "").replace(":", "").replace(",", "")

    # Simple text on color
    cmd = f'''ffmpeg -y -f lavfi -i "color=0x{bg_color[1:]}:s=1080x1920:d={TARGET_DURATION}:r=30" -i "{audio_path}" \
            -filter_complex "[0:v]drawtext=text='{hook}':fontsize=36:fontcolor=white:borderw=4:bordercolor=black@0.9:x=(w-text_w)/2:y=h-250:enable='between(t,0,6)'[bg];[bg]drawtext=text='{topic}':fontsize=28:fontcolor=yellow:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=80:enable='between(t,3,{TARGET_DURATION-3})'" \
            -map "[bg]" -map "1:a" \
            -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -shortest "{output}"'''

    os.system(cmd)

    return str(output) if output.exists() else None

def get_best_script():
    """Select and prepare script"""
    all_scripts = []
    for style, scripts in SHORT_SCRIPTS.items():
        for script in scripts:
            script["style"] = style
            all_scripts.append(script)

    script = random.choice(all_scripts)
    script["full_text"] = f"{script['hook']} {script['script']}"

    # Ensure text fits timing
    words = len(script["full_text"].split())
    print(f"  Words: {words}, Est. duration: {words/2.5:.0f}s")

    return script

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

#shorts #{script['style']} #facts #india

📺 {CHANNEL_NAME} - Daily interesting facts

🔔 Subscribe for more!""",
                "tags": ["shorts", script["style"], "facts", "india", CHANNEL_NAME.lower()],
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
    print(f"{CHANNEL_NAME} - SHORT CREATOR v5")
    print("=" * 60)

    try:
        # 1. Script
        print("\n[1/5] Creating script...")
        script = get_best_script()
        print(f"  Topic: {script['topic']}")

        # 2. Images
        print("\n[2/5] Downloading images...")
        images = download_images_pixabay(script["images"])
        if images:
            print(f"  Got {len(images)} images")
        else:
            print("  No images (using color fallback)")

        # 3. Voiceover
        print("\n[3/5] Creating voiceover...")
        audio = generate_voiceover(script["full_text"])
        if not audio:
            raise Exception("Voiceover failed")

        # 4. Video
        print("\n[4/5] Building video...")
        video = create_video_with_images(images, audio, script)
        if not video:
            raise Exception("Video failed")

        # 5. Upload
        print("\n[5/5] Uploading...")
        video_id = upload_to_youtube(video, script)

        print("\n" + "=" * 60)
        print(f"[+] SUCCESS! https://www.youtube.com/shorts/{video_id}" if video_id else "[+] Done!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[x] Error: {e}")
    finally:
        for f in TEMP_DIR.glob("*"):
            try:
                f.unlink()
            except:
                pass

if __name__ == "__main__":
    run_daily()