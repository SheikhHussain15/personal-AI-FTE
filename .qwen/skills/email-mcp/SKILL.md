---
name: email-mcp
description: |
  Send emails via Gmail API using MCP (Model Context Protocol) server.
  Provides tools for sending, drafting, and searching emails.
  Requires Gmail API credentials with send permissions.
---

# Email MCP Skill

Send and manage emails via Gmail API using MCP server.

## Prerequisites

### 1. Gmail API Setup

Same as Gmail Watcher, but with send scope:

```bash
# Scope needed: https://www.googleapis.com/auth/gmail.send
```

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Authenticate with Send Scope

```bash
python .qwen/skills/email-mcp/scripts/email_auth.py --vault ../AI_Employee_Vault
```

## Quick Start

### Start MCP Server

```bash
# Start email MCP server
python .qwen/skills/email-mcp/scripts/email_mcp_server.py --port 8809
```

### Configure in Qwen Code

Add to MCP configuration:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": [".qwen/skills/email-mcp/scripts/email_mcp_server.py"],
      "env": {
        "GMAIL_TOKEN_PATH": "/path/to/token.json"
      }
    }
  }
}
```

## Available Tools

### `email_send`

Send an email immediately.

```json
{
  "to": "recipient@example.com",
  "subject": "Invoice #1234",
  "body": "Please find attached...",
  "cc": "manager@example.com"
}
```

### `email_draft`

Create a draft without sending.

```json
{
  "to": "recipient@example.com",
  "subject": "Proposal",
  "body": "Here is the proposal..."
}
```

### `email_search`

Search Gmail for messages.

```json
{
  "query": "is:unread from:client@example.com"
}
```

## Usage Examples

### Send Invoice Email

```bash
python .qwen/skills/email-mcp/scripts/mcp_client.py call \
  -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "client@example.com", "subject": "Invoice #1234", "body": "Please pay $500 by end of month."}'
```

### Create Draft

```bash
python .qwen/skills/email-mcp/scripts/mcp_client.py call \
  -u http://localhost:8809 \
  -t email_draft \
  -p '{"to": "partner@example.com", "subject": "Partnership", "body": "Lets discuss..."}'
```

## Integration with Qwen Code

After processing emails in Needs_Action:

```bash
cd AI_Employee_Vault
qwen "Reply to the urgent email from client@example.com using email MCP server"
```

## Approval Workflow

For sensitive emails, use approval pattern:

1. Create draft in `/Pending_Approval/`
2. Human moves to `/Approved/`
3. MCP server sends email

## Security Notes

- Token provides send access - keep secure
- Never commit token.json to git
- Use dry-run mode for testing
- Implement rate limiting

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run email_auth.py |
| Send failed | Check Gmail send scope |
| Server not starting | Check port 8809 is free |

## Files

```
.qwen/skills/email-mcp/
├── SKILL.md
├── scripts/
│   ├── email_mcp_server.py
│   ├── email_auth.py
│   └── mcp_client.py
└── references/
    └── gmail-send-api.md
```

---

*Email MCP Skill v0.2 (Silver Tier)*
