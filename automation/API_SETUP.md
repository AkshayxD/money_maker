# YouTube Shorts Generator - API Key Setup

This document explains how to set up optional API keys for enhanced AI features.

## Free Tier API Keys

### 1. OpenAI API Key (Optional)
For AI-generated scripts instead of pre-written ones.

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to GitHub Secrets as `OPENAI_API_KEY`

**Free credits**: New accounts get $5 free credits.

### 2. Replicate API Key (Optional)
For AI image generation with Stable Diffusion.

1. Go to https://replicate.com/account/api-tokens
2. Create an API token
3. Add to GitHub Secrets as `REPLICATE_API_TOKEN`

**Free tier**: Includes free compute for Stable Diffusion.

### 3. Segmind API Key (Optional)
Alternative for AI image generation.

1. Go to https://segmind.com
2. Sign up for free account
3. Copy API key
4. Add to GitHub Secrets as `SEGMIND_API_KEY`

**Free tier**: 100 credits for image generation.

## Without API Keys

The pipeline works without any API keys using:
- **Scripts**: Pre-written curated scripts (v10 includes 15+ topics)
- **Images**: Free images from Unsplash/Picsum
- **Audio**: Microsoft Edge neural voices (free)
- **Video**: FFmpeg with Ken Burns effect

## Recommended Setup Order

1. **Start without keys** - Test the basic pipeline works
2. **Add OpenAI key** - For fresh, unique scripts every time
3. **Add Replicate/Segmind key** - For AI-generated images matching your content exactly

## Adding Keys to GitHub

1. Go to your repo: https://github.com/AkshayxD/money_maker
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each key:
   - Name: `OPENAI_API_KEY`
   - Value: your-api-key

The pipeline automatically detects available keys and uses them.