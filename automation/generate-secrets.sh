#!/bin/bash
# GitHub Secrets Setup Helper
# Run this locally to generate secrets for GitHub

# Get token data
TOKEN=$(cat youtube/token.json | base64)
echo "YOUTUBE_TOKEN_DATA=$TOKEN"

echo ""

# Get credentials
CREDS=$(cat youtube/credentials.json | base64)
echo "YOUTUBE_CLIENT_CONFIG=$CREDS"
