"""
Photo Tagger - Generate SEO titles and tags for stock photos
Usage: python photo_tagger.py
"""

import os
import json
from pathlib import Path

PHOTOS_DIR = Path(__file__).parent.parent / "photos"
OUTPUT_FILE = Path(__file__).parent / "photo_results.json"

KEYWORDS = {
    "nature": ["landscape", "scenic", "outdoor", "beautiful", "serene", "peaceful", "tranquil", "calm", "wilderness", "countryside", "field", "meadow", "forest", "tree", "sunrise", "sunset"],
    "water": ["water", "lake", "river", "ocean", "sea", "beach", "coastal", "wave", "shore", "tropical", "marina", "harbor", "boat"],
    "kerala": ["kerala", "backwaters", "houseboat", "coconut", "paddy", "spice", "ayurveda", "kathakali", "monsoon", "munnar", "alleppey", "kochi", "beach", "fishing", "coastal"],
    "culture": ["traditional", "cultural", "heritage", "festival", "ceremony", "spiritual", "religious", "temple", "architecture", "historical"],
    "food": ["food", "cuisine", "dish", "meal", "cooking", "spice", "fresh", "delicious"],
    "travel": ["travel", "tourism", "destination", "vacation", "adventure", "explore", "journey", "wanderlust", "backpacking"]
}

def generate_title(description: str) -> str:
    templates = [
        f"Beautiful {description.split()[0] if description else 'landscape'} - scenic India",
        f"Serene {description} in Kerala, India",
        f"Stunning view of {description}",
        f"Peaceful {description} photography",
        f"{description.title()} - Kerala scenic"
    ]
    import random
    return random.choice(templates)

def generate_tags(description: str) -> list:
    tags = set()
    desc_lower = description.lower()

    for category, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                tags.add(kw)

    tags.update(["photography", "stock photo", "travel", "nature", "beautiful", "high quality", "india"])
    return list(tags)[:15]

def process_photos():
    if not PHOTOS_DIR.exists():
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\n📁 Created photos directory: {PHOTOS_DIR}")
        print("\n📸 Drop your photos here and run this script again.")
        return []

    files = [f for f in os.listdir(PHOTOS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

    if not files:
        print("\n📭 No photos found.")
        print(f"\nAdd photos to: {PHOTOS_DIR}")
        return []

    print(f"\n📸 Found {len(files)} photos\n")

    results = []
    for i, file in enumerate(files, 1):
        filename = os.path.splitext(file)[0]
        description = filename.replace("-", " ").replace("_", " ").strip() or "scenic landscape"

        title = generate_title(description)
        tags = generate_tags(description)

        result = {"filename": file, "title": title, "tags": tags}
        results.append(result)

        print(f"[{i}/{len(files)}] {file}")
        print(f"  Title: {title}")
        print(f"  Tags: {', '.join(tags[:5])}...\n")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Results saved to: {OUTPUT_FILE}")
    print("\n📋 Next: Upload to Shutterstock, Adobe Stock, or Pond5")

if __name__ == "__main__":
    print("\n🎯 Stock Photo Tagger")
    print("=" * 30)
    process_photos()