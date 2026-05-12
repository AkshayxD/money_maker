"""
YouTube Shorts Generator v9
- Per-sentence audio generation with exact timing
- Context-relevant images from Pexels (free API)
- Proper audio-video sync
"""

import os
import sys
import json
import random
import subprocess
import requests
import asyncio
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

# Scripts with per-sentence images and text
SHORT_SCRIPTS = {
    "facts": [
        {
            "topic": "The oldest living thing on Earth",
            "hook": "This tree is older than the pyramids.",
            "sentences": [
                ("Meet the oldest living thing on Earth.", "ancient bristlecone pine tree forest"),
                ("This ancient tree has been growing for over five thousand years.", "old ancient tree bark closeup"),
                ("It was already old when the first pyramids were built.", "egypt pyramids ancient world"),
                ("Scientists come from around the world to study it.", "scientist research nature"),
                ("Every ring in its trunk represents one year of history.", "tree cross section rings"),
                ("It survived ice ages and countless seasons.", "winter snow forest trees"),
                ("This silent witness continues to grow today.", "tree forest nature landscape"),
            ]
        },
        {
            "topic": "Why cats see in darkness",
            "hook": "Cats see better than you at night.",
            "sentences": [
                ("Cats have superpowers after dark.", "cat night eyes glowing"),
                ("Their eyes contain a special reflective layer.", "cat closeup eyes yellow"),
                ("This layer reflects light back through the retina.", "cat animal portrait dark"),
                ("That's why cat eyes appear to glow.", "cat glowing eyes darkness"),
                ("While you stumble in darkness, cats navigate with ease.", "cat night vision predator"),
                ("Their pupils dilate to three times human size.", "cat eyes closeup feline"),
                ("These adaptations made cats expert hunters.", "cat hunting predator wild"),
            ]
        },
        {
            "topic": "The ocean has more gold than all governments",
            "hook": "There's more gold in the ocean than ever mined.",
            "sentences": [
                ("Deep in our oceans lies a fortune beyond imagination.", "deep ocean underwater darkness"),
                ("Scientists estimate over twenty billion tons of gold.", "gold bars treasure wealth"),
                ("That's enough for everyone on Earth to have pounds of it.", "gold coins wealth money"),
                ("Yet it's so spread out that extraction costs exceed value.", "ocean waves beach coast"),
                ("The treasure remains dissolved in the depths.", "underwater ocean blue sea"),
                ("The ocean keeps its golden secrets hidden forever.", "ocean depth mysterious blue"),
            ]
        },
    ],
    "kerala": [
        {
            "topic": "Why Kerala has no McDonald's",
            "hook": "The only Indian state without a McDonald's.",
            "sentences": [
                ("Kerala stands alone as the only Indian state without McDonald's.", "india street food market"),
                ("The reason lies in the state's unique culture.", "india traditional culture colorful"),
                ("Kerala has a large vegetarian population.", "indian vegetarian food curry"),
                ("Many residents do not eat beef for religious reasons.", "india temple religious spiritual"),
                ("McDonald's signature items include beef.", "burger fast food restaurant"),
                ("The few that opened eventually closed.", "india street food vendors"),
                ("Cultural values triumphed over corporate expansion.", "india traditional market colorful"),
            ]
        },
        {
            "topic": "The martial art that inspired all others",
            "hook": "This 3000 year old art inspired action movies.",
            "sentences": [
                ("Kalaripayattu is the mother of all martial arts.", "martial arts warrior combat"),
                ("Born in Kerala over three thousand years ago.", "india kerala traditional ancient"),
                ("It combines combat techniques with spiritual practice.", "yoga meditation spiritual practice"),
                ("Practitioners master movements that look dance-like.", "martial arts movement graceful"),
                ("Legends say Buddha learned from Kerala masters.", "buddha spiritual meditation"),
                ("This ancient art influenced traditions across Asia.", "asian martial arts warrior"),
                ("Kalaripayattu is experiencing a revival today.", "martial arts training practice"),
            ]
        },
        {
            "topic": "How Kerala became 100% literate first",
            "hook": "This Indian state achieved 100% literacy first.",
            "sentences": [
                ("In 1991, Kerala became fully literate.", "books library education"),
                ("No other state had achieved complete adult literacy.", "student reading books"),
                ("The secret was strong government commitment.", "government building india"),
                ("Even families in poverty prioritized schooling.", "school children education india"),
                ("Education became deeply embedded in culture.", "education learning knowledge"),
                ("Women played a crucial role in spreading literacy.", "women education empowerment"),
                ("Kerala proved universal education was achievable.", "success achievement education"),
            ]
        },
    ],
    "travel": [
        {
            "topic": "The most dangerous road on Earth",
            "hook": "This road has killed hundreds of people.",
            "sentences": [
                ("In Pakistan, the Karakoram Highway passes through terrifying territory.", "pakistan mountain road himalayas"),
                ("This incredible road was built during the 1970s.", "mountain road engineering construction"),
                ("Narrow passages hang thousands of meters above valleys.", "mountain cliff edge dangerous"),
                ("There are no guardrails to protect drivers.", "mountain road no barrier edge"),
                ("Landslides and rockfalls are common here.", "mountain landslide rocks falling"),
                ("Yet thousands of trucks travel this route yearly.", "trucks highway mountain road"),
                ("This is the most dangerous highway on Earth.", "dangerous road mountain extreme"),
            ]
        },
        {
            "topic": "The island where animals outnumber humans",
            "hook": "Animals outnumber humans by 100 to 1 here.",
            "sentences": [
                ("In Botswana, wildlife roams freely.", "africa safari elephants wildlife"),
                ("Lions, zebras, and elephants live here in numbers.", "safari lions zebras wildlife"),
                ("Humans are merely visitors in this wild kingdom.", "safari wilderness nature africa"),
                ("The area forms part of Chobe National Park.", "africa national park safari"),
                ("Every year, thousands witness the animal migrations.", "elephant migration africa savanna"),
                ("Nature operates by its own rules here.", "wildlife nature africa savanna"),
                ("This glimpse reminds us of our planet's past.", "africa sunset wilderness nature"),
            ]
        },
        {
            "topic": "The beach with pink sand",
            "hook": "This beach has pink sand most don't know.",
            "sentences": [
                ("On Bonaire island in the Caribbean lies this unique beach.", "caribbean tropical island beach"),
                ("The sand has a distinctive pink color.", "pink beach sand tropical"),
                ("The color comes from red coral mixed with white sand.", "coral reef ocean underwater"),
                ("Crystal clear turquoise waters meet the pink sand.", "turquoise water beach caribbean"),
                ("This creates a dreamlike landscape.", "paradise beach tropical beautiful"),
                ("This unknown paradise remains uncrowded.", "empty beach tropical peaceful"),
                ("Nature's artistry produces colors no paint could match.", "sunset beach beautiful colors"),
            ]
        },
    ],
    "quotes": [
        {
            "topic": "The 5 AM habit of successful people",
            "hook": "Every successful person shares one morning habit.",
            "sentences": [
                ("Winners wake up before the world starts moving.", "sunrise morning early dawn"),
                ("At five in the morning, distractions are zero.", "quiet morning peaceful sunrise"),
                ("The mind is fresh and uncluttered.", "meditation peaceful calm morning"),
                ("This quiet hour becomes a competitive advantage.", "success achievement morning motivation"),
                ("While others sleep, winners are already ahead.", "sunrise early morning productivity"),
                ("They use this time for exercise and planning.", "morning workout exercise fitness"),
                ("Take back control of your mornings and change everything.", "success motivation sunrise achievement"),
            ]
        },
        {
            "topic": "Why consistency beats talent",
            "hook": "Talent will fail you. Consistency will not.",
            "sentences": [
                ("Every expert was once a beginner who refused to quit.", "athlete beginner training"),
                ("What separates winners from quitters is consistency.", "athlete training discipline"),
                ("They showed up every single day.", "daily workout gym training"),
                ("Talent gives you a head start but cannot carry you.", "runner race starting line"),
                ("Effort and persistence create skills talent cannot match.", "training practice improvement"),
                ("Small steps accumulate into remarkable achievements.", "mountain climb achievement summit"),
                ("Talent is a gift, but consistency is a choice.", "discipline determination success"),
            ]
        },
        {
            "topic": "The one thing that separates winners from losers",
            "hook": "Winners and losers have the same opportunities.",
            "sentences": [
                ("When faced with difficulty, losers make excuses.", "mountain obstacle challenge"),
                ("Winners find ways forward instead.", "mountain peak success summit"),
                ("Your reaction to failure determines your future.", "overcoming challenge determination"),
                ("Success is not about never falling down.", "falling getting up perseverance"),
                ("True success lies in getting back up every time.", "stand up determination rising"),
                ("Every successful person has faced doubt.", "darkness night struggle perseverance"),
                ("What made them different was refusing to accept defeat.", "victory winning champion success"),
            ]
        },
    ],
    "food": [
        {
            "topic": "The pizza created to feed a poor family",
            "hook": "This pizza was created to help a poor family.",
            "sentences": [
                ("The Margherita pizza was born in Naples during hard times.", "italian pizza restaurant naples"),
                ("Queen Margherita visited a poor neighborhood.", "queen royal palace italy"),
                ("The palace chefs had nothing fancy available.", "simple food basic cooking"),
                ("The local cook improvised with tomatoes, mozzarella, and basil.", "pizza ingredients fresh basil"),
                ("The queen loved it and asked for more.", "happy satisfied delicious food"),
                ("That humble creation became world-famous.", "famous pizza italian food"),
                ("Simple beginnings can lead to global fame.", "success humble beginning achievement"),
            ]
        },
        {
            "topic": "Why Indian food is the most diverse",
            "hook": "Indian food is the most diverse cuisine on Earth.",
            "sentences": [
                ("India has over two thousand distinct cuisines.", "indian food curry spices colorful"),
                ("Each region speaks a different language and eats different foods.", "india diverse culture market"),
                ("Spices here are not just about flavor.", "indian spices colorful market"),
                ("They preserve food and provide nutrition.", "indian cooking traditional spices"),
                ("From coconut Kerala dishes to northern kebabs.", "kerala food coconut curry south india"),
                ("The diversity comes from centuries of exchange.", "india spice market trade"),
                ("Indian cuisine represents a universe of flavors.", "indian food variety colorful delicious"),
            ]
        },
        {
            "topic": "The spice once worth more than gold",
            "hook": "This spice was once worth more than gold.",
            "sentences": [
                ("Black pepper once cost more than gold in ancient Rome.", "black pepper spices market"),
                ("Emperors paid fortunes for tiny quantities.", "roman emperor ancient wealth"),
                ("Kerala was the world's only source for centuries.", "kerala india spice plantation"),
                ("The spice traveled thousands of miles through dangerous routes.", "silk road trade ancient journey"),
                ("This small berry shaped global trade history.", "trade route ships ocean voyage"),
                ("It drove exploration and built empires.", "exploration discovery new worlds"),
                ("This humble spice changed history forever.", "spice history ancient trade"),
            ]
        },
    ]
}

def get_audio_duration(audio_path):
    """Get audio duration in seconds using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except:
        return 0

async def generate_audio_segment(text, output_path):
    """Generate audio for a single sentence using edge-tts"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        print(f"  Edge-TTS error: {e}")
        return False

def download_image(search_term, idx, timestamp):
    """Download image from Pexels (free, reliable)"""
    try:
        output = TEMP_DIR / f"img-{timestamp}-{idx}.jpg"

        # Use Unsplash Source with better queries
        query = quote(search_term.replace(' ', '+'))
        url = f"https://source.unsplash.com/1080x1920/?{query}"

        r = requests.get(url, timeout=30, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 10000:
            with open(output, "wb") as f:
                f.write(r.content)
            if output.exists() and output.stat().st_size > 10000:
                return str(output)
    except Exception as e:
        print(f"  Image error: {e}")
    return None

def create_image_segment(image_path, duration, output_path):
    """Create a video segment from an image"""
    if not image_path or not Path(image_path).exists():
        # Fallback to gradient background
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'color=0x667eea:s=1080x1920:d={duration}:r=30',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-pix_fmt', 'yuv420p', str(output_path)
        ]
        subprocess.run(cmd, capture_output=True)
        return output_path.exists()

    # Scale and crop to 9:16 without stretching
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

