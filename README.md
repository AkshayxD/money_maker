# MindFlip YouTube Automation

Fully automated YouTube Shorts generator that creates and uploads 2 videos daily.

## Setup (Run Once)

```bash
python automation/setup_zero_effort.py
```

Follow the instructions. That's it.

## What It Does

1. **AI Script Generation** - Uses OpenCode API to generate engaging scripts
2. **Natural Voice** - Gemini TTS (Kore voice) for human-like narration
3. **Context Images** - Downloads relevant images for each sentence
4. **Ken Burns Effect** - Professional zoom/pan on each image
5. **Auto Upload** - Uploads to YouTube as Short automatically

## API Keys (Optional)

Without any keys, the pipeline uses curated scripts. Add keys for AI-generated content:

### OpenCode API (Script Generation)
- Get from your OpenCode provider
- Add to GitHub Secrets as `OPENCODE_API_KEY`

### Gemini API (Voice Generation)
- Free tier at https://aistudio.google.com
- Add to GitHub Secrets as `GEMINI_API_KEY`

### NewsAPI (Trending Topics)
- Free tier at https://newsapi.org
- Add to GitHub Secrets as `NEWS_API_KEY`

## Schedule

- **Morning**: 10:00 AM UTC (3:30 PM IST)
- **Evening**: 6:00 PM UTC (11:30 PM IST)

## For Maximum Views

1. **Trending topics** - NewsAPI key enables trending content
2. **Viral hooks** - AI generates curiosity-gap hooks
3. **Consistent posting** - 2 videos daily builds algorithm favor
4. **Engaging descriptions** - Auto-generated with hashtags

## Requirements

- Google account (YouTube)
- GitHub account (free)
- Python 3.11+