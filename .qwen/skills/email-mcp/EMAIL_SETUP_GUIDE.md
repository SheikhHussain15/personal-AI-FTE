# Email MCP - Complete Setup Guide

## Overview

Email MCP allows your AI Employee to **send emails** via Gmail API with proper approval workflow.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Email Sending Workflow                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Gmail Watcher detects email → Creates action file   │
│     ↓                                                    │
│  2. Qwen Code reads & drafts response                   │
│     ↓                                                    │
│  3. Draft saved to Pending_Approval/                    │
│     ↓                                                    │
│  4. Human reviews & moves to Approved/                  │
│     ↓                                                    │
│  5. Email MCP sends the email                           │
│     ↓                                                    │
│  6. File moved to Done/Email/                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Gmail API Credentials

You already have these for Gmail Watcher!

**Location:** `credentials.json` in project root

### 2. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## Step-by-Step Setup

### Step 1: Authenticate with Send Permissions

Your current token only has `readonly` scope. We need to add `send` scope.

```bash
cd .qwen/skills/email-mcp/scripts
python email_auth.py --vault ../../../../AI_Employee_Vault
```

**What happens:**
1. Browser opens
2. Login to Gmail
3. Grant send permissions
4. Token saved with new scopes

**Token will be saved to:**
```
AI_Employee_Vault/Scripts/token.json
```

---

### Step 2: Start Email MCP Server

```bash
python email_mcp_server.py --vault ../../../../AI_Employee_Vault --port 8809
```

**Server starts on port 8809**

You should see:
```
Email MCP Server initialized on port 8809
Connected to Gmail API
Email MCP Server running on port 8809
Available tools: email_send, email_draft, email_search
```

---

### Step 3: Configure in Qwen Code / Claude Code

Add to your MCP configuration:

**File:** `~/.config/claude-code/mcp.json` (or Qwen Code config)

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": [
        "C:/Users/hr773/Documents/GitHub/personal-AI-FTE/.qwen/skills/email-mcp/scripts/email_mcp_server.py"
      ],
      "env": {
        "GMAIL_TOKEN_PATH": "C:/Users/hr773/Documents/GitHub/personal-AI-FTE/AI_Employee_Vault/Scripts/token.json"
      }
    }
  }
}
```

---

### Step 4: Test Email Sending

#### Test with MCP Client:

```bash
cd .qwen/skills/email-mcp/scripts

# Send test email
python mcp_client.py call -u http://localhost:8809 -t email_send -p "{\"to\": \"your-email@gmail.com\", \"subject\": \"Test from AI Employee\", \"body\": \"This is a test email from the Email MCP server!\"}"
```

#### Expected Response:
```json
{
  "success": true,
  "message_id": "18e4f2a3b5c6d7e8",
  "thread_id": "18e4f2a3b5c6d7e8",
  "status": "sent",
  "timestamp": "2026-03-02T03:00:00"
}
```

---

## Usage Examples

### Send Email Directly

```bash
python mcp_client.py call -u http://localhost:8809 \
  -t email_send \
  -p '{
    "to": "client@example.com",
    "subject": "Re: Project Update",
    "body": "Hi,\n\nThank you for your email. The project is on track.\n\nBest regards,\nHussain"
  }'
```

### Create Draft (Don't Send)

```bash
python mcp_client.py call -u http://localhost:8809 \
  -t email_draft \
  -p '{
    "to": "partner@example.com",
    "subject": "Partnership Proposal",
    "body": "Hi,\n\nI would like to discuss a partnership...\n\nBest,\nHussain"
  }'
```

### Search Emails

```bash
python mcp_client.py call -u http://localhost:8809 \
  -t email_search \
  -p '{
    "query": "is:unread from:linkedin",
    "max_results": 5
  }'
```

---

## Integration with Gmail Watcher

### Complete Workflow:

#### 1. Email Arrives
```
Gmail Watcher detects unread email
Creates: Needs_Action/EMAIL_Client_Inquiry_18e4f2a3.md
```

#### 2. AI Processes
```bash
cd AI_Employee_Vault
qwen "Read the email from client@example.com in Needs_Action. Draft a professional response."
```

#### 3. Draft Created
```markdown
---
type: email_reply
status: pending_approval
to: client@example.com
subject: Re: Project Inquiry
---

## Draft Content

Hi,