def concatenate_videos(video_list, output_path):
    """Concatenate multiple video segments"""
    if not video_list:
        return False

    list_file = TEMP_DIR / "concat.txt"
    with open(list_file, "w") as f:
        for v in video_list:
            f.write(f"file '{v}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(list_file),
        '-c', 'copy', str(output_path)
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path.exists()

def concatenate_audio(audio_list, output_path):
    """Concatenate multiple audio segments"""
    if not audio_list:
        return False

    list_file = TEMP_DIR / "audio_concat.txt"
    with open(list_file, "w") as f:
        for a in audio_list:
            f.write(f"file '{a}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(list_file),
        '-c', 'copy', str(output_path)
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path.exists()

def create_final_video(video_path, audio_path, output_path):
    """Combine video and audio"""
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-i', str(audio_path),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-shortest',
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path.exists()

def get_best_script():
    """Select a random script"""
    all_scripts = []
    for style, scripts in SHORT_SCRIPTS.items():
        for script in scripts:
            script["style"] = style
            all_scripts.append(script)
    return random.choice(all_scripts)

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
    print(f"{CHANNEL_NAME} - SHORT CREATOR v9")
    print("=" * 60)

    timestamp = int(datetime.now().timestamp())

    try:
        # 1. Script
        print("\n[1/5] Creating script...")
        script = get_best_script()
        print(f"  Topic: {script['topic']}")
        print(f"  Sentences: {len(script['sentences'])}")

        # 2. Generate audio and download images per sentence
        print("\n[2/5] Creating audio segments...")
        audio_segments = []
        image_segments = []
        total_duration = 0

        for idx, (text, image_query) in enumerate(script['sentences']):
            # Generate audio for this sentence
            audio_seg = TEMP_DIR / f"audio-{timestamp}-{idx}.mp3"
            success = asyncio.run(generate_audio_segment(text, str(audio_seg)))

            if success and audio_seg.exists():
                dur = get_audio_duration(str(audio_seg))
                audio_segments.append(str(audio_seg))
                print(f"  [{idx+1}] {text[:40]}... ({dur:.1f}s)")
                total_duration += dur
            else:
                # Fallback: create silent segment
                audio_segments.append(None)
                print(f"  [{idx+1}] {text[:40]}... (silent fallback)")

            # Download image for this sentence
            img = download_image(image_query, idx, timestamp)
            image_segments.append(img)

        print(f"  Total audio duration: {total_duration:.1f}s")

        if not audio_segments:
            raise Exception("No audio generated")

        # 3. Concatenate all audio
        print("\n[3/5] Combining audio...")
        full_audio = TEMP_DIR / f"full-audio-{timestamp}.mp3"
        valid_audio = [a for a in audio_segments if a and Path(a).exists()]

        if len(valid_audio) == 1:
            Path(valid_audio[0]).rename(full_audio)
        elif len(valid_audio) > 1:
            concatenate_audio(valid_audio, str(full_audio))

        if not full_audio.exists():
            raise Exception("Audio concatenation failed")

        final_audio_duration = get_audio_duration(str(full_audio))
        print(f"  Final audio duration: {final_audio_duration:.1f}s")

        # 4. Create video segments synced to audio
        print("\n[4/5] Building video...")

        # Recalculate durations based on actual audio
        video_segments = []
        segment_durations = []

        for idx, audio_seg in enumerate(audio_segments):
            if audio_seg and Path(audio_seg).exists():
                dur = get_audio_duration(audio_seg)
            else:
                # Distribute remaining time among silent segments
                remaining = final_audio_duration - sum(segment_durations)
                silent_count = sum(1 for a in audio_segments[idx:] if not a or not Path(a).exists())
                dur = remaining / silent_count if silent_count > 0 else 3.0

            segment_durations.append(dur)

            # Adjust image duration to match audio
            seg = TEMP_DIR / f"seg-{timestamp}-{idx}.mp4"
            img = image_segments[idx]

            # Extend image duration to match audio duration
            if img and Path(img).exists():
                # Loop the image for the full duration
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1', '-i', img,
                    '-t', str(dur),
                    '-vf', 'scale=1920:1920:force_original_aspect_ratio=increase,crop=1080:1920',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-pix_fmt', 'yuv420p', '-r', '30',
                    str(seg)
                ]
                subprocess.run(cmd, capture_output=True)
            else:
                # Fallback color
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi', '-i', f'color=0x667eea:s=1080x1920:d={dur}:r=30',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-pix_fmt', 'yuv420p', str(seg)
                ]
                subprocess.run(cmd, capture_output=True)

            if seg.exists():
                video_segments.append(str(seg))

        if not video_segments:
            raise Exception("No video segments created")

        # Concatenate video
        print("  Concatenating video segments...")
        concat_video = TEMP_DIR / f"concat-video-{timestamp}.mp4"
        concatenate_videos(video_segments, str(concat_video))

        if not concat_video.exists():
            raise Exception("Video concatenation failed")

        # 5. Combine video and audio
        print("\n[5/5] Combining video and audio...")
        output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

        # Ensure video length matches audio
        cmd = [
            'ffmpeg', '-y',
            '-i', str(concat_video),
            '-i', str(full_audio),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-t', str(final_audio_duration),
            str(output)
        ]
        subprocess.run(cmd, capture_output=True)

        if not output.exists():
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