"""
Claude Integration - Connect Python with Claude Code AI
Usage:
  python claude_integration.py write "Write a short story"
  python claude_integration.py youtube "Generate a script about [topic]"
  python claude_integration.py photos "Tag these photos: [descriptions]"
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
CWD = Path(__file__).parent.parent
BOOKS_DIR = CWD / "books" / "drafts"
SCRIPTS_DIR = CWD / "youtube" / "scripts"

# Claude project name (creates .claude folder for context)
PROJECT_NAME = "money-maker"

def run_claude(prompt: str, output_file: str = None) -> str:
    """
    Run Claude Code with a prompt and return the response.
    Uses --print flag for non-interactive mode.
    """
    # Create a prompt file to avoid shell escaping issues
    prompt_file = CWD / ".claude" / f"prompt-{int(datetime.now().timestamp())}.txt"
    prompt_file.parent.mkdir(exist_ok=True)
    prompt_file.write_text(prompt)

    try:
        # Run Claude with the prompt file
        result = subprocess.run(
            ["claude", "--print", f"< {prompt_file}"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(CWD)
        )

        # Cleanup prompt file
        if prompt_file.exists():
            prompt_file.unlink()

        if result.returncode == 0:
            response = result.stdout
            if output_file:
                Path(output_file).write_text(response)
                print(f"Saved to: {output_file}")
            return response
        else:
            print(f"Claude error: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("Claude took too long - try a shorter prompt")
        return None
    except FileNotFoundError:
        print("Claude CLI not found. Make sure Claude Code is installed and in PATH")
        return None

def write_book(topic: str):
    """Use Claude to write a book"""
    prompt = f"""Write a complete book for Amazon KDP in HTML format.

Topic: {topic}

Requirements:
- 5000-10000 words
- Proper HTML structure with title, chapters, formatting
- Engaging content suitable for self-publishing
- Save to: {BOOKS_DIR}/book-{int(datetime.now().timestamp())}.html

Format the output as complete, publication-ready HTML.
Make it substantial - real content, not placeholder text."""

    output = BOOKS_DIR / f"book-{int(datetime.now().timestamp())}.html"
    result = run_claude(prompt, str(output))

    if result:
        print(f"\n[+] Book created: {output}")
    else:
        print("\n[x] Failed to create book")

def write_youtube_script(topic: str, style: str = "facts"):
    """Use Claude to generate a YouTube script"""
    prompt = f"""Create a complete YouTube video script for the topic: {topic}

Style: {style}

Output as JSON with this structure:
{{
  "metadata": {{"topic": "...", "style": "...", "duration": "..."}},
  "sections": [
    {{"time": "0:00", "type": "HOOK", "text": "...", "visual": "...", "audio": "..."}},
    {{"time": "0:03", "type": "INTRO", "text": "...", "visual": "...", "audio": "..."}},
    {{"time": "0:10", "type": "MAIN", "text": "...", "visual": "...", "audio": "..."}},
    {{"time": "0:45", "type": "OUTRO", "text": "...", "visual": "...", "audio": "..."}}
  ]
}}

Make it engaging, viral-worthy content. Include actual narration text.
Save to: {SCRIPTS_DIR}/script-{int(datetime.now().timestamp())}.json"""

    output = SCRIPTS_DIR / f"script-{int(datetime.now().timestamp())}.json"
    result = run_claude(prompt, str(output))

    if result:
        print(f"\n[+] YouTube script created: {output}")
    else:
        print("\n[x] Failed to create script")

def tag_photos(descriptions: str):
    """Use Claude to generate SEO tags for photos"""
    prompt = f"""Generate SEO-friendly titles, descriptions, and tags for these stock photos.

Photos: {descriptions}

Output as JSON array:
[
  {{"filename": "photo1.jpg", "title": "...", "description": "...", "tags": ["tag1", "tag2", ...]}},
  ...
]

Make titles catchy, descriptions compelling, and tags optimized for stock photo sites.
Save to: {CWD}/photos/tags-{int(datetime.now().timestamp())}.json"""

    output = CWD / "photos" / f"tags-{int(datetime.now().timestamp())}.json"
    result = run_claude(prompt, str(output))

    if result:
        print(f"\n[+] Photo tags generated: {output}")
    else:
        print("\n[x] Failed to generate tags")

def generate_cover_prompt(book_title: str, book_type: str):
    """Use Claude to create an image prompt for a book cover"""
    prompt = f"""Create a detailed image generation prompt for a book cover.

Book Title: {book_title}
Book Type: {book_type}

Generate a DALL-E/Midjourney compatible prompt that would create an eye-catching
book cover suitable for Amazon KDP self-publishing.

Output just the prompt, nothing else."""

    result = run_claude(prompt)

    if result:
        prompt_file = CWD / "books" / "covers" / f"{book_title[:20].replace(' ', '-')}-cover-prompt.txt"
        prompt_file.parent.mkdir(exist_ok=True)
        prompt_file.write_text(result.strip())
        print(f"\n[+] Cover prompt saved: {prompt_file}")
    else:
        print("\n[x] Failed to create cover prompt")

def batch_generate(num_books: int = 5):
    """Generate multiple books automatically"""
    topics = [
        "30-Day Morning Routine for Success",
        "Simple Indian Recipes for Beginners",
        "Word Search Puzzles for Kids",
        "Sleep Better: Natural Remedies",
        "Travel Guide: Kerala on a Budget"
    ]

    print(f"\n[*] Generating {num_books} books...\n")

    for i, topic in enumerate(topics[:num_books], 1):
        print(f"[{i}/{num_books}] {topic}")
        write_book(topic)
        print()

def show_help():
    print("""
Claude Integration - AI-Powered Content Generation
==================================================

Commands:
  book [topic]         - Write a book (e.g., python claude_integration.py book "Morning Motivation")
  youtube [topic] [style] - Generate YouTube script (styles: facts, quotes, travel, kerala)
  photos [descriptions] - Generate SEO tags for photos
  cover [title] [type]  - Generate book cover prompt
  batch [num]           - Generate multiple books at once
  help                  - Show this help

Examples:
  python claude_integration.py book "Short stories about Indian villages"
  python claude_integration.py youtube "Kerala backwaters" kerala
  python claude_integration.py photos "sunset, beach, coconut trees, houseboat"
  python claude_integration.py batch 5

Note: Requires Claude Code CLI installed and in PATH.
""")

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "help":
        show_help()
        sys.exit()

    cmd = args[0]

    if cmd == "book":
        topic = " ".join(args[1:]) or "A guide to productivity"
        write_book(topic)

    elif cmd == "youtube":
        topic = args[1] if len(args) > 1 else "Interesting facts"
        style = args[2] if len(args) > 2 else "facts"
        write_youtube_script(topic, style)

    elif cmd == "photos":
        desc = " ".join(args[1:]) or "landscape, nature, scenic"
        tag_photos(desc)

    elif cmd == "cover":
        title = " ".join(args[1:-1]) if len(args) > 2 else "My Book"
        btype = args[-1] if len(args) > 2 else "guide"
        generate_cover_prompt(title, btype)

    elif cmd == "batch":
        num = int(args[1]) if len(args) > 1 else 5
        batch_generate(num)

    else:
        print(f"Unknown command: {cmd}")
        show_help()