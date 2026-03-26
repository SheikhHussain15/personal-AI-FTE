# 🐦 Twitter (X) Integration Skill

**Type**: Watcher + Action  
**Purpose**: Monitor and post to Twitter/X  
**Status**: 🚧 Development  

---

## Overview

This skill provides integration with Twitter API v2 for:
- **Twitter Watcher**: Monitor mentions, DMs, and keyword mentions
- **Twitter Poster**: Publish tweets and threads
- **Engagement Tracking**: Track likes, retweets, replies

---

## Architecture

```
┌─────────────────┐      Twitter API     ┌─────────────────┐
│   Qwen Code     │ ◄──────────────────► │   Twitter       │
│   (Reasoning)   │    HTTP/REST         │   Servers       │
└─────────────────┘                      └─────────────────┘
         │                                      │
         │                                      ├── Tweets
         │                                      ├── Mentions
         │                                      └── DMs
         ▼
┌─────────────────┐
│  Vault Folders  │
│  - Needs_Action │
│  - Approved     │
│  - Done         │
└─────────────────┘
```

---

## Prerequisites

### 1. Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for a developer account
3. Create a new project and app

### 2. Get API Credentials

From your app dashboard, get:
- API Key
- API Secret
- Access Token
- Access Token Secret
- Bearer Token

### 3. Required Permissions

| Permission | Purpose |
|------------|---------|
| `tweet.read` | Read tweets |
| `tweet.write` | Create tweets |
| `users.read` | Read user info |
| `follows.read` | Read followers |
| `like.read` | Read likes |
| `like.write` | Create likes |
| `dm.read` | Read DMs |
| `dm.write` | Send DMs |

---

## Installation

```bash
# Install dependencies
pip install tweepy python-dotenv

# Configure credentials
python scripts/twitter_config.py \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET \
  --access-token YOUR_TOKEN \
  --access-secret YOUR_TOKEN_SECRET
```

---

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `twitter_post` | Post a tweet | text, media_url, reply_to |
| `twitter_thread` | Post a tweet thread | tweets[], media_urls[] |
| `twitter_get_mentions` | Get recent mentions | limit, since_id |
| `twitter_get_dms` | Get direct messages | limit |
| `twitter_search` | Search tweets | query, limit |
| `twitter_get_metrics` | Get tweet metrics | tweet_id |

---

## Configuration

```json
{
  "api_key": "your_api_key",
  "api_secret": "your_api_secret",
  "access_token": "your_access_token",
  "access_token_secret": "your_token_secret",
  "bearer_token": "your_bearer_token",
  "check_interval": 30,
  "keywords": ["your brand", "your products"]
}
```

---

## Usage Examples

### Post a Tweet

```bash
python scripts/twitter_poster.py \
  --vault ../AI_Employee_Vault \
  --text "Exciting business update! #startup"
```

### Post a Thread

```bash
python scripts/twitter_poster.py \
  --vault ../AI_Employee_Vault \
  --thread "First tweet..." "Second tweet..." "Third tweet..."
```

### Monitor Mentions

```bash
python scripts/twitter_watcher.py \
  --vault ../AI_Employee_Vault \
  --interval 30
```

---

## File Structure

```
twitter-integration/
├── SKILL.md
├── scripts/
│   ├── twitter_config.py      # Configuration setup
│   ├── twitter_client.py      # Twitter API client
│   ├── twitter_watcher.py     # Monitor mentions/DMs
│   └── twitter_poster.py      # Post tweets
└── references/
    └── twitter-api-docs.md    # API reference
```

---

## Error Handling

| Error | Code | Recovery |
|-------|------|----------|
| Rate limited | TW_001 | Wait 15 minutes, retry |
| Authentication failed | TW_002 | Refresh tokens |
| Duplicate tweet | TW_003 | Modify content |
| Tweet too long | TW_004 | Split into thread |
| Media upload failed | TW_005 | Check format/size |

---

## Rate Limits (API v2)

| Endpoint | Limit |
|----------|-------|
| POST /tweets | 200 per 15 min |
| GET /mentions | 300 per 15 min |
| GET /search | 300 per 15 min |
| POST /dm | 1000 per day |

---

## Security

- Never commit API credentials
- Use environment variables
- Rotate tokens regularly
- Enable 2FA on developer account
- Monitor app usage

---

## References

- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)

---

*Twitter (X) Integration v0.1 | AI Employee Hackathon 2026*
