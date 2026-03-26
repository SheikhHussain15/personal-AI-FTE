# 🥈 Silver Tier Skills - AI Employee

**Status**: ✅ **SKILLS CREATED**

**Date**: 2026-02-26

---

## Overview

Silver Tier adds **6 new skills** to your AI Employee, enabling:
- Email monitoring (Gmail)
- WhatsApp message detection
- Email sending via MCP
- Human approval workflows
- LinkedIn auto-posting
- Multi-step plan management

---

## Skills Summary

| Skill | Type | Purpose | Status |
|-------|------|---------|--------|
| **gmail-watcher** | Watcher | Monitor Gmail for important emails | ✅ Created |
| **whatsapp-watcher** | Watcher | Monitor WhatsApp Web for urgent messages | ✅ Created |
| **email-mcp** | MCP Server | Send emails via Gmail API | ✅ Created |
| **approval-workflow** | Workflow | Human-in-the-loop approvals | ✅ Created |
| **linkedin-poster** | Action | Auto-post to LinkedIn | ✅ Created |
| **plan-manager** | Utility | Manage multi-step task plans | ✅ Created |

Plus existing skills:
| **browsing-with-playwright** | Browser | Web automation | ✅ Available |

---

## Installation

### 1. Install Dependencies

```bash
# For Gmail Watcher & Email MCP
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# For WhatsApp Watcher & LinkedIn Poster
pip install playwright
playwright install chromium
```

### 2. Verify Skills

```bash
ls .qwen/skills/
# Should show:
# - browsing-with-playwright
# - gmail-watcher
# - whatsapp-watcher
# - email-mcp
# - approval-workflow
# - linkedin-poster
# - plan-manager
```

---

## Quick Start by Skill

### Gmail Watcher

```bash
# Step 1: Authenticate
python .qwen/skills/gmail-watcher/scripts/gmail_auth.py --vault ../AI_Employee_Vault

# Step 2: Start watcher
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ../AI_Employee_Vault --interval 120
```

### WhatsApp Watcher

```bash
# Start watcher (QR code will appear)
python .qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --vault ../AI_Employee_Vault
```

### Email MCP (Sending)

```bash
# Step 1: Authenticate with send scope
python .qwen/skills/email-mcp/scripts/email_auth.py --vault ../AI_Employee_Vault

# Step 2: Start MCP server
python .qwen/skills/email-mcp/scripts/email_mcp_server.py --port 8809
```

### Approval Workflow

```bash
# Watch for approved actions
python .qwen/skills/approval-workflow/scripts/approval_watcher.py --vault ../AI_Employee_Vault

# Execute approved actions
python .qwen/skills/approval-workflow/scripts/approval_executor.py --vault ../AI_Employee_Vault
```

### LinkedIn Poster

```bash
# Create a post (requires approval)
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py \
  --vault ../AI_Employee_Vault \
  --content "Business update post..."
```

### Plan Manager

```bash
# Create a new plan
python .qwen/skills/plan-manager/scripts/create_plan.py \
  --vault ../AI_Employee_Vault \
  --task "Process monthly invoices" \
  --steps "Collect,Extract,Categorize,Enter,File,Update"
```

---

## Silver Tier Requirements Checklist

| Requirement | Skill | Status |
|-------------|-------|--------|
| Two or more Watcher scripts | gmail-watcher, whatsapp-watcher | ✅ |
| Auto-post on LinkedIn | linkedin-poster | ✅ |
| Plan.md reasoning loop | plan-manager | ✅ |
| MCP server for external action | email-mcp | ✅ |
| Human-in-the-loop approval | approval-workflow | ✅ |
| Basic scheduling | (Use cron/Task Scheduler with scripts) | ⏳ |
| All as Agent Skills | All skills in .qwen/skills/ | ✅ |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Employee (Silver)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Gmail      │  │  WhatsApp    │  │  Filesystem  │      │
│  │   Watcher    │  │   Watcher    │  │   Watcher    │      │
│  │  (Bronze+)   │  │  (Silver)    │  │   (Bronze)   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │  Needs_Action/  │                        │
│                  └────────┬────────┘                        │
│                           │                                 │
│              ┌────────────▼────────────┐                    │
│              │     Qwen Code Core      │                    │
│              │  + Plan Manager Skill   │                    │
│              └────────────┬────────────┘                    │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │               │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │   Email      │  │  LinkedIn    │  │  Approval    │      │
│  │   MCP        │  │   Poster     │  │  Workflow    │      │
│  │  (Silver)    │  │  (Silver)    │  │  (Silver)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
.qwen/skills/
├── browsing-with-playwright/    # [Existing] Browser automation
├── gmail-watcher/               # [NEW] Gmail monitoring
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── gmail_watcher.py
│   │   └── gmail_auth.py
│   └── references/
├── whatsapp-watcher/            # [NEW] WhatsApp monitoring
│   ├── SKILL.md
│   └── scripts/
│       └── whatsapp_watcher.py
├── email-mcp/                   # [NEW] Email sending
│   ├── SKILL.md
│   └── scripts/
├── approval-workflow/           # [NEW] HITL approvals
│   ├── SKILL.md
│   └── scripts/
├── linkedin-poster/             # [NEW] LinkedIn posting
│   ├── SKILL.md
│   └── scripts/
└── plan-manager/                # [NEW] Plan management
    ├── SKILL.md
    └── scripts/
```

---

## Usage Workflow

### Complete Email Processing Flow

```
1. Gmail Watcher detects new email
   ↓
2. Creates EMAIL_*.md in Needs_Action/
   ↓
3. Qwen Code reads and processes
   ↓
4. If reply needed → creates approval request
   ↓
5. Human approves (moves to Approved/)
   ↓
6. Email MCP sends reply
   ↓
7. Logs action, moves to Done/
```

### Complete LinkedIn Posting Flow

```
1. Qwen Code generates post content
   ↓
2. Creates post draft in Pending_Approval/
   ↓
3. Human reviews and approves
   ↓
4. LinkedIn Poster publishes
   ↓
5. Screenshot saved, logged
```

---

## Next Steps (Gold Tier)

To upgrade to Gold Tier, add:
- [ ] Odoo accounting integration
- [ ] Facebook/Instagram posting
- [ ] Twitter (X) integration
- [ ] Weekly CEO Briefing automation
- [ ] Error recovery & graceful degradation
- [ ] Comprehensive audit logging
- [ ] Ralph Wiggum persistence loop

---

## Troubleshooting

| Issue | Skill | Solution |
|-------|-------|----------|
| Gmail auth failed | gmail-watcher | Check credentials.json |
| WhatsApp QR timeout | whatsapp-watcher | Clear session, retry |
| Email send failed | email-mcp | Verify send scope |
| Approval not executing | approval-workflow | Check Approved/ folder |
| LinkedIn post failed | linkedin-poster | Re-authenticate session |
| Plan not updating | plan-manager | Check file permissions |

---

## Resources

- **Bronze Tier**: `../bronze-tier/README.md`
- **Hackathon Blueprint**: `../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Agent Skills Docs**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

---

*Silver Tier Skills Package v0.2 | AI Employee Hackathon 2026*
