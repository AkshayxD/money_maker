"""
YouTube OAuth Setup Tool
Generates GitHub secrets from your local credentials

Usage:
  python setup_github_secrets.py

This will:
1. Read your existing youtube/credentials.json and youtube/token.json
2. Encode them for GitHub Secrets
3. Show you the exact commands to run
"""

import os
import json
import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TOKEN_FILE = BASE_DIR / "youtube" / "token.json"
CREDENTIALS_FILE = BASE_DIR / "youtube" / "credentials.json"

def encode_json_for_github(data):
    """Encode JSON to base64 for GitHub secrets"""
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()

def generate_github_commands():
    print("\n" + "=" * 60)
    print("GITHUB SECRETS SETUP")
    print("=" * 60)

    if not TOKEN_FILE.exists():
        print("\n[X] Error: youtube/token.json not found!")
        print("    Run: python youtube_uploader.py auth")
        print("    Then come back and run this script again.")
        return

    if not CREDENTIALS_FILE.exists():
        print("\n[X] Error: youtube/credentials.json not found!")
        print("    Run: python youtube_uploader.py setup")
        print("    Then come back and run this script again.")
        return

    # Read credentials
    with open(TOKEN_FILE, 'r') as f:
        token_data = json.load(f)

    with open(CREDENTIALS_FILE, 'r') as f:
        credentials_data = json.load(f)

    # Encode them
    token_b64 = encode_json_for_github(token_data)
    credentials_b64 = encode_json_for_github(credentials_data)

    print("\n[+] Credentials found!")
    print("\n" + "-" * 60)
    print("STEPS TO ADD SECRETS TO GITHUB:")
    print("-" * 60)
    print("""
1. Go to your GitHub repository: https://github.com/YOUR_USERNAME/money_maker

2. Click Settings > Secrets and Variables > Actions

3. Add these 2 secrets (click "New repository secret" for each):

SECRET 1:
  Name: YOUTUBE_TOKEN_DATA
  Value (copy this one line):""")

    print(f"\n{token_b64}")

    print("""
\nSECRET 2:
  Name: YOUTUBE_CLIENT_CONFIG
  Value (copy this one line):""")

    print(f"\n{credentials_b64}")

    print("""
    """ + "-" * 60)

    # Also show gh CLI commands
    print("\n[+] OR use GitHub CLI (faster):")
    print(f'   gh secret set YOUTUBE_TOKEN_DATA --body "{token_b64}"')
    print(f'   gh secret set YOUTUBE_CLIENT_CONFIG --body "{credentials_b64}"')

    print("\n" + "=" * 60)
    print("AFTER ADDING SECRETS:")
    print("  1. Push your code to GitHub")
    print("  2. Go to Actions tab")
    print("  3. Click Morning Upload workflow")
    print("  4. Click Run workflow to test")
    print("=" * 60)

def create_secrets_file():
    """Create a helper script that generates the secrets locally"""
    script_content = '''#!/bin/bash
# GitHub Secrets Setup Helper
# Run this locally to generate secrets for GitHub

# Get token data
TOKEN=$(cat youtube/token.json | base64)
echo "YOUTUBE_TOKEN_DATA=$TOKEN"

echo ""

# Get credentials
CREDS=$(cat youtube/credentials.json | base64)
echo "YOUTUBE_CLIENT_CONFIG=$CREDS"
'''
    output = BASE_DIR / "automation" / "generate-secrets.sh"
    output.write_text(script_content)
    print(f"\n[+] Created: {output}")
    print("    Run: bash automation/generate-secrets.sh")
    print("    Copy the output into GitHub Secrets")

if __name__ == "__main__":
    print("\n[*] GitHub Secrets Generator")
    print("=" * 40)
    generate_github_commands()
    create_secrets_file()