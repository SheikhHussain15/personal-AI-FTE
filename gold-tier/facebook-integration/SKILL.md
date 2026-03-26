# 📘 Facebook/Instagram Integration Skill

**Type**: Watcher + Action  
**Purpose**: Monitor and post to Facebook Pages and Instagram Business accounts  
**Status**: 🚧 Development  

---

## Overview

This skill provides integration with Meta's Graph API for:
- **Facebook Watcher**: Monitor page messages, comments, and mentions
- **Facebook Poster**: Publish posts to Facebook Pages
- **Instagram Poster**: Publish posts to Instagram Business accounts
- **Engagement Tracking**: Track likes, comments, shares

---

## Architecture

```
┌─────────────────┐      Graph API       ┌─────────────────┐
│   Qwen Code     │ ◄──────────────────► │   Meta Servers  │
│   (Reasoning)   │    HTTP/REST         │   (FB/IG)       │
└─────────────────┘                      └─────────────────┘
         │                                      │
         │                                      ├── Facebook Page
         │                                      ├── Instagram Business
         │                                      └── Messenger
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

### 1. Meta Developer App

1. Go to [Meta Developers](https://developers.facebook.com/)
2. Create new app → Business type
3. Add products:
   - Facebook Login
   - Instagram Graph API
   - Pages API

### 2. Get Access Tokens

```bash
# Run authentication script
python scripts/facebook_auth.py \
  --app-id YOUR_APP_ID \
  --app-secret YOUR_APP_SECRET
```

### 3. Required Permissions

| Permission | Purpose |
|------------|---------|
| `pages_read_engagement` | Read page posts, comments |
| `pages_manage_posts` | Create page posts |
| `pages_messaging` | Read/send messages |
| `instagram_basic` | Basic Instagram access |
| `instagram_content_publish` | Publish Instagram posts |
| `instagram_manage_messages` | Read/send Instagram DMs |

---

## Installation

```bash
# Install dependencies
pip install facebook-business requests python-dotenv

# For browser automation (fallback)
pip install playwright
playwright install chromium
```

---

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `facebook_post` | Post to Facebook Page | page_id, message, link, image_url |
| `instagram_post` | Post to Instagram | ig_user_id, caption, image_url |
| `facebook_get_messages` | Get page messages | page_id, limit |
| `facebook_get_comments` | Get post comments | post_id, limit |
| `facebook_get_insights` | Get page analytics | page_id, metric, period |
| `instagram_get_comments` | Get media comments | media_id, limit |

---

## Configuration

```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "access_token": "your_long_lived_token",
  "page_id": "your_page_id",
  "instagram_business_account_id": "your_ig_account_id",
  "check_interval": 60
}
```

---

## Usage Examples

### Post to Facebook

```bash
python scripts/facebook_poster.py \
  --vault ../AI_Employee_Vault \
  --page-id 123456789 \
  --message "Exciting business update!" \
  --image-url "https://example.com/image.jpg"
```

### Post to Instagram

```bash
python scripts/instagram_poster.py \
  --vault ../AI_Employee_Vault \
  --caption "New product launch! #business" \
  --image-url "https://example.com/product.jpg"
```

### Monitor Messages

```bash
python scripts/facebook_watcher.py \
  --vault ../AI_Employee_Vault \
  --page-id 123456789 \
  --interval 60
```

---

## File Structure

```
facebook-integration/
├── SKILL.md
├── scripts/
│   ├── facebook_auth.py       # OAuth authentication
│   ├── facebook_watcher.py    # Monitor messages/comments
│   ├── facebook_poster.py     # Post to Facebook
│   ├── instagram_poster.py    # Post to Instagram
│   └── facebook_client.py     # Graph API client
└── references/
    └── graph-api-docs.md      # API reference
```

---

## Error Handling

| Error | Code | Recovery |
|-------|------|----------|
| Token expired | FB_001 | Refresh long-lived token |
| Permission denied | FB_002 | Request additional permissions |
| Rate limited | FB_003 | Wait and retry (exponential backoff) |
| Invalid page | FB_004 | Verify page ID |
| Image upload failed | FB_005 | Check image URL/format |

---

## Security

- Never commit access tokens
- Use environment variables
- Rotate tokens every 60 days
- Limit app permissions
- Enable app review for production

---

## References

- [Meta Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Facebook Login](https://developers.facebook.com/docs/facebook-login)

---

*Facebook/Instagram Integration v0.1 | AI Employee Hackathon 2026*
