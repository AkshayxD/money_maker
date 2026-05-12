"""
YouTube Shorts Generator v8
- Proper 9:16 vertical video (1080x1920)
- Synced visuals: images change with narration sections
- Natural voice with edge-tts
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

# Scripts split into sentences for timing sync
SHORT_SCRIPTS = {
    "facts": [
        {"topic": "The oldest living thing on Earth", "hook": "This tree is older than the pyramids.", "sentences": [
            ("Meet the oldest living thing on Earth.", ["forest", "tree", "nature"]),
            ("This ancient bristlecone pine tree has been growing in California for over five thousand years.", ["tree", "ancient", "forest"]),
            ("It was already old when the first pyramids were built in Egypt.", ["pyramids", "ancient", "egypt"]),
            ("Scientists come from around the world to study this incredible organism.", ["scientist", "research", "nature"]),
            ("Every ring in its trunk represents one year of life.", ["tree", "rings", "nature"]),
            ("It has survived ice ages, droughts, and countless seasons.", ["winter", "snow", "nature"]),
            ("This silent witness to human history continues to grow today.", ["tree", "forest", "nature"]),
        ]},
        {"topic": "Why cats see in darkness", "hook": "Here's why cats see better than you at night.", "sentences": [
            ("Cats have superpowers after dark.", ["cat", "animal", "night"]),
            ("Their eyes contain a special reflective layer called the tapetum lucidum.", ["cat eyes", "animal", "nature"]),
            ("This layer reflects light back through the retina.", ["cat", "animal", "glowing"]),
            ("That's why a cat's eyes appear to glow green or yellow.", ["cat eyes", "animal", "glowing"]),
            ("While you stumble in darkness, your cat can navigate with ease.", ["cat", "animal", "night"]),
            ("Their pupils can dilate to three times the size of human pupils.", ["cat", "animal", "eyes"]),
            ("These adaptations made cats expert hunters during twilight hours.", ["cat", "hunter", "wild"]),
        ]},
        {"topic": "The ocean has more gold than all governments", "hook": "There's more gold in the ocean than all gold ever mined.", "sentences": [
            ("Deep in our oceans lies a fortune beyond imagination.", ["ocean", "underwater", "sea"]),
            ("Scientists estimate over twenty billion tons of gold dissolved in seawater.", ["gold", "treasure", "ocean"]),
            ("That's enough to give every person on Earth several pounds of gold.", ["gold", "treasure", "wealth"]),
            ("Yet the gold is so spread out that extraction costs more than its worth.", ["ocean", "underwater", "depths"]),
            ("The treasure remains dissolved in the depths, inaccessible.", ["ocean", "underwater", "deep"]),
            ("The ocean keeps its golden secrets hidden forever.", ["ocean", "underwater", "sea"]),
        ]},
    ],
    "kerala": [
        {"topic": "Why Kerala has no McDonald's", "hook": "The only Indian state without a McDonald's.", "sentences": [
            ("Kerala stands alone as the only Indian state without a McDonald's.", ["india", "food", "curry"]),
            ("The reason lies in the state's unique cultural composition.", ["india", "culture", "traditional"]),
            ("Kerala has a large vegetarian population.", ["vegetarian", "food", "healthy"]),
            ("Many residents do not eat beef for religious reasons.", ["india", "temple", "religion"]),
            ("McDonald's signature items include beef patties.", ["food", "burger", "restaurant"]),
            ("The few McDonald's that opened eventually closed their doors.", ["india", "street food", "market"]),
            ("Cultural values triumphed over corporate expansion.", ["india", "culture", "traditional"]),
        ]},
        {"topic": "The martial art that inspired all others", "hook": "This 3000 year old art inspired every action movie.", "sentences": [
            ("Kalaripayattu is the mother of all martial arts.", ["martial arts", "combat", "warrior"]),
            ("Born in Kerala over three thousand years ago.", ["india", "kerala", "traditional"]),
            ("It combines combat techniques with spiritual practice.", ["martial arts", "yoga", "meditation"]),
            ("Practitioners master intricate movements that look almost dance-like.", ["martial arts", "dance", "movement"]),
            ("Legends say that even Buddha learned from Kerala masters.", ["buddha", "india", "spiritual"]),
            ("This ancient art influenced martial traditions across Asia.", ["martial arts", "warrior", "combat"]),
            ("Kalaripayattu is experiencing a revival today.", ["martial arts", "india", "traditional"]),
        ]},
        {"topic": "How Kerala became 100% literate first", "hook": "This Indian state achieved 100% literacy first.", "sentences": [
            ("In 1991, Kerala became the first fully literate state in India.", ["books", "education", "india"]),
            ("No other state had achieved complete adult literacy.", ["library", "reading", "books"]),
            ("The secret was strong government commitment to education.", ["education", "school", "learning"]),
            ("Even families living in poverty prioritized schooling.", ["education", "india", "school"]),
            ("Education became deeply embedded in the culture.", ["books", "learning", "culture"]),
            ("Women played a crucial role in spreading literacy.", ["women", "education", "india"]),
            ("Kerala proved universal education was achievable.", ["education", "success", "india"]),
        ]},
    ],
    "travel": [
        {"topic": "The most dangerous road on Earth", "hook": "This road has killed over 300 people in one year.", "sentences": [
            ("In Pakistan, the Karakoram Highway passes through terrifying territory.", ["mountain", "road", "cliffs"]),
            ("This incredible road was built during the 1970s.", ["mountain", "highway", "engineering"]),
            ("Narrow passages hang thousands of meters above the valleys.", ["mountain", "cliffs", "danger"]),
            ("There are no guardrails to protect drivers.", ["mountain", "road", "cliffs"]),
            ("Landslides and rockfalls are common occurrences.", ["mountain", "landslide", "danger"]),
            ("Yet thousands of trucks travel this route every year.", ["truck", "highway", "travel"]),
            ("This road truly earns its reputation as the most dangerous on Earth.", ["mountain", "danger", "road"]),
        ]},
        {"topic": "The island where animals outnumber humans", "hook": "On this island, animals outnumber humans by 100 to 1.", "sentences": [
            ("In Botswana's Savute, wildlife roams freely.", ["safari", "elephants", "africa"]),
            ("Lions, zebras, and elephants live here in extraordinary numbers.", ["safari", "wildlife", "africa"]),
            ("Humans are merely visitors in this wild kingdom.", ["safari", "wilderness", "nature"]),
            ("The area forms part of Chobe National Park.", ["safari", "park", "africa"]),
            ("Every year, thousands of tourists witness the animal migrations.", ["safari", "elephants", "migration"]),
            ("Nature operates by its own rules here.", ["safari", "wildlife", "nature"]),
            ("This glimpse of the ancient world reminds us of our planet's past.", ["safari", "wilderness", "nature"]),
        ]},
        {"topic": "The beach with pink sand", "hook": "This beach has pink sand most don't know exists.", "sentences": [
            ("On Bonaire island in the Caribbean lies a unique beach.", ["beach", "tropical", "caribbean"]),
            ("The sand has a distinctive pink color.", ["pink beach", "sand", "tropical"]),
            ("The color comes from tiny red coral mixed with white sand.", ["coral", "beach", "ocean"]),
            ("Crystal clear turquoise waters meet the pink sand.", ["beach", "ocean", "caribbean"]),
            ("This creates a dreamlike landscape.", ["beach", "paradise", "tropical"]),
            ("This unknown paradise remains uncrowded.", ["beach", "empty", "tropical"]),
            ("Nature's artistry produces colors that no paint could match.", ["beach", "sunset", "ocean"]),
        ]},
    ],
    "quotes": [
        {"topic": "The 5 AM habit of successful people", "hook": "Every successful person shares one morning habit.", "sentences": [
            ("Winners wake up before the world starts moving.", ["sunrise", "morning", "motivation"]),
            ("At five in the morning, distractions are at zero.", ["sunrise", "morning", "early"]),
            ("The mind is fresh and uncluttered by the day's demands.", ["meditation", "peaceful", "morning"]),
            ("This quiet hour becomes a competitive advantage.", ["sunrise", "success", "motivation"]),
            ("While others sleep, winners are already three hours ahead.", ["sunrise", "morning", "productivity"]),
            ("They use this time for exercise, reading, and planning.", ["workout", "reading", "morning"]),
            ("Take back control of your mornings and watch everything change.", ["sunrise", "motivation", "success"]),
        ]},
        {"topic": "Why consistency beats talent", "hook": "Talent will fail you. Consistency will not.", "sentences": [
            ("Every expert was once a beginner who refused to quit.", ["athlete", "training", "practice"]),
            ("What separates winners from quitters is pure consistency.", ["athlete", "discipline", "training"]),
            ("They showed up every single day, even when motivation faded.", ["workout", "training", "discipline"]),
            ("Talent gives you a head start but cannot carry you across the finish line.", ["athlete", "running", "race"]),
            ("Effort and persistence create skills talent alone cannot match.", ["training", "gym", "workout"]),
            ("Small steps forward accumulate into remarkable achievements.", ["athlete", "mountain", "success"]),
            ("Talent is a gift, but consistency is a choice anyone can make.", ["athlete", "training", "discipline"]),
        ]},
        {"topic": "The one thing that separates winners from losers", "hook": "Winners and losers have the same opportunities.", "sentences": [
            ("When faced with difficulty, losers make excuses.", ["mountain", "obstacle", "challenge"]),
            ("Winners find ways forward instead.", ["mountain peak", "success", "victory"]),
            ("Your reaction to failure determines your future.", ["overcoming", "challenge", "success"]),
            ("Success is not about never falling down.", ["falling", "getting up", "persistence"]),
            ("True success lies in getting back up every single time.", ["mountain peak", "success", "victory"]),
            ("Every successful person has faced moments of doubt.", ["mountain", "darkness", "challenge"]),
            ("What made them different was refusing to accept defeat.", ["mountain peak", "success", "winning"]),
        ]},
    ],
    "food": [
        {"topic": "The pizza created to feed a poor family", "hook": "This pizza was created to help a poor family survive.", "sentences": [
            ("The Margherita pizza was born in Naples during hard times.", ["pizza", "italian", "food"]),
            ("Queen Margherita visited a poor neighborhood in Naples.", ["italy", "queen", "palace"]),
            ("The palace chefs had nothing fancy available.", ["italian food", "restaurant", "cooking"]),
            ("The local pizzaiolo improvised with tomatoes, mozzarella, and basil.", ["pizza", "ingredients", "cooking"]),
            ("The queen loved it so much she asked for it again.", ["pizza", "italian", "food"]),
            ("That humble creation became one of the world's most beloved foods.", ["pizza", "italian", "restaurant"]),
            ("Simple beginnings can lead to global fame.", ["pizza", "italian", "food"]),
        ]},
        {"topic": "Why Indian food is the most diverse", "hook": "Indian food is the most diverse cuisine on Earth.", "sentences": [
            ("India has over two thousand distinct cuisines.", ["indian food", "spices", "curry"]),
            ("Each region speaks a different language and eats different foods.", ["india", "cultural", "diversity"]),
            ("Spices here are not just about flavor.", ["spices", "indian food", "colorful"]),
            ("They preserve food and provide essential nutrition.", ["spices", "cooking", "ingredients"]),
            ("From coconut-based Kerala dishes to northern kebabs.", ["curry", "kerala", "indian food"]),
            ("The diversity comes from centuries of cultural exchange.", ["india", "market", "spices"]),
            ("Indian cuisine truly represents a universe of flavors.", ["indian food", "curry", "spices"]),
        ]},
        {"topic": "The spice once worth more than gold", "hook": "This spice was once worth more than gold.", "sentences": [
            ("Black pepper once cost more than gold in ancient Rome.", ["pepper", "spice", "market"]),
            ("Emperors paid fortunes for tiny quantities.", ["gold", "treasure", "wealth"]),
            ("Kerala was the world's only source for centuries.", ["india", "kerala", "spices"]),
            ("The spice traveled thousands of miles through dangerous routes.", ["silk road", "trade", "journey"]),
            ("This small berry shaped the history of global trade.", ["spice", "market", "trade"]),
            ("It drove exploration and built empires.", ["exploration", "ships", "discovery"]),
            ("This humble spice changed history forever.", ["pepper", "spice", "history"]),
        ]},
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
        return 45

def download_image(query, idx, timestamp):
    """Download a single image from Lorem Picsum"""
    try:
        output = TEMP_DIR / f"img-{timestamp}-{idx}.jpg"
        # Use fixed seeds for consistent images
        url = f"https://picsum.photos/seed/{query.replace(' ', '')}/1080/1920"
        r = requests.get(url, timeout=30, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(output, "wb") as f:
                f.write(r.content)
            if output.exists() and output.stat().st_size > 5000:
                return str(output)
    except Exception as e:
        print(f"  Image error: {e}")
    return None

async def generate_voiceover_edge(text):
    """Generate voiceover using edge-tts"""
    try:
        import edge_tts
        output = TEMP_DIR / f"voice-{int(datetime.now().timestamp())}.mp3"
        communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
        await communicate.save(str(output))
        return str(output)
    except Exception as e:
        print(f"  Edge-TTS error: {e}")
        return None

def generate_voiceover(text):
    """Generate voiceover"""
    audio = asyncio.run(generate_voiceover_edge(text))
    if not audio:
        try:
            from gtts import gTTS
            output = TEMP_DIR / f"voice-{int(datetime.now().timestamp())}.mp3"
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(str(output))
            return str(output)
        except:
            return None
    return audio

def estimate_sentence_duration(sentence):
    """Estimate duration based on word count (average 4 words/second for natural speech)"""
    words = len(sentence.split())
    return max(2.0, words / 4.0)  # Minimum 2 seconds

def download_sentence_images(sentences):
    """Download images for each sentence section"""
    timestamp = int(datetime.now().timestamp())
    sentence_images = []

    for idx, (sentence, queries) in enumerate(sentences):
        img = download_image(queries[0], idx, timestamp)
        if not img:
            img = download_image("nature", idx, timestamp)
        sentence_images.append(img)
        print(f"  Section {idx+1}: {sentence[:40]}...")

    return sentence_images

def create_synced_video(sentences, sentence_images, audio_path):
    """Create video with images synced to sentence timing"""
    output = UPLOADS_DIR / f"short-{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"

    # Calculate durations for each section
    durations = [estimate_sentence_duration(s[0]) for s in sentences]
    total_duration = sum(durations)

    print(f"  Total video duration: {total_duration:.1f}s")
    print(f"  Creating {len(sentences)} sections")

    # Create video segments for each sentence
    segments = []
    for idx, (sentence, queries) in enumerate(sentences):
        img = sentence_images[idx] if idx < len(sentence_images) else None
        duration = durations[idx]
        seg = TEMP_DIR / f"seg-{idx}.mp4"

        if img and Path(img).exists():
            # Create segment with image - proper 9:16 crop (not stretch)
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', img,
                '-t', str(duration),
                '-vf', 'scale=1920:1920:force_original_aspect_ratio=increase,crop=1080:1920',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-pix_fmt', 'yuv420p', '-r', '30',
                str(seg)
            ]
        else:
            # Fallback: use solid color
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi', '-i', f'color=0x667eea:s=1080x1920:d={duration}:r=30',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p',
                str(seg)
            ]

        subprocess.run(cmd, capture_output=True)
        if seg.exists():
            segments.append(str(seg))

    if not segments:
        print("  No segments created")
        return None

    # Concatenate all segments
    list_file = TEMP_DIR / "segments.txt"
    with open(list_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")

    concat_output = TEMP_DIR / "concat-video.mp4"
    cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_file), '-c', 'copy', str(concat_output)]
    subprocess.run(cmd, capture_output=True)

    if not concat_output.exists():
        print("  Concatenation failed")
        return None

    # Add audio to video
    cmd = [
        'ffmpeg', '-y',
        '-i', str(concat_output),
        '-i', audio_path,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-shortest',
        str(output)
    ]
    subprocess.run(cmd, capture_output=True)

    if output.exists():
        return str(output)

    print("  Failed to add audio")
    return None

def get_best_script():
    """Select and prepare script"""
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
    print(f"{CHANNEL_NAME} - SHORT CREATOR v8")
    print("=" * 60)

    try:
        # 1. Script
        print("\n[1/5] Creating script...")
        script = get_best_script()
        print(f"  Topic: {script['topic']}")
        print(f"  Sections: {len(script['sentences'])}")

        # 2. Images (synced to sentences)
        print("\n[2/5] Downloading images...")
        sentence_images = download_sentence_images(script["sentences"])
        print(f"  Downloaded {len([i for i in sentence_images if i])} images")

        # 3. Voiceover (full text)
        print("\n[3/5] Creating voiceover...")
        full_text = script['hook'] + ' ' + ' '.join([s[0] for s in script['sentences']])
        audio = generate_voiceover(full_text)
        if not audio:
            raise Exception("Voiceover failed")
        print(f"  Audio created: {full_text[:50]}...")

        # 4. Video (synced)
        print("\n[4/5] Building synced video...")
        video = create_synced_video(script['sentences'], sentence_images, audio)
        if not video:
            raise Exception("Video creation failed")

        # 5. Upload
        print("\n[5/5] Uploading...")
        video_id = upload_to_youtube(video, script)

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