"""
Book Generator - Create e-books for Amazon KDP
Usage: python book_generator.py
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DRAFTS_DIR = BASE_DIR / "books" / "drafts"
COVERS_DIR = BASE_DIR / "books" / "covers"

BOOK_TYPES = {
    "short_story": {"name": "Short Story Collection", "words": 8000, "chapters": 5},
    "guide": {"name": "How-To Guide", "words": 12000, "chapters": 8},
    "puzzles": {"name": "Activity Book", "words": 5000, "chapters": 10},
    "children": {"name": "Children's Story", "words": 3000, "chapters": 1},
    "devotional": {"name": "Motivational Journal", "words": 10000, "chapters": 30}
}

KERALA_IDEAS = [
    "Traditional Kerala Recipes",
    "Munnar Tea Plantation Guide",
    "Backwater Houseboat Experience",
    "Kathakali Dance Explained",
    "Ayurveda Home Remedies",
    "Kids Stories from Kerala",
    "30 Days of Malayalam Phrases",
    "Onam Celebration Guide"
]

GENERIC_IDEAS = [
    "Daily Gratitude Journal",
    "Word Search Challenge",
    "Short Stories Volume 1",
    "Morning Motivation 30 Days",
    "Lazy Person's Productivity Guide",
    "Budget Travel India",
    "Sleep Better Tonight",
    "Small Space Gardening"
]

def create_word_search_html(title: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ text-align: center; }}
        pre {{ font-family: monospace; font-size: 14px; line-height: 1.4; }}
        .puzzle {{ background: #f5f5f5; padding: 20px; margin: 20px 0; }}
    </style>
</head>
<body>
<h1>{title}</h1>
<p style="text-align:center;">Fun puzzles for all ages</p>
<hr/>
"""

def create_guide_html(title: str, niche: str) -> str:
    chapters_html = ""
    chapter_titles = [
        "Getting Started",
        "Understanding the Basics",
        "Building Your Foundation",
        "Common Mistakes to Avoid",
        "Advanced Techniques",
        "Troubleshooting Tips",
        "Maintaining Progress",
        "Growing Your Skills"
    ]

    for i, ct in enumerate(chapter_titles[:8], 1):
        chapters_html += f"""
<h2>Chapter {i}: {ct}</h2>
<p>This chapter covers important aspects of {niche.lower()}. Focus on understanding before moving forward.</p>
<ul>
<li>Start with small, achievable goals</li>
<li>Build consistency over perfection</li>
<li>Celebrate small wins</li>
</ul>
"""

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Georgia, serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ text-align: center; color: #333; }}
        h2 {{ color: #555; margin-top: 30px; }}
    </style>
</head>
<body>
<h1>{title}</h1>
<p style="text-align:center;">Your Complete Guide to {niche}</p>
<hr/>

<h2>Introduction</h2>
<p>Welcome! This book helps you understand and master {niche}. Whether starting out or looking to improve, this guide provides practical insights.</p>

{chapters_html}

<h2>Conclusion</h2>
<p>You've completed this guide! Remember: consistency and patience are key to success. Keep practicing, stay motivated, and don't be afraid to start again if needed.</p>
<p style="text-align:center;">Good luck on your journey!</p>
</body>
</html>"""

def create_children_story(title: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; font-size: 18px; }}
        h1 {{ text-align: center; color: #2c5f2d; }}
        p {{ text-indent: 2em; margin: 1em 0; }}
    </style>
</head>
<body>
<h1>{title}</h1>
<hr/>

<h2>The Adventure Begins</h2>

<p>Once upon a time, in a small village surrounded by green hills and flowing rivers, there lived a curious young one named Kai.</p>

<p>Every morning, Kai would wake up with the sun and wonder what new adventure the day would bring.</p>

<p>One day, while exploring near an old tree, Kai discovered something unusual - a tiny glowing stone!</p>

<p>"What could this be?" Kai whispered, picking it up carefully.</p>

<p>As soon as Kai touched it, the stone began to shine and a friendly voice spoke!</p>

<p>"Hello, young explorer! I've been waiting for someone brave."</p>

<p>Kai's eyes widened. "A talking stone? This is the beginning of an adventure!"</p>

<p>And so began a wonderful journey that taught Kai about friendship, courage, and magic.</p>

<p><em>The End</em></p>
<p style="text-align:center;">⭐</p>
</body>
</html>"""

def generate_book(book_type: str, title: str, niche: str = ""):
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c for c in title if c.isalnum() or c in " -").strip()
    filename = safe_title.lower().replace(" ", "-") + ".html"
    filepath = DRAFTS_DIR / filename

    if book_type == "children":
        content = create_children_story(title)
    else:
        content = create_guide_html(title, niche or "interesting topics")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Save cover prompt
    cover_prompt = f"Create a book cover for '{title}'. Style: {'playful for children' if book_type == 'children' else 'professional non-fiction'}. Colors: {'bright cheerful' if book_type == 'children' else 'clean modern'}."
    prompt_file = COVERS_DIR / f"{safe_title.lower().replace(' ', '-')}-cover-prompt.txt"
    with open(prompt_file, "w") as f:
        f.write(cover_prompt)

    print(f"\n✅ Book created: {filepath}")
    print(f"   Cover prompt: {prompt_file}")
    return filepath

def show_menu():
    print("\n📚 Amazon KDP Book Generator")
    print("=" * 35)
    print("\nBook types:")
    for key, info in BOOK_TYPES.items():
        print(f"  {key}: {info['name']} ({info['words']//1000}k words)")

    print("\n📋 Kerala Ideas:")
    for i, idea in enumerate(KERALA_IDEAS, 1):
        print(f"  {i}. {idea}")

    print("\n📋 General Ideas:")
    for i, idea in enumerate(GENERIC_IDEAS, 1):
        print(f"  {i}. {idea}")

    print("\n💡 Just tell me what book to create!")
    print("   Examples: 'Write a children's story about...',")
    print("             'Create a puzzle book', 'Write a guide about...'")

if __name__ == "__main__":
    show_menu()