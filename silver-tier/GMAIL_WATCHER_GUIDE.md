# Gmail Watcher - Complete Guide

## ✅ Current Status: READY TO USE

Your Gmail Watcher is **fully configured** and ready to monitor your inbox!

---

## What is Gmail Watcher?

Gmail Watcher is an AI Employee skill that:
- **Monitors** your Gmail inbox 24/7
- **Detects** new, unread, important emails
- **Creates** action files in your Obsidian vault
- **Enables** AI to process and respond to emails automatically

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                  Gmail Watcher Flow                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Gmail Watcher polls Gmail API every 2 minutes        │
│     ↓                                                    │
│  2. Fetches unread, important messages                   │
│     ↓                                                    │
│  3. Extracts: From, Subject, Date, Preview               │
│     ↓                                                    │
│  4. Creates .md action file in Needs_Action/             │
│     ↓                                                    │
│  5. Marks message as processed (won't duplicate)         │
│     ↓                                                    │
│  6. Qwen Code processes the action file                  │
│     ↓                                                    │
│  7. AI can: Reply, Forward, Create Tasks, Archive        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Your Setup Status

| Component | Status | Details |
|-----------|--------|---------|
| Gmail API Libraries | ✅ Installed | google-api-python-client v2.190.0 |
| Credentials | ✅ Configured | credentials.json (project: first-fte) |
| Token | ✅ Active | token.json (authenticated) |
| Watcher Script | ✅ Ready | gmail_watcher.py |

**You're all set! No additional setup needed.**

---

## Quick Start

### Start Gmail Watcher

**New simplified location:**
```bash
cd AI_Employee_Vault\Scripts
python gmail_watcher.py --vault .. --interval 120
```

**Or use the batch file:**
```bash
start-gmail-watcher.bat
```

**Or start all watchers together:**
```bash
silver-tier\start-watchers.bat
```
(This starts Gmail, LinkedIn, and Filesystem watchers together)

---

## What Happens When Email Arrives

### Example: Client sends urgent email

**Email Received:**
```
From: client@company.com
Subject: Urgent: Project Invoice Needed
Date: 2026-02-28 10:30 AM
Preview: Hi, Please send the invoice for the recent project...
```

**Action File Created in `Needs_Action/`:**

```markdown
---
type: email
from: client@company.com
subject: Urgent: Project Invoice Needed
received: 2026-02-28T10:30:00
priority: high
status: pending
message_id: 18e4f2a3b5c6d7e8
---

# Email: Urgent: Project Invoice Needed

**From:** client@company.com
**Received:** 2026-02-28 10:30
**Priority:** High

## Content

Hi, Please send the invoice for the recent project...

## Suggested Actions

- [ ] Reply to sender
- [ ] Create and send invoice
- [ ] Archive after processing

## Notes

*Add notes or context here*

---
*Created by Gmail Watcher v0.2*
```

---

## Configuration

### Watcher Settings

| Setting | Default | Can Change |
|---------|---------|------------|
| Check Interval | 120 seconds | Yes |
| Monitored Labels | INBOX, IMPORTANT | Yes |
| Priority Keywords | urgent, asap, invoice, payment | Yes |
| Max Results | 10 emails per check | Yes |

### Change Check Interval

```bash
# Check every 5 minutes (300 seconds)
python gmail_watcher.py --vault ../../../AI_Employee_Vault --interval 300

# Check every minute (60 seconds)
python gmail_watcher.py --vault ../../../AI_Employee_Vault --interval 60
```

### Custom Keywords for Priority

Edit `gmail_watcher.py` line 58:
```python
self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'important']
```

Add your own keywords:
```python
self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'important', 'deadline', 'review']
```

---

## Integration with AI Employee

### Workflow Example

```
1. Gmail Watcher detects new email
   ↓
2. Creates file in Needs_Action/
   ↓
3. Filesystem Watcher notifies orchestrator
   ↓
4. Qwen Code reads the email
   ↓
5. AI determines action needed
   ↓
6. Creates response draft / task / etc.
   ↓
7. Moves to Approved/ if action needed
   ↓
8. Human reviews and approves
   ↓
9. AI executes (sends email, creates invoice, etc.)
```

### Process Emails with Qwen Code

```bash
cd AI_Employee_Vault
qwen "Process new emails in Needs_Action folder. Reply to urgent ones and create invoices for payment requests."
```

---

## Email Filtering

### What Emails Get Flagged?

Gmail Watcher monitors:
- ✅ **Unread** emails
- ✅ **Important** emails (as marked by Gmail)
- ✅ Emails in **INBOX**

### Gmail's "Important" Detection

Gmail automatically marks emails as important based on:
- Sender frequency
- Your past interactions
- Keywords in subject/content
- Direct emails (not newsletters)

### Improve Gmail Filtering

1. **Star important senders**
2. **Mark emails as important** manually
3. **Create Gmail filters** for specific senders
4. **Use labels** for categorization

---

## Monitoring & Logs

### Check Watcher Status

```bash
# View latest logs
type AI_Employee_Vault\Logs\watcher_*.log

# Or use PowerShell
Get-Content AI_Employee_Vault\Logs\watcher_*.log -Tail 20
```

### Sample Log Output

```
2026-02-28 10:30:15 - GmailWatcher - INFO - Connected to Gmail API
2026-02-28 10:30:15 - GmailWatcher - INFO - Gmail Watcher ready
2026-02-28 10:32:15 - GmailWatcher - INFO - Checking for new emails...
2026-02-28 10:32:16 - GmailWatcher - INFO - No new emails
2026-02-28 10:34:16 - GmailWatcher - INFO - Checking for new emails...
2026-02-28 10:34:17 - GmailWatcher - INFO - Found 1 new email(s)
2026-02-28 10:34:17 - GmailWatcher - INFO - Created action file: EMAIL_Urgent_Project_18e4f2a3.md
```

### View Created Action Files

```bash
# List pending email actions
dir AI_Employee_Vault\Needs_Action\EMAIL_*.md

# List processed emails
dir AI_Employee_Vault\Done\Email\
```

---

## Troubleshooting

### Issue: "Gmail credentials not found"

**Solution:**
Your credentials are already set up at:
```
C:\Users\hr773\Documents\GitHub\personal-AI-FTE\credentials.json
```

If you need to re-authenticate:
```bash
cd .qwen/skills/gmail-watcher/scripts
python gmail_auth.py --vault ../../../AI_Employee_Vault
```

### Issue: "No emails detected"

**Check:**
1. Are emails marked as **Important** by Gmail?
2. Are emails **Unread**?
3. Check Gmail spam folder (watcher ignores spam)

**Test:**
- Send yourself an email from another account
- Mark it as important (click star)
- Wait 2 minutes

### Issue: "Token expired"

**Solution:**
```bash
# Delete old token
del AI_Employee_Vault\Scripts\token.json

# Re-authenticate
cd .qwen/skills/gmail-watcher/scripts
python gmail_auth.py --vault ../../../AI_Employee_Vault
```

### Issue: "API quota exceeded"

**Gmail API Limits:**
- 1,000,000 units per day
- Each check uses ~5 units
- At 120s interval: ~36 checks/hour = ~180 units/hour

**Solution:**
- Reduce check frequency (increase interval)
- Wait 24 hours for quota reset

---

## Best Practices

### Check Interval

| Use Case | Recommended Interval |
|----------|---------------------|
| Personal email | 300 seconds (5 min) |
| Business email | 120 seconds (2 min) |
| High priority | 60 seconds (1 min) |
| Testing | 30 seconds |

### Email Management

1. **Review daily** - Check `Needs_Action/` folder each morning
2. **Archive processed** - Move completed emails to `Done/Email/`
3. **Set up filters** - Use Gmail filters for auto-categorization
4. **Use labels** - Create Gmail labels for different email types

### Security

- ✅ Never share `credentials.json` or `token.json`
- ✅ Both files are in `.gitignore` (won't be committed)
- ✅ Token auto-refreshes when expired
- ✅ Read-only access (can't send emails without approval)

---

## Advanced Usage

### Monitor Specific Labels

```bash
python gmail_watcher.py --vault ../../../AI_Employee_Vault \
  --labels "INBOX,IMPORTANT,Work"
```

### Search Queries

Customize what emails to fetch by editing the search query in `gmail_watcher.py`:

```python
# Line 128
q='is:unread is:important from:@client.com'  # Only from clients
q='is:unread subject:invoice'  # Only invoices
q='is:unread after:2026/02/28'  # Only today's emails
```

### Batch Processing

Process multiple emails at once:

```bash
cd AI_Employee_Vault
qwen "Process all emails in Needs_Action folder. Create a summary of urgent items and draft responses for each."
```

---

## Complete Workflow Example

### Scenario: Client requests invoice

**1. Email arrives:**
```
From: client@startup.com
Subject: Invoice for Phase 1
Body: Hi, please send invoice for Phase 1 completion...
```

**2. Gmail Watcher (2 minutes later):**
- Detects unread, important email
- Creates: `Needs_Action/EMAIL_Invoice_Phase1_18e4f2a3.md`
- Logs: "Created action file for client@startup.com"

**3. You (or Qwen Code) process:**
```bash
qwen "Read the invoice request email. Draft a professional response and create an invoice template."
```

**4. AI creates:**
- Email draft response
- Invoice markdown file
- Task in Plans/ folder

**5. You review and approve:**
- Move response to `Approved/`
- AI sends email via Email MCP
- Move original to `Done/Email/`

---

## Files Reference

```
.qwen/skills/gmail-watcher/
├── SKILL.md                    # Skill documentation
├── scripts/
│   ├── gmail_watcher.py        # Main watcher script
│   └── gmail_auth.py           # Authentication helper
└── references/
    └── gmail-api-setup.md      # Setup guide

AI_Employee_Vault/
├── Needs_Action/
│   └── EMAIL_*.md             # New email action files
├── Done/
│   └── Email/                  # Processed emails
└── Logs/
    └── watcher_*.log           # Activity logs
```

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| Start watcher | `cd AI_Employee_Vault\Scripts` then `python gmail_watcher.py --vault ..` |
| Custom interval | `python gmail_watcher.py --vault .. --interval 300` |
| View logs | `type AI_Employee_Vault\Logs\watcher_*.log` |
| List pending emails | `dir AI_Employee_Vault\Needs_Action\EMAIL_*.md` |
| Re-authenticate | `cd AI_Employee_Vault\Scripts` then `python gmail_auth.py --vault ..` |
| Quick start | Double-click `start-gmail-watcher.bat` |

---

## Support

For issues:
1. Check logs: `AI_Employee_Vault/Logs/watcher_*.log`
2. Verify token exists: `AI_Employee_Vault/Scripts/token.json`
3. Test Gmail API: Run `gmail_auth.py`
4. Review this guide

---

*AI Employee System - Silver Tier*
*Last Updated: 2026-02-28*
*Gmail Watcher v0.2*