Thank you for your inquiry...

---
*Ready for approval*
```

#### 4. Human Approval
- Review draft in `Pending_Approval/`
- Move to `Approved/` if OK

#### 5. Send via MCP
```bash
# Orchestrator or manual trigger
python mcp_client.py call -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "client@example.com", "subject": "Re: Project Inquiry", "body": "Hi,\n\nThank you..."}'
```

#### 6. Move to Done
```bash
move Approved\EMAIL_Client_Inquiry_*.md Done\Email\
```

---

## Approval Workflow Files

### Pending Approval File Format:

```markdown
---
type: email_send_request
action: email_send
created: 2026-03-02T03:00:00
status: pending
priority: normal
---

# Email Send Request

**To:** client@example.com  
**Subject:** Re: Project Inquiry  
**Created:** 2026-03-02 03:00

## Content

Hi,

Thank you for your inquiry. I would be happy to discuss this project...

Best regards,
Hussain Raza

## Instructions

### To Approve
1. Review the email content above
2. Move this file to `/Approved` folder
3. Email MCP will send it automatically

### To Reject
1. Move this file to `/Rejected` folder
2. Add reason for rejection in notes below

## Notes

*Add comments or feedback here*

---
*Created by AI Employee System*
```

---

## Security & Best Practices

### Token Security
- ✅ Token saved to `Scripts/token.json`
- ✅ Already in `.gitignore` (won't commit to git)
- ⚠️ Never share token.json file
- ⚠️ Rotate token every 90 days

### Approval Workflow
- ✅ ALWAYS require approval for new contacts
- ✅ ALWAYS require approval for bulk emails
- ✅ Review all drafts before sending
- ⚠️ Never auto-send without approval

### Rate Limiting
- Gmail limit: 500 emails/day (free), 2000/day (Workspace)
- Recommended: Max 50 emails/hour
- MCP server enforces rate limiting

---

## Troubleshooting

### Issue: "Token not found"

**Solution:**
```bash
python email_auth.py --vault ../../../../AI_Employee_Vault
```

---

### Issue: "Send failed - insufficient permissions"

**Solution:**
1. Delete old token: `del AI_Employee_Vault\Scripts\token.json`
2. Re-authenticate with send scope:
   ```bash
   python email_auth.py --vault ../../../../AI_Employee_Vault
   ```

---

### Issue: "MCP Server won't start"

**Check:**
1. Port 8809 is not in use
2. Token file exists
3. Gmail API libraries installed

**Test:**
```bash
python email_mcp_server.py --vault ../../../../AI_Employee_Vault --port 8809
```

---

### Issue: "Email not sending"

**Check Gmail:**
1. Visit: https://myaccount.google.com/permissions
2. Verify AI Employee has access
3. Check Gmail sent folder for email

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| Authenticate | `python email_auth.py --vault ../../../../AI_Employee_Vault` |
| Start Server | `python email_mcp_server.py --vault ../../../../AI_Employee_Vault --port 8809` |
| Send Email | `python mcp_client.py call -u http://localhost:8809 -t email_send -p '{...}'` |
| Create Draft | `python mcp_client.py call -u http://localhost:8809 -t email_draft -p '{...}'` |
| Search Emails | `python mcp_client.py call -u http://localhost:8809 -t email_search -p '{...}'` |

---

## Files Reference

```
.qwen/skills/email-mcp/
├── SKILL.md                    # Skill documentation
├── scripts/
│   ├── email_mcp_server.py     # MCP server (sends emails)
│   ├── email_auth.py           # Authentication script
│   └── mcp_client.py           # MCP client for testing
└── references/
    └── gmail-send-api.md       # Gmail API reference

AI_Employee_Vault/
├── Pending_Approval/
│   └── EMAIL_SEND_*.md        # Awaiting approval
├── Approved/
│   └── EMAIL_SEND_*.md        # Ready to send
├── Done/
│   └── Email/                  # Sent emails
└── Scripts/
    └── token.json              # Gmail API token
```

---

## Next Steps

1. **Authenticate:** Run `email_auth.py`
2. **Start Server:** Run `email_mcp_server.py --port 8809`
3. **Test:** Send a test email
4. **Integrate:** Use with Gmail Watcher workflow

---

*AI Employee System - Silver Tier*
*Email MCP v0.2*
*Last Updated: 2026-03-02*
