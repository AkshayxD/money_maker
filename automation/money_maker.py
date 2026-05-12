"""
Money Maker - Main Automation Runner (Python)
Usage: python money_maker.py [command]

Commands:
  photos     - Process and tag photos
  book       - Generate book (specify type)
  youtube    - Generate YouTube script
  all        - Generate everything
  status     - Show current status
  help       - Show help
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent
PHOTOS_DIR = BASE_DIR / "photos"
DRAFTS_DIR = BASE_DIR / "books" / "drafts"
SCRIPTS_DIR = BASE_DIR / "youtube" / "scripts"

def show_menu():
    print("\n[$] MONEY MAKER - Passive Income Automation")
    print("=" * 45)
    print("\nThree ways to earn:\n")

    # Photos status
    try:
        photos = [f for f in os.listdir(PHOTOS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        photo_status = f"[{len(photos)}] photos ready" if photos else "[X] No photos"
    except:
        photo_status = "[X] Photos folder missing"
    print(f"1. Stock Photos - {photo_status}")

    # Books status
    try:
        books = list(DRAFTS_DIR.glob("*.html"))
        book_status = f"[{len(books)}] books drafted" if books else "[X] No books"
    except:
        book_status = "[X] Drafts folder missing"
    print(f"2. Amazon KDP Books - {book_status}")

    # YouTube status
    try:
        scripts = list(SCRIPTS_DIR.glob("*.json"))
        yt_status = f"[{len(scripts)}] scripts ready" if scripts else "[X] No scripts"
    except:
        yt_status = "[X] Scripts folder missing"
    print(f"3. YouTube Channel - {yt_status}")

    print("\n" + "=" * 45)
    print("\nCommands:")
    print("  photos          - Process photos for stock sites")
    print("  book [type]     - Generate book (short_story/guide/puzzles/children/devotional)")
    print("  youtube [topic] - Generate YouTube script")
    print("  claude [action] - Use AI to generate content (book/youtube/photos)")
    print("  upload [file]   - Upload video to YouTube")
    print("  auto            - Run fully automated daily pipeline (generate+upload)")
    print("  all             - Generate everything at once")
    print("  status          - Detailed status")
    print("  help            - Show this menu\n")

def show_status():
    print("\n[=] STATUS\n" + "=" * 40)

    # Photos
    print("\nPhotos:")
    try:
        photos = [f for f in os.listdir(PHOTOS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"   Total: {len(photos)} photos")
        print(f"   Path: {PHOTOS_DIR}")
    except Exception as e:
        print(f"   Error: {e}")

    # Books
    print("\nBooks:")
    try:
        books = list(DRAFTS_DIR.glob("*.html"))
        print(f"   Total: {len(books)} drafts")
        print(f"   Path: {DRAFTS_DIR}")
        if books:
            for b in books:
                print(f"   - {b.name}")
    except Exception as e:
        print(f"   Error: {e}")

    # YouTube
    print("\nYouTube:")
    try:
        scripts = list(SCRIPTS_DIR.glob("*.json"))
        print(f"   Total: {len(scripts)} scripts")
        print(f"   Path: {SCRIPTS_DIR}")
        if scripts:
            for s in scripts:
                print(f"   - {s.name}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\nPlatforms to sign up:")
    print("   [ ] Shutterstock contributor account")
    print("   [ ] Amazon KDP account")
    print("   [ ] YouTube channel")
    print("   [ ] Indian bank account for payments")

def run_photos():
    print("\n[*] Processing photos...\n")
    os.system(f'python "{Path(__file__).parent}/photo_tagger.py"')

def run_book(book_type=None):
    print("\n[*] Book Generator\n")
    print("Book types: short_story, guide, puzzles, children, devotional")
    print("\nJust tell me what book to write!")
    print("   Examples: 'Write a childrens story about...'")
    print("             'Create a puzzle book about...'\n")

def run_youtube(topic=None):
    if not topic:
        print("\n[*] YouTube Script Generator\n")
        print("Usage: python money_maker.py youtube [topic]")
        print("\nExamples:")
        print('  python money_maker.py youtube "Kerala backwaters"')
        print('  python money_maker.py youtube "motivational quotes"')
        print('  python money_maker.py youtube "mysterious places" kerala\n')
        return

    print(f"\n[*] Generating YouTube script: {topic}\n")
    os.system(f'python "{Path(__file__).parent}/youtube_script.py" "{topic}"')

def run_claude(action=None, args=None):
    """Run Claude Code for AI-powered content generation"""
    if not action:
        print("\n[*] Claude AI Integration\n")
        print("Usage: python money_maker.py claude [action] [args]")
        print("\nActions:")
        print("  book [topic]      - Write a book with AI")
        print("  youtube [topic]   - Generate YouTube script with AI")
        print("  photos [desc]    - Generate photo tags with AI")
        print("  cover [title] [type] - Generate cover prompt with AI")
        print("  batch [num]       - Generate multiple books")
        print("\nOr just tell me what to create - I can do it directly!\n")
        return

    os.system(f'python "{Path(__file__).parent}/claude_integration.py" {action} {" ".join(args) if args else ""}')

def show_help():
    print("\n[?] HELP - Quick Start")
    print("=" * 40)
    print("\n1. ADD PHOTOS: Drop them in photos/")
    print("2. RUN: python money_maker.py photos")
    print("3. UPLOAD: Go to shutterstock.com/contributor")
    print("\nTips:")
    print("- Best photos: landscapes, nature, Kerala scenery")
    print("- Book niches: puzzles, short stories, how-to guides")
    print("- YouTube: Shorts get faster traction")
    print("\nJust ask me to generate content directly!")
    show_menu()

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    cmd = args[0] if args else "menu"

    if cmd == "photos":
        run_photos()
    elif cmd == "book":
        run_book(args[1] if len(args) > 1 else None)
    elif cmd == "youtube":
        run_youtube(args[1] if len(args) > 1 else None)
    elif cmd == "claude":
        run_claude(args[1] if len(args) > 1 else None, args[2:] if len(args) > 2 else [])
    elif cmd == "upload":
        print("\n[*] YouTube Upload\n")
        os.system(f'python "{Path(__file__).parent}/youtube_uploader.py" upload {" ".join(args[1:])}')
    elif cmd == "auto":
        print("\n[*] Running fully automated pipeline...\n")
        os.system(f'python "{Path(__file__).parent}/auto_pipeline.py" daily')
    elif cmd == "all":
        print("\n[*] Generating all content...\n")
        run_photos()
        print("\n" + "=" * 40)
    elif cmd == "status":
        show_status()
    elif cmd == "help":
        show_help()
    else:
        show_menu()