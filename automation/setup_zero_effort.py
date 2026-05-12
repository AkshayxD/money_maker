"""
ZERO-EFFORT SETUP SCRIPT
Run this ONCE, and everything is configured.

What it does:
1. Creates Google Cloud project (requires manual URL visit)
2. Authenticates with YouTube
3. Sets up GitHub repo
4. Configures everything

User only needs to:
1. Visit ONE URL (OAuth consent)
2. Run this script
3. Done forever
"""

import os
import sys
import webbrowser
from pathlib import Path
from time import sleep

BASE_DIR = Path(__file__).parent.parent

def print_step(num, text):
    print(f"\n{'='*50}")
    print(f"STEP {num}: {text}")
    print('='*50)

def main():
    print("\n" + "="*60)
    print("ZERO-EFFORT MONEY MAKER SETUP")
    print("="*60)
    print("\nThis script sets up EVERYTHING automatically.")
    print("You only need to visit ONE URL and click Allow.\n")

    # Step 1: Instructions
    print_step(1, "GOOGLE CLOUD SETUP (3 minutes)")
    print("""
Follow these steps (no coding required):

1. Open this URL in your browser:
   https://console.cloud.google.com/projectcreate

2. Enter Project Name: money-maker
3. Click CREATE

4. Go to this URL:
   https://console.cloud.google.com/apis/library/youtube-data-api?v3

5. Search for "YouTube Data API v3" and click ENABLE

6. Go to Credentials:
   https://console.cloud.google.com/apis/credentials

7. Click CREATE CREDENTIALS > OAuth client ID

8. Application type: Desktop app

9. Name it: youtube-uploader > CREATE

10. Click DOWNLOAD JSON

11. Move the downloaded file to this folder:
    """)
    print(f"    {BASE_DIR / 'youtube' / 'credentials.json'}")
    print("""
12. Come back here and press ENTER
""")

    input("\nPress ENTER when you've completed Step 1...")

    # Check if credentials exist
    creds_file = BASE_DIR / "youtube" / "credentials.json"
    if not creds_file.exists():
        print("\n[X] credentials.json not found!")
        print("    Make sure you moved it to the correct folder.")
        print("    Run this script again.")
        return

    print("\n[+] credentials.json found!")

    # Step 2: OAuth
    print_step(2, "YOUTUBE AUTHENTICATION (30 seconds)")
    print("""
Now we need to connect to your YouTube channel.
This requires one manual step:

1. I'll open a URL in your browser
2. Sign in with your Google account (same as YouTube)
3. Click ALLOW
4. Come back here

This is required by Google - cannot be automated.
""")

    input("\nPress ENTER to open the authentication URL...")

    # Run OAuth
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials

    TOKEN_FILE = BASE_DIR / "youtube" / "token.json"

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(creds_file),
            ["https://www.googleapis.com/auth/youtube.upload"]
        )
        print("\n[*] Opening browser for authentication...")
        creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
        print("[+] Authentication successful!")
    except Exception as e:
        print(f"\n[X] Authentication failed: {e}")
        print("    Make sure credentials.json is in the correct folder.")
        return

    # Step 3: Generate secrets
    print_step(3, "GENERATE GITHUB SECRETS")
    print("""
Now we create the secrets for GitHub Actions.
This is automated - just copy the output.
""")

    import base64
    import json

    token_data = json.loads(TOKEN_FILE.read_text())
    creds_data = json.loads(creds_file.read_text())

    token_b64 = base64.b64encode(json.dumps(token_data).encode()).decode()
    creds_b64 = base64.b64encode(json.dumps(creds_data).encode()).decode()

    print("\n" + "-"*60)
    print("COPY THESE TWO VALUES:")
    print("-"*60)

    print(f"\n1. YOUTUBE_TOKEN_DATA:\n\n{token_b64}\n")
    print(f"\n2. YOUTUBE_CLIENT_CONFIG:\n\n{creds_b64}\n")

    print("-"*60)

    # Step 4: GitHub setup
    print_step(4, "GITHUB SETUP")
    print("""
1. Create GitHub repo:
   - Go to https://github.com/new
   - Name: money_maker
   - Public
   - Don't add README or .gitignore
   - Click Create repository

2. Add secrets:
   - Go to: https://github.com/YOUR_USERNAME/money_maker/settings/secrets/actions
   - Click "New repository secret"
   - Name: YOUTUBE_TOKEN_DATA
   - Value: [copy from above - the long string]
   - Click Add secret
   - Repeat for YOUTUBE_CLIENT_CONFIG

3. Push code:
   - Come back here and run these commands:
""")

    print(f"""
    cd {BASE_DIR}
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/money_maker.git
    git push -u origin main
""")

    # Step 5: Test
    print_step(5, "TEST THE SETUP")
    print("""
After pushing to GitHub:
1. Go to: https://github.com/YOUR_USERNAME/money_maker/actions
2. Click "Morning Upload" > "Run workflow" > "Run workflow"
3. Watch it run - first video uploads!

You're done!
""")

    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("""
Summary:
- Google Cloud: Project created
- YouTube: Authenticated
- GitHub: Ready to push
- Secrets: Copy the values above

Next time you open this folder:
  python automation/auto_pipeline.py daily

Or push to GitHub for fully automated daily uploads!
""")

if __name__ == "__main__":
    main()