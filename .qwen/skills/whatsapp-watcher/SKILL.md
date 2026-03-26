---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for urgent messages using Playwright browser automation.
  Detects keywords like "urgent", "asap", "invoice", "payment" and creates
  action files in the vault. Requires WhatsApp Web session authentication.
  
  WARNING: Be aware of WhatsApp's Terms of Service when using automation.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web for urgent messages using browser automation.

## Prerequisites

### 1. Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2. Setup Session Directory

```bash
mkdir -p AI_Employee_Vault/Scripts/whatsapp_session
```

### 3. Initial Authentication

1. Run the watcher script
2. QR code will appear in terminal
3. Scan with WhatsApp mobile app
4. Session saved for future use

## Quick Start

```bash
# Start WhatsApp Watcher
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault
```

## Configuration

### Environment Variables

```bash
# Session Settings
WHATSAPP_SESSION_PATH=/path/to/whatsapp_session
WHATSAPP_CHECK_INTERVAL=30

# Keywords to detect (comma-separated)
WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,help
```

### Watcher Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `--interval` | 30s | Time between checks |
| `--keywords` | urgent,asap,invoice,payment,help | Keywords to detect |
| `--headless` | false | Run browser in background |

## How It Works

```
1. Watcher launches Chromium with persistent session
2. Navigates to WhatsApp Web
3. Scans for unread messages
4. Checks message text for keywords
5. Creates .md file in Needs_Action/
6. Marks message as processed
```

## Action File Format

```markdown
---
type: whatsapp
from: +1234567890
chat: John Doe
received: 2026-02-26T10:30:00
priority: high
status: pending
keywords: urgent, invoice
---

# WhatsApp Message

**From:** +1234567890 (John Doe)
**Received:** 2026-02-26 10:30
**Priority:** High
**Keywords:** urgent, invoice

## Message Content

Hi, I need the invoice sent urgently for payment processing...

## Suggested Actions

- [ ] Reply on WhatsApp
- [ ] Send invoice
- [ ] Follow up if needed

---
*Created by WhatsApp Watcher v0.2 (Silver Tier)*
```

## Usage Examples

### Basic Usage

```bash
# Start with defaults
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault
```

### Custom Keywords

```bash
# Detect specific keywords
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault \
  --keywords "pricing,quote,order,urgent"
```

### Visible Browser (Debug)

```bash
# Show browser window for debugging
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault --headless false
```

## Security Notes

⚠️ **Important:**

- WhatsApp session contains authentication data - keep secure
- Never commit session files to git
- Be aware of WhatsApp's Terms of Service
- Consider using WhatsApp Business API for production

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not appearing | Check terminal, wait 30 seconds |
| Session expired | Delete session folder and re-authenticate |
| No messages detected | Check WhatsApp Web is working manually |
| Browser crashes | Try `--headless false` for debugging |

## Files

```
.qwen/skills/whatsapp-watcher/
├── SKILL.md              # This file
├── scripts/
│   └── whatsapp_watcher.py  # Main watcher script
└── references/
    └── whatsapp-setup.md    # Setup guide
```

---

*WhatsApp Watcher Skill v0.2 (Silver Tier)*
