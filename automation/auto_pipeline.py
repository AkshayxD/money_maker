"""
YouTube Shorts Generator v4
- Pixabay API (no API key needed for photos)
- Downloads images and creates animated slideshow video
- Voiceover synced to slides
- Multiple visual styles
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

# Scripts optimized for 45 second shorts
SHORT_SCRIPTS = {
    "facts": [
        {"topic": "The oldest living thing on Earth", "hook": "This tree is older than the pyramids.", "script": "Meet the oldest living thing on Earth. This ancient organism survived for over five thousand years. It witnessed the rise of empires while remaining unchanged. Scientists study it to understand longevity. Imagine what stories it could tell.", "images": ["ancient tree forest", "old oak tree", "nature huge tree"]},
        {"topic": "Why cats see in darkness", "hook": "Here's why cats see better than you in the dark.", "script": "Cats have superpowers at night. Their eyes contain a special layer called tapetum lucidum. This reflects light back through their retina, giving a second chance to detect it. That's why their eyes glow in darkness. Plus, they have more rod cells.", "images": ["cat eyes glowing", "cat night portrait", "cat hunting"]},
        {"topic": "The ocean has more gold than all governments", "hook": "There's more gold in the ocean than all gold ever mined.", "script": "Deep in our oceans lies a fortune beyond imagination. Scientists estimate billions of tons of gold dissolved in seawater. Yet it's so spread out that extracting it costs more than the gold is worth. Every liter contains about thirteen billionths of a gram.", "images": ["underwater ocean", "gold coins treasure", "ocean depth blue"]},
        {"topic": "A country that pays citizens to do nothing", "hook": "This country pays citizens to do nothing.", "script": "In Alaska, every resident receives an annual dividend from oil revenues. Started in 1982, it has continued every year since. It provides thousands of dollars to each citizen just for living there. The state believes sharing natural resources benefits everyone.", "images": ["alaska mountains", "oil platform sunset", "dollar money"]},
    ],
    "kerala": [
        {"topic": "Why Kerala has no McDonald's", "hook": "The only Indian state without a McDonald's. Here's why.", "script": "Kerala stands alone as the only Indian state without a McDonald's. The reason? Kerala's vegetarian population and religious preferences make beef off the menu. Without their signature items, opening a restaurant becomes unviable. Cultural values trump corporate expansion.", "images": ["kerala food traditional", "indian curry dish", "vegetarian cuisine color"]},
        {"topic": "The martial art that inspired all others", "hook": "This 3000 year old art inspired every action movie.", "script": "Kalaripayattu is the mother of all martial arts. Born in Kerala over three thousand years ago, it combines combat with spiritual practice. Legends say Buddha learned from Kerala masters. Bruce Lee studied its principles. Today, it remains alive in training centers.", "images": ["martial arts warrior pose", "kerala culture dance", "ancient combat"]},
        {"topic": "How Kerala became 100% literate first", "hook": "This Indian state achieved 100% literacy first.", "script": "In 1991, Kerala became the first fully literate state in India. The secret was strong government commitment to education. Even poor families prioritized schooling. Temples became schools. Community groups promoted reading. Education became a cultural value.", "images": ["books library education", "student reading", "school children learning"]},
        {"topic": "The spice that built Kerala's fortune", "hook": "This spice made Kerala one of the richest places.", "script": "Pepper built Kerala's ancient wealth. For centuries, it was worth more than gold in Europe. Kings fought wars to control Kerala's pepper trade. The monsoons and fertile soil created perfect growing conditions. This humble spice shaped global history.", "images": ["black pepper spice", "kerala market spices", "pepper harvest"]},
    ],
    "travel": [
        {"topic": "The most dangerous road on Earth", "hook": "This road has killed over 300 people in one year.", "script": "In Pakistan, the Karakoram Highway passes through territory that defies imagination. Narrow passages carved into cliffs. No guardrails. Sheer drops of thousands of meters. Fog appears without warning. Landslides are common. Yet thousands drive here yearly, drawn by the ultimate test of courage.", "images": ["mountain road cliff", "dangerous highway twist", "mountain road fog"]},
        {"topic": "The island where animals outnumber humans 100 to 1", "hook": "On this island, animals outnumber humans by 100 to 1.", "script": "In Botswana's Savute, wildlife roams freely. Lions, zebras, elephants live here. Humans are visitors, not rulers. Predators hunt using ancient techniques. Nature operates by its own rules. It's a glimpse of what our planet looked like before human dominance.", "images": ["safari elephants africa", "lion wildlife", "zebra savanna"]},
        {"topic": "The beach with pink sand", "hook": "This beach has pink sand and most don't know it exists.", "script": "On Bonaire island in the Caribbean, pink sand meets turquoise water. The color comes from crushed coral mixed with white sand. The effect is dreamlike, almost artificial. Yet it's completely natural. This hidden paradise remains uncrowded despite its beauty.", "images": ["pink beach caribbean", "tropical beach turquoise", "pink sand closeup"]},
    ],
    "quotes": [
        {"topic": "The 5 AM habit of successful people", "hook": "Every successful person shares one morning habit.", "script": "Winners wake up before the world starts moving. At five AM, distractions are zero. The mind is fresh. Energy is high. This quiet hour becomes a competitive advantage. While others sleep, winners prepare. By the time others rise, winners have already begun winning.", "images": ["sunrise morning alarm", "productive morning desk", "sunrise silhouette"]},
        {"topic": "Why consistency beats talent", "hook": "Talent will fail you. Consistency will not.", "script": "Every expert was once a beginner. What separates winners from quitters is simple. They showed up every single day. Talent gives you a head start. But consistency finishes the race. Your daily showing up is your unfair advantage. Practice beats talent.", "images": ["athlete training hard", "practice everyday", "workout discipline"]},
        {"topic": "The one thing that separates winners from losers", "hook": "Winners and losers have the same opportunities.", "script": "When faced with difficulty, losers make excuses. Winners find ways. The gap between success and failure isn't talent or luck. It's response. Your reaction to failure determines your future. Success isn't about never falling. It's about getting up every time.", "images": ["mountain peak success", "overcoming obstacles", "winning trophy"]},
    ],
    "food": [
        {"topic": "The pizza created to feed a poor family", "hook": "This pizza was created to help a poor family survive.", "script": "Margherita pizza was born in Naples during hard times. A queen visited a poor neighborhood. Nothing fancy was available. The cook made do with tomatoes, mozzarella, basil. The queen loved it. The humble dish became a symbol of Italian cuisine.", "images": ["pizza making chef", "italian pizza fresh", "tomatoes ingredients"]},
        {"topic": "Why Indian food is the most diverse", "hook": "Indian food is the most diverse cuisine on Earth.", "script": "India has over two thousand distinct cuisines. Each region speaks a different language and eats different foods. The Himalayas, deserts, coastlines, and jungles shape what's eaten. Spices here aren't just flavor. They preserve food in heat. No other country matches this diversity.", "images": ["indian spices variety", "curry masala color", "food spread indian"]},
        {"topic": "The spice once worth more than gold", "hook": "This spice was once worth more than gold.", "script": "Black pepper once cost more than gold in ancient Rome. Emperors paid fortunes for tiny quantities. Kerala was the world's only source for centuries. Explorers sought new routes to find it. Wars were fought over pepper trade. Today it sits humble in every kitchen.", "images": ["black pepper spice bowl", "spice market pile", "pepper closeup"]},
    ]
}

TARGET_DURATION = 48
WORDS_PER_SECOND = 2.5

def download_images_pixabay(queries):
    """Download images from Pixabay (no API key needed)"""
    images = []

    for query in queries:
        try:
            # Pixabay search URL (returns JSON with image URLs)
            url = f"https://pixabay.com/api/?key=47895777-cd4f4f8f91e37f8c69e01b4bb&q={quote(query)}&image_type=photo&per_page=3&orientation=vertical"

            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                if hits:
                    # Get medium resolution image
                    img = random.choice(hits)
                    img_url = img.get("webformatURL") or img.get("largeImageURL")

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

        if len(images) >= 4:
            break

    return images

def create_slideshow_video(images, audio_path, script):
    """Create slideshow video from downloaded images"""
    output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    if not images:
        # Fallback to animated gradient
        return create_animated_fallback(audio_path, script)

    # Calculate timing per image
    num_images = len(images)
    duration_per_image = TARGET_DURATION / num_images
    fade_duration = 0.5

    # Build filter for slideshow with zoom and pan effects
    filter_parts = []

    for i, img in enumerate(images):
        # Add zoom/pan effect to each image
        scale = f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.001,1.05)':d=1:s=1080x1920,fps=25"
        filter_parts.append(scale)

    # Concatenate all processed images
    if len(images) > 1:
        filter_complex = ";".join(filter_parts) + f";[out]concat=n={num_images}:v=1[out]"

        cmd = f'''ffmpeg -y {" -i " .join(images)} -filter_complex "{filter_complex}" -map "[out]" "{TEMP_DIR}/slideshow_raw.mp4"'''
        os.system(cmd)

        slideshow = TEMP_DIR / "slideshow_raw.mp4"
    else:
        slideshow = images[0]

    # Now add text overlay and audio
    hook = script["hook"][:50].replace("'", "").replace(":", "")
    topic = script["topic"][:35].replace("'", "").replace(":", "")

    # Text overlay with animation
    filter_str = f"""
    drawtext=text='{hook}':fontsize=38:fontcolor=white:borderw=4:bordercolor=black@0.9:x=(w-text_w)/2:y=h-350:enable='between(t,0,6)',
    drawtext=text='{topic}':fontsize=28:fontcolor=yellow@0.95:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=120:enable='between(t,4,{TARGET_DURATION-2})',
    drawtext=text='Follow for more facts like this':fontsize=22:fontcolor=white@0.8:x=(w-text_w)/2:y=h-80:enable='between(t,{TARGET_DURATION-5},{TARGET_DURATION})'
    """

    cmd = f'''ffmpeg -y -i "{slideshow}" -i "{audio_path}" \
            -filter_complex "{filter_str}" \
            -map 0:v -map 1:a \
            -c:v libx264 -preset medium -crf 23 \
            -c:a aac -b:a 128k \
            -t {TARGET_DURATION} \
            -shortest \
            "{output}"'''

    print("  Creating slideshow video...")
    os.system(cmd)

    if output.exists() and output.stat().st_size > 50000:
        return str(output)

    return None

def create_animated_fallback(audio_path, script):
    """Create animated video with motion background"""
    output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    hook = script["hook"][:50].replace("'", "").replace(":", "")
    topic = script["topic"][:35].replace("'", "").replace(":", "")

    # Create animated gradient with particle-like effect
    colors = ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe", "#00f2fe"]
    bg_color = random.choice(colors)

    filter_str = f"""
    drawtext=text='{hook}':fontsize=42:fontcolor=white:borderw=5:bordercolor=black@0.9:x=(w-text_w)/2:y=h-400:enable='between(t,0,6)',
    drawtext=text='{topic}':fontsize=30:fontcolor=yellow@0.95:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=150:enable='between(t,4,{TARGET_DURATION-2})'
    """

    cmd = f'''ffmpeg -y -f lavfi -i "color=c=0x{bg_color[1:]}:s=1080x1920:d={TARGET_DURATION}:r=30" \
            -f lavfi -i "color=c=0xffffff:s=100x100:d={TARGET_DURATION}:r=5" \
            -filter_complex "[1:v]scale=200:200,format=yuva420p,fade=t=out:st=4:d=1:alpha=1,colorkey=0x{bg_color[1:]}:0.01[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,{TARGET_DURATION})'" \
            -i "{audio_path}" \
            -filter_complex "{filter_str}" \
            -map 0:v -map 2:a \
            -c:v libx264 -preset medium -crf 23 \
            -c:a aac -b:a 128k \
            -t {TARGET_DURATION} \
            -shortest \
            "{output}"'''

    os.system(cmd)

    if output.exists():
        return str(output)
    return None

def generate_voiceover(text):
    """Generate voiceover using gTTS"""
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

def get_best_script():
    """Select a random script"""
    all_scripts = []
    for style, scripts in SHORT_SCRIPTS.items():
        for script in scripts:
            script["style"] = style
            all_scripts.append(script)

    script = random.choice(all_scripts)
    script["full_text"] = f"{script['hook']}. {script['script']}"
    script["estimated_duration"] = len(script["full_text"].split()) / WORDS_PER_SECOND

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
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            }
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
    """Run full pipeline"""
    print("\n" + "=" * 60)
    print(f"{CHANNEL_NAME} - SHORT CREATOR v4 (Pixabay Images)")
    print("=" * 60)

    try:
        # 1. Get script
        print("\n[1/5] Creating script...")
        script = get_best_script()
        print(f"  Topic: {script['topic']}")
        print(f"  Style: {script['style']}")

        # 2. Download images
        print("\n[2/5] Downloading images from Pixabay...")
        images = download_images_pixabay(script["images"])

        if images:
            print(f"  Got {len(images)} images")
        else:
            print("  Using animated background")

        # 3. Voiceover
        print("\n[3/5] Creating voiceover...")
        audio = generate_voiceover(script["full_text"])
        if not audio:
            raise Exception("Voiceover failed")

        # 4. Create video
        print("\n[4/5] Building video slideshow...")
        video = create_slideshow_video(images, audio, script)
        if not video:
            raise Exception("Video creation failed")

        print(f"  Video: {os.path.basename(video)}")

        # 5. Upload
        print("\n[5/5] Uploading...")
        video_id = upload_to_youtube(video, script)

        # Log
        log_file = BASE_DIR / "youtube" / "upload-log.json"
        log = json.loads(log_file.read_text()) if log_file.exists() else []
        log.append({"date": datetime.now().isoformat(), "topic": script["topic"], "video_id": video_id})
        log_file.write_text(json.dumps(log, indent=2))

        print("\n" + "=" * 60)
        print(f"[+] SUCCESS! https://www.youtube.com/shorts/{video_id}" if video_id else "[+] Video created!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[x] Error: {e}")
    finally:
        for f in TEMP_DIR.glob("*"):
            if f.is_file():
                try:
                    f.unlink()
                except:
                    pass

if __name__ == "__main__":
    run_daily()