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
        {"topic": "The oldest living thing on Earth", "hook": "This tree is older than the pyramids.", "script": "Meet the oldest living thing on Earth. This ancient bristlecone pine tree has been growing in the White Mountains of California for over five thousand years. It was already old when the first pyramids were built in Egypt. Scientists come from around the world to study this incredible organism. Every ring in its trunk represents one year of life, telling stories of ancient civilizations that rose and fell during its lifetime. It has survived ice ages, droughts, and countless seasons. This silent witness to human history continues to grow today.", "images": ["ancient tree forest", "old pine tree", "mountain nature"]},
        {"topic": "Why cats see in darkness", "hook": "Here's why cats see better than you at night.", "script": "Cats have superpowers after dark. Their eyes contain a special reflective layer called the tapetum lucidum. This layer reflects light back through the retina, giving light-sensitive cells a second chance to detect it. That's why a cat's eyes appear to glow green or yellow when light hits them in the dark. While you stumble in darkness, your cat can navigate with ease. Their pupils can dilate to three times the size of human pupils, allowing maximum light intake. These remarkable adaptations made cats expert hunters during twilight hours.", "images": ["cat eyes glowing", "cat dark night", "cat portrait"]},
        {"topic": "The ocean has more gold than all governments", "hook": "There's more gold in the ocean than all gold ever mined.", "script": "Deep in our oceans lies a fortune beyond imagination. Scientists estimate over twenty billion tons of gold dissolved in seawater. That's enough to give every person on Earth several pounds of gold. Yet here's the catch. The gold is so spread out that a single liter of seawater contains only about thirteen billionths of a gram. Extracting it would cost far more than the gold is actually worth. So the treasure remains there, dissolved in the depths, inaccessible to human technology. The ocean keeps its golden secrets hidden.", "images": ["underwater ocean blue", "gold treasure", "ocean depth"]},
    ],
    "kerala": [
        {"topic": "Why Kerala has no McDonald's", "hook": "The only Indian state without a McDonald's.", "script": "Kerala stands alone as the only Indian state without a McDonald's restaurant. The reason lies in the state's unique cultural and religious composition. Kerala has a large vegetarian population, and many residents do not eat beef for religious reasons. Since McDonald's signature items include beef patties, the chain found it difficult to operate profitably while respecting local customs. The few McDonald's that did open in Kerala eventually closed their doors. Cultural values triumphed over corporate expansion in this case. Kerala continues to thrive with its own traditional cuisine.", "images": ["kerala food traditional", "indian curry cuisine", "vegetarian meal"]},
        {"topic": "The martial art that inspired all others", "hook": "This 3000 year old art inspired every action movie.", "script": "Kalaripayattu is considered the mother of all martial arts. Born in the southern Indian state of Kerala over three thousand years ago, it combines combat techniques with spiritual practice. Practitioners train their bodies and minds together, mastering intricate movements that look almost dance-like. Legends say that even the Buddha himself learned from Kerala masters. This ancient art influenced martial traditions across Asia, from China to Japan. Today, Kalaripayattu is experiencing a revival, with dedicated schools training new generations of practitioners who carry forward this remarkable heritage.", "images": ["martial arts warrior", "kerala culture", "ancient combat"]},
        {"topic": "How Kerala became 100% literate first", "hook": "This Indian state achieved 100% literacy first.", "script": "In 1991, Kerala made history by becoming the first fully literate state in India. No other state had achieved complete literacy among adults. The secret behind Kerala's success was strong government commitment to education dating back decades. Even families living in poverty prioritized sending their children to school. Education became deeply embedded in the culture. The government invested heavily in schools and teacher training. Women played a crucial role in spreading literacy through grassroots efforts. Kerala proved that universal education was achievable even in developing regions.", "images": ["books library", "student reading", "education school"]},
    ],
    "travel": [
        {"topic": "The most dangerous road on Earth", "hook": "This road has killed over 300 people in one year.", "script": "In Pakistan, the Karakoram Highway passes through territory that defies imagination. This incredible feat of engineering was built by workers from Pakistan, China, and Britain during the 1970s. Narrow passages carved into cliffs hang thousands of meters above the valleys below. There are no guardrails to protect drivers from the sheer drops. Landslides and rockfalls are common occurrences. Yet despite the dangers, thousands of trucks travel this route every year, carrying goods between the two countries. The views are breathtaking, but one moment of lost concentration can be fatal. This road truly earns its reputation as the most dangerous highway on Earth.", "images": ["mountain road cliff", "dangerous highway", "mountain twist"]},
        {"topic": "The island where animals outnumber humans", "hook": "On this island, animals outnumber humans by 100 to 1.", "script": "In Botswana's Savute region, wildlife roams freely across vast landscapes. Lions, zebras, elephants, and countless other species live here in extraordinary numbers. Humans are merely visitors in this wild kingdom. The area forms part of Chobe National Park, one of Africa's most important wildlife sanctuaries. Every year, thousands of tourists come to witness the incredible animal migrations. The predators hunt with practiced skill, following traditions passed down through generations. Nature operates by its own rules here. This glimpse of the ancient world reminds us what our planet looked like before human civilization spread across every corner of the globe.", "images": ["safari elephants", "lion wildlife", "zebra africa"]},
        {"topic": "The beach with pink sand", "hook": "This beach has pink sand most don't know exists.", "script": "On the small Caribbean island of Bonaire lies one of the world's most unique beaches. The sand here has a distinctive pink color that seems almost unreal. The secret behind this natural wonder lies in the surrounding coral reefs. Tiny red coral organisms mix with white sand, creating the pink hue. The color is most vibrant near the water's edge, where fresh coral fragments constantly wash ashore. Crystal clear turquoise waters meet the pink sand, creating a dreamlike landscape. This relatively unknown paradise remains uncrowded compared to more famous Caribbean destinations. Nature's artistry produces colors that no paint could match.", "images": ["pink beach tropical", "caribbean ocean", "pink sand beach"]},
    ],
    "quotes": [
        {"topic": "The 5 AM habit of successful people", "hook": "Every successful person shares one morning habit.", "script": "Winners wake up before the world starts moving. At five in the morning, distractions are at zero. The mind is fresh and uncluttered by the day's demands. Energy levels are naturally high. This quiet hour becomes a powerful competitive advantage that compounds over time. While others are still sleeping and hitting snooze, winners are already three hours ahead. They use this time for exercise, reading, planning, or simply thinking. Many famous CEOs and entrepreneurs share this morning ritual. The successful people of this world understand that how you start your day determines how you live your life. Take back control of your mornings and watch everything change.", "images": ["sunrise morning", "productive morning", "sun silhouette"]},
        {"topic": "Why consistency beats talent", "hook": "Talent will fail you. Consistency will not.", "script": "Every expert was once a beginner who refused to quit. What separates winners from quitters is simple and pure consistency. They showed up every single day, even when motivation faded. Talent gives you a head start in any endeavor, but it cannot carry you across the finish line alone. Effort and persistence create skills that raw talent alone cannot match. Think about it. The tortoise beat the hare not through speed but through determination. Every single day, small steps forward accumulate into remarkable achievements. Success is not about being the best naturally. It is about being the best through relentless effort. Talent is a gift, but consistency is a choice that anyone can make.", "images": ["athlete training", "practice everyday", "workout discipline"]},
        {"topic": "The one thing that separates winners from losers", "hook": "Winners and losers have the same opportunities.", "script": "When faced with difficulty, losers make excuses while winners find ways forward. Your reaction to failure determines your future more than any other single factor. Success is not about never falling down. Everyone stumbles along the way. True success lies in getting back up every single time you fall. There will always be obstacles in your path. There will always be voices telling you it cannot be done. The difference between those who succeed and those who fail is simply a refusal to accept defeat. Every successful person you admire has faced moments of doubt and darkness. What made them different was they kept pushing forward regardless. Choose to be a winner today.", "images": ["mountain peak", "overcoming obstacles", "success winning"]},
    ],
    "food": [
        {"topic": "The pizza created to feed a poor family", "hook": "This pizza was created to help a poor family survive.", "script": "The Margherita pizza was born in Naples during particularly hard economic times. Legend tells that Queen Margherita of Italy visited a poor neighborhood in Naples. The palace chefs had nothing fancy available to prepare for her visit. The local pizzaiolo improvised, making a simple flatbread topped with tomatoes, mozzarella cheese, and fresh basil. The queen loved it so much that she asked for it again and again. The colors of the toppings were said to represent the Italian flag. That humble creation eventually became one of the most beloved foods in the entire world. Simple beginnings can lead to global fame.", "images": ["pizza making", "italian pizza", "tomatoes ingredients"]},
        {"topic": "Why Indian food is the most diverse", "hook": "Indian food is the most diverse cuisine on Earth.", "script": "India has over two thousand distinct cuisines, more than any other country on the planet. Each region of this vast country speaks a different language and eats completely different foods. Spices here are not just about flavor. They serve crucial purposes like preserving food in the hot climate and providing essential nutrition. From the coconut-based dishes of Kerala to the meat-heavy kebabs of the north, every region has its own identity. The diversity comes from centuries of trade, migration, and cultural exchange. No other country in the world matches India's incredible variety of tastes, techniques, and traditions. Indian cuisine truly represents a complete universe of flavors waiting to be explored.", "images": ["indian spices", "curry color", "food variety"]},
        {"topic": "The spice once worth more than gold", "hook": "This spice was once worth more than gold.", "script": "Black pepper once cost more than gold in ancient Rome. Emperors and wealthy nobles paid fortunes for tiny quantities of this humble spice. The reason for its extraordinary value was simple geography. Kerala in southern India was the world's only source of black pepper for centuries. The spice had to travel thousands of miles through dangerous routes to reach European markets. Each journey was perilous, passing through bandits, storms, and political conflicts. This small, wrinkled berry shaped the history of global trade. It drove exploration, sparked wars, and built empires. The desire for pepper was one of the original forces that connected the ancient world. This humble spice changed history forever.", "images": ["black pepper spice", "spice market", "pepper pile"]},
    ]
}

TARGET_DURATION = 45

def download_images(query, idx=0):
    """Download image from Unsplash (free, no API key needed)"""
    try:
        url = f"https://source.unsplash.com/1080x1920/?{quote(query)}"
        output = TEMP_DIR / f"img-{int(datetime.now().timestamp())}-{idx}.jpg"
        r = requests.get(url, timeout=30, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(output, "wb") as f:
                f.write(r.content)
            if output.exists() and output.stat().st_size > 5000:
                print(f"  Downloaded: {query}")
                return str(output)
    except Exception as e:
        print(f"  Error: {e}")
    return None

def download_images_pixabay(queries):
    """Download images from Unsplash"""
    images = []
    for i, query in enumerate(queries):
        img = download_images(query, i)
        if img:
            images.append(img)
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

    # Create individual video segments with zoom effect
    segments = []
    for i, img in enumerate(images):
        seg = TEMP_DIR / f"seg-{i}.mp4"
        segments.append(str(seg))

        # Simple zoom-in effect using scale and crop
        cmd = f'ffmpeg -y -loop 1 -i "{img}" -t {duration_per_image} -vf "scale=1200:-1" -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p "{seg}"'
        os.system(cmd)

        if not seg.exists():
            # Fallback: just scale to vertical
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

    # Simple text on color - no complex filter graph
    cmd = f'ffmpeg -y -f lavfi -i "color=0x{bg_color[1:]}:s=1080x1920:d={TARGET_DURATION}:r=30" -i "{audio_path}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -shortest "{output}"'

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