"""
YouTube Script Generator - Create video scripts for AI-powered YouTube
Usage: python youtube_script.py [topic] [style]
"""

import json
import os
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent.parent / "youtube" / "scripts"
THUMBNAILS_DIR = Path(__file__).parent.parent / "youtube" / "thumbnails"

STYLES = {
    "facts": {"name": "Facts You Never Knew", "duration": "45-60s", "hook": ["You won't believe this...", "99% don't know this...", "This will blow your mind..."]},
    "quotes": {"name": "Motivational Quotes", "duration": "60-90s", "hook": ["Your daily motivation...", "Need inspiration? Watch this...", "Save this for a bad day..."]},
    "travel": {"name": "Travel Destinations", "duration": "60-120s", "hook": ["This place looks like paradise...", "Is this the most beautiful...", "Hidden gem alert..."]},
    "kerala": {"name": "Kerala Special", "duration": "60-90s", "hook": ["Kerala is unlike anywhere...", "God's Own Country...", "The magic of Kerala..."]},
    "cooking": {"name": "Food & Recipes", "duration": "60-180s", "hook": ["This recipe changed my life...", "Secret ingredient is...", "Make this once..."]}
}

KERALA_TOPICS = [
    "Backwater houseboat ride",
    "Why Kerala monsoon is magical",
    "Hidden beaches in Kerala",
    "Traditional Kerala breakfast",
    "Kathakali dance explained",
    "Munnar tea plantations",
    "Ayurvedic healing secrets",
    "Onam festival traditions"
]

VIRAL_TOPICS = [
    "Mysterious places that exist",
    "Facts about the ocean",
    "Ancient buildings unexplained",
    "What happens when you sleep",
    "Foods invented by accident",
    "Animals older than dinosaurs",
    "Places like alien planets"
]

QUOTES = {
    "success": ["The only limit is your mind.", "Dream big, work harder.", "Success is built one day at a time."],
    "happiness": ["Happiness is a choice.", "Find joy in the little things.", "Be content with what you have."],
    "courage": ["Be brave enough to be different.", "Face your fears head-on.", "Courage is not absence of fear."]
}

def generate_script(topic: str, style: str = "facts") -> dict:
    template = STYLES.get(style, STYLES["facts"])
    hook = template["hook"][0]

    script = {
        "metadata": {
            "topic": topic,
            "style": template["name"],
            "duration": template["duration"],
            "generated": datetime.now().isoformat()
        },
        "sections": [],
        "video_assets": {
            "required": ["Hook clip (3s)", "Intro animation (2s)", "Main content clips (30s)", "Outro (5s)"],
            "sources": ["pexels.com", "pixabay.com", "coverr.co"],
            "music": ["pixabay.com/music", "freesound.org"]
        }
    }

    # Hook
    script["sections"].append({
        "time": "0:00",
        "type": "HOOK",
        "text": hook,
        "visual": "Use most stunning clip, text overlay: " + hook,
        "audio": "Upbeat background music",
        "note": "Keep viewers - 3 seconds max!"
    })

    # Intro
    intros = {
        "facts": f"Today we're diving into {topic}...",
        "quotes": "Here's a collection to change your perspective...",
        "travel": f"Welcome to {topic} - breathtaking views...",
        "kerala": f"Welcome to God's Own Country! Today: {topic}...",
        "cooking": f"Today we're making {topic}..."
    }
    script["sections"].append({
        "time": "0:03",
        "type": "INTRO",
        "text": intros.get(style, f"Today: {topic}"),
        "visual": "Brand intro template",
        "audio": "Transition music",
        "note": "Under 5 seconds"
    })

    # Main content
    contents = {
        "facts": generate_facts_content(topic),
        "quotes": generate_quotes_content(),
        "travel": generate_travel_content(topic),
        "kerala": generate_kerala_content(topic),
        "cooking": generate_cooking_content(topic)
    }
    script["sections"].append({
        "time": "0:10",
        "type": "MAIN CONTENT",
        "text": contents.get(style, f"Everything about {topic}..."),
        "visual": "Stock clips from Pexels/Pixabay",
        "audio": "Background music + voiceover",
        "note": "~150 words/min"
    })

    # Outro
    script["sections"].append({
        "time": "0:45",
        "type": "OUTRO",
        "text": "If this was valuable, give it a thumbs up! Subscribe for more! See you next time!",
        "visual": "End screen with subscribe button",
        "audio": "Outro music fade",
        "note": "Critical for YouTube algorithm"
    })

    return script

def generate_facts_content(topic: str) -> str:
    return f"""Here's what you need to know about {topic}:

First - this will change how you see the world.

Second - most people have no idea about this, but it's been right here all along.

Third - once you learn this, you can't unsee it.

And here's the most surprising part...

The world is full of amazing things we never learned in school. Keep learning, keep growing!"""

def generate_quotes_content() -> str:
    import random
    theme = random.choice(list(QUOTES.keys()))
    quotes_list = QUOTES[theme]
    theme_name = theme.capitalize()

    content = f"Today's collection is about {theme_name}. Save these for a rainy day:\n\n"
    for i, q in enumerate(quotes_list, 1):
        content += f"{i}. \"{q}\"\n   Take a moment to let that sink in.\n\n"
    content += "\nRemember: words have power. Which resonated with you?"
    return content

def generate_travel_content(topic: str) -> str:
    return f"""Here's what makes {topic} special:

The scenery will take your breath away - views nothing compares to.

The local culture is vibrant, with traditions passed down generations.

The food is a must-try - every dish tells a story of the land.

The people are warm and welcoming, proud of their heritage.

That's what makes this place unique. Put it on your bucket list!"""

def generate_kerala_content(topic: str) -> str:
    return f"""Kerala has something unique for everyone:

The backwaters offer peace unlike anywhere else on Earth.

The hill stations provide cool climates and tea views stretching forever.

The beaches are pristine - golden sands and swaying palms.

The food is a burst of flavors - fresh spices and coastal ingredients.

And the people? Warm, welcoming, proud of their heritage.

That's the magic of God's Own Country."""

def generate_cooking_content(topic: str) -> str:
    return f"""Here's how to make the perfect {topic}:

First - gather your ingredients. Quality matters.

The key is in the preparation - take your time here.

Watch the heat carefully - this is where most go wrong.

And here's the secret: add just a little more time than you think.

The result should smell amazing and look even better.

Try it and share your results with me!"""

def save_script(script: dict, filename: str):
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save JSON
    script_path = SCRIPTS_DIR / filename
    with open(script_path, "w") as f:
        json.dump(script, f, indent=2)

    # Save readable version
    readme_path = SCRIPTS_DIR / filename.replace(".json", "-readme.txt")
    with open(readme_path, "w") as f:
        f.write(f"YOUTUBE SCRIPT: {script['metadata']['topic']}\n")
        f.write(f"Style: {script['metadata']['style']}\n")
        f.write(f"Duration: {script['metadata']['duration']}\n")
        f.write("=" * 40 + "\n\n")
        for section in script["sections"]:
            f.write(f"[{section['time']}] {section['type']}\n")
            f.write(f"TEXT: {section['text']}\n")
            f.write(f"VISUAL: {section['visual']}\n\n")

    print(f"\n✅ Script saved: {script_path}")
    print(f"   Readable: {readme_path}")
    return script_path

def show_help():
    print("\n🎬 YouTube Script Generator")
    print("=" * 35)
    print("\nUsage: python youtube_script.py [topic] [style]")
    print("\nStyles:")
    for key, info in STYLES.items():
        print(f"  {key}: {info['name']} ({info['duration']})")

    print("\n📋 Kerala topics:")
    for t in KERALA_TOPICS:
        print(f"  - {t}")

    print("\n📋 Viral topics:")
    for t in VIRAL_TOPICS:
        print(f"  - {t}")

    print("\nExamples:")
    print('  python youtube_script.py "Kerala backwaters" kerala')
    print('  python youtube_script.py "motivational quotes" quotes')
    print('  python youtube_script.py "mysterious places" facts')

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if not args:
        show_help()
    else:
        topic = args[0]
        style = args[1] if len(args) > 1 else "facts"

        print(f"\nGenerating script for: '{topic}' ({style} style)\n")
        script = generate_script(topic, style)
        filename = f"script-{int(datetime.now().timestamp())}.json"
        save_script(script, filename)

        print("\n📋 Next steps:")
        print("1. Get clips from pexels.com or pixabay.com")
        print("2. Add voiceover (Google TTS or manual)")
        print("3. Assemble video")
        print("4. Upload to YouTube!")