---
name: gmail-watcher
description: |
  Monitor Gmail for new important emails and create action files in the vault.
  Uses Gmail API to fetch unread/important messages and converts them to
  markdown files for Qwen Code processing. Requires Gmail API credentials.
---

# Gmail Watcher Skill

Monitor Gmail inbox and create actionable items in your AI Employee vault.

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Authenticate First Time

```bash
python .qwen/skills/gmail-watcher/scripts/gmail_auth.py --vault ../AI_Employee_Vault
```

## Quick Start

```bash
# Start Gmail Watcher
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120
```

## Configuration

### Environment Variables

Create `.env` file in vault root:

```bash
# Gmail API Credentials
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.json

# Watcher Settings
GMAIL_CHECK_INTERVAL=120
GMAIL_LABELS=INBOX,IMPORTANT
```

### Watcher Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `--interval` | 120s | Time between checks |
| `--labels` | INBOX,IMPORTANT | Gmail labels to monitor |
| `--keywords` | urgent,asap,invoice | Keywords for priority |

## How It Works

```
1. Watcher polls Gmail API every 2 minutes
2. Fetches unread, important messages
3. Extracts: From, Subject, Date, Snippet
4. Creates .md file in Needs_Action/
5. Marks message as processed
6. Qwen Code processes the action file
```

## Action File Format

Each email creates a file like:

```markdown
---
type: email
from: client@example.com
subject: Urgent: Invoice Payment
received: 2026-02-26T10:30:00
priority: high
status: pending
message_id: 18e4f2a3b5c6d7e8
---

# Email: Urgent: Invoice Payment

**From:** client@example.com
**Received:** 2026-02-26 10:30
**Priority:** High

## Content

Thank you for your service. Please send the invoice for payment...

## Suggested Actions

- [ ] Reply to sender
- [ ] Create and send invoice
- [ ] Archive after processing
```

## Usage Examples

### Basic Usage

```bash
# Start with defaults
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ../AI_Employee_Vault
```

### Custom Interval

```bash
# Check every 5 minutes
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 300
```

### With Keywords

```bash
# Only flag emails with specific keywords
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ../AI_Employee_Vault \
  --keywords "invoice,payment,urgent,asap"
```

## Integration with Qwen Code

After watcher creates action files:

```bash
cd AI_Employee_Vault
qwen "Process new emails in Needs_Action folder. Reply to urgent ones and create invoices."
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run `gmail_auth.py` |
| No emails detected | Check Gmail labels/filters |
| API quota exceeded | Wait 24 hours or reduce frequency |
| Token expired | Delete `token.json` and re-authenticate |

## Security Notes

- Never commit `token.json` or `credentials.json` to git
- Store credentials in secure location
- Use app-specific passwords if 2FA enabled
- Rotate credentials monthly

## Files

```
.qwen/skills/gmail-watcher/
├── SKILL.md              # This file
├── scripts/
│   ├── gmail_watcher.py  # Main watcher script
│   └── gmail_auth.py     # Authentication helper
└── references/
    └── gmail-api-setup.md  # Setup guide
```

---

*Gmail Watcher Skill v0.2 (Silver Tier)*
