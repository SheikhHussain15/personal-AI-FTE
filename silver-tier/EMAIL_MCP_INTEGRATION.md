# Email MCP + Gmail Watcher - Complete Integration Guide

## ✅ What's Been Created

| Component | Status | Location |
|-----------|--------|----------|
| **Gmail Watcher** | ✅ Working | `AI_Employee_Vault/Scripts/gmail_watcher.py` |
| **Email MCP Server** | ✅ Created | `.qwen/skills/email-mcp/scripts/email_mcp_server.py` |
| **Email Auth Script** | ✅ Created | `.qwen/skills/email-mcp/scripts/email_auth.py` |
| **MCP Client** | ✅ Created | `.qwen/skills/email-mcp/scripts/mcp_client.py` |
| **Setup Guide** | ✅ Created | `.qwen/skills/email-mcp/EMAIL_SETUP_GUIDE.md` |

---

## How It Works Together

```
┌─────────────────────────────────────────────────────────────────┐
│            Complete Email Automation Flow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INCOMING EMAIL:                                                 │
│  1. Gmail Watcher detects unread email                          │
│  2. Creates action file in Needs_Action/                        │
│  3. Qwen Code reads & drafts response                           │
│  4. Draft saved to Pending_Approval/                            │
│  5. Human reviews & approves (moves to Approved/)               │
│  6. Email MCP sends the email ✅                                 │
│  7. File moved to Done/Email/                                   │
│                                                                  │
│  OUTGOING EMAIL:                                                 │
│  1. Create email draft file                                     │
│  2. Move to Approved/                                           │
│  3. Email MCP sends automatically                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## MCP Server Architecture

### What is MCP?

**MCP (Model Context Protocol)** is a protocol that allows AI agents like Claude Code/Qwen Code to interact with external services through standardized tool calls.

### Email MCP Server Components:

```
Email MCP Server (email_mcp_server.py)
│
├── Tool: email_send
│   └── Sends email immediately via Gmail API
│
├── Tool: email_draft
│   └── Creates draft without sending
│
└── Tool: email_search
    └── Searches Gmail for messages
```

### How MCP Works:

1. **Server Runs** on port 8809
2. **Client Sends** JSON-RPC requests
3. **Server Executes** Gmail API calls
4. **Returns** result to client

**Example Request:**
```json
{
  "tool": "email_send",
  "params": {
    "to": "client@example.com",
    "subject": "Re: Project",
    "body": "Hi, thanks for your email..."
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "message_id": "18e4f2a3b5c6d7e8",
  "status": "sent"
}
```

---

## Step-by-Step Setup

### Step 1: Authenticate with Send Permissions

Your current Gmail token only has `readonly` scope. We need to add `send` scope.

```bash
cd C:\Users\hr773\Documents\GitHub\personal-AI-FTE\.qwen\skills\email-mcp\scripts
python email_auth.py --vault ../../../../AI_Employee_Vault
```

**What happens:**
1. Browser opens
2. Login to Gmail
3. Grant **send** permissions (NEW!)
4. Token saved with updated scopes

**Token location:**
```
AI_Employee_Vault/Scripts/token.json
```

---

### Step 2: Start Email MCP Server

```bash
cd .qwen/skills/email-mcp/scripts
python email_mcp_server.py --vault ../../../../AI_Employee_Vault --port 8809
```

**Expected output:**
```
Email MCP Server initialized on port 8809
Connected to Gmail API
Email MCP Server running on port 8809
Available tools: email_send, email_draft, email_search
```

**Keep this terminal open!** Server runs continuously.

---

### Step 3: Test Email Sending

#### Test with MCP Client:

```bash
cd .qwen/skills/email-mcp/scripts

# Send test email to yourself
python mcp_client.py call -u http://localhost:8809 ^
  -t email_send ^
  -p "{\"to\": \"hr7730774@gmail.com\", \"subject\": \"Test from AI Employee\", \"body\": \"This is a test email from the Email MCP server!\"}"
```

**Expected response:**
```json
{
  "success": true,
  "message_id": "18e4f2a3b5c6d7e8",
  "status": "sent"
}
```

✓ Check your Gmail inbox for the test email!

---

### Step 4: Integrate with Gmail Watcher

#### Complete Workflow Example:

**1. Email Arrives:**
```
From: client@company.com
Subject: Project Inquiry
```

**2. Gmail Watcher Creates:**
```
Needs_Action/EMAIL_Project_Inquiry_18e4f2a3.md
```

**3. Qwen Code Processes:**
```bash
cd AI_Employee_Vault
qwen "Read the email from client@company.com. Draft a professional response."
```

**4. Draft Created in Pending_Approval/:**
```markdown
---
type: email_send_request
to: client@company.com
subject: Re: Project Inquiry
status: pending
---

Hi,

Thank you for your inquiry. I'd be happy to discuss this project...

Best regards,
Hussain Raza
```

**5. Human Approves:**
- Review draft
- Move file from `Pending_Approval/` to `Approved/`

**6. Email MCP Sends:**
```bash
python mcp_client.py call -u http://localhost:8809 ^
  -t email_send ^
  -p "{\"to\": \"client@company.com\", \"subject\": \"Re: Project Inquiry\", \"body\": \"Hi,\\n\\nThank you...\"}"
```

**7. Move to Done:**
```bash
move Approved\EMAIL_Project_Inquiry_*.md Done\Email\
```

---

## Integration with Qwen Code / Claude Code

### Configure MCP in Claude Code:

**File:** `~/.config/claude-code/mcp.json`

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

### Then Claude Can Send Emails:

```bash
claude "Send an email to hr7730774@gmail.com with subject 'Meeting Tomorrow' and body 'Hi, just confirming our meeting at 2 PM tomorrow. Thanks!'"
```

Claude will use the Email MCP server to send!

---

## Security & Approval Workflow

### Why Approval is Important:

Email MCP **can** send emails automatically, but should it?

**Recommended Workflow:**
```
AI Drafts → Human Approves → MCP Sends
```

### Approval Thresholds:

| Email Type | Auto-Send? | Approval Required |
|------------|-----------|-------------------|
| Known contacts | ❌ No | ✅ YES |
| New contacts | ❌ No | ✅ YES |
| Bulk emails | ❌ No | ✅ YES |
| Invoices/Payments | ❌ No | ✅ YES |
| Test emails | ⚠️ Maybe | You decide |

### Best Practice:

**ALWAYS require human approval before sending.** The MCP server is powerful - use it responsibly!

---

## Troubleshooting

### Issue: "Token not found or invalid"

**Solution:**
```bash
# Delete old token
del AI_Employee_Vault\Scripts\token.json

# Re-authenticate with send scope
cd .qwen/skills/email-mcp/scripts
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
3. Check Gmail sent folder

**Test with client:**
```bash
python mcp_client.py call -u http://localhost:8809 ^
  -t email_send ^
  -p "{\"to\": \"hr7730774@gmail.com\", \"subject\": \"Test\", \"body\": \"Test\"}"
```

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| **Authenticate** | `python email_auth.py --vault ../../../../AI_Employee_Vault` |
| **Start MCP Server** | `python email_mcp_server.py --vault ../../../../AI_Employee_Vault --port 8809` |
| **Send Email** | `python mcp_client.py call -u http://localhost:8809 -t email_send -p '{...}'` |
| **Create Draft** | `python mcp_client.py call -u http://localhost:8809 -t email_draft -p '{...}'` |
| **Search Emails** | `python mcp_client.py call -u http://localhost:8809 -t email_search -p '{...}'` |
| **Stop Server** | Press Ctrl+C in server terminal |

---

## Files Created

```
.qwen/skills/email-mcp/
├── SKILL.md                    # Original skill doc
├── EMAIL_SETUP_GUIDE.md        # Complete setup guide (NEW)
└── scripts/
    ├── email_mcp_server.py     # MCP server (NEW)
    ├── email_auth.py           # Authentication (NEW)
    └── mcp_client.py           # Test client (NEW)

AI_Employee_Vault/
├── Needs_Action/
│   └── EMAIL_*.md             # New emails
├── Pending_Approval/
│   └── EMAIL_SEND_*.md        # Drafts awaiting approval
├── Approved/
│   └── EMAIL_SEND_*.md        # Ready to send
├── Done/
│   └── Email/                  # Sent emails
└── Scripts/
    └── token.json              # Gmail API token (updated)
```

---

## Next Steps

### 1. Authenticate (Required)
```bash
cd .qwen/skills/email-mcp/scripts
python email_auth.py --vault ../../../../AI_Employee_Vault
```

### 2. Start MCP Server
```bash
python email_mcp_server.py --vault ../../../../AI_Employee_Vault --port 8809
```

### 3. Test Sending
```bash
python mcp_client.py call -u http://localhost:8809 ^
  -t email_send ^
  -p "{\"to\": \"hr7730774@gmail.com\", \"subject\": \"Test\", \"body\": \"Email MCP is working!\"}"
```

### 4. Integrate with Workflow
- Process emails in Needs_Action/
- Draft responses with Qwen Code
- Approve and send via MCP

---

## Summary

✅ **Gmail Watcher** - Reads incoming emails  
✅ **Email MCP Server** - Sends outgoing emails  
✅ **Approval Workflow** - Human reviews before sending  
✅ **MCP Protocol** - Standardized AI-to-service communication  

**You now have complete email automation!** 📧✅

---

*AI Employee System - Silver Tier*
*Email MCP Integration v0.2*
*Created: 2026-03-02*
