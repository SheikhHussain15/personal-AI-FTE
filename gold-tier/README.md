# 🥇 Gold Tier - AI Employee (Autonomous Employee)

**Status**: 🚧 **IN DEVELOPMENT**

**Date**: 2026-03-08

---

## Overview

Gold Tier transforms your AI Employee into a fully **autonomous business partner** with:
- **Odoo ERP Integration** - Full accounting and business management
- **Facebook/Instagram Integration** - Social media automation
- **Twitter (X) Integration** - Twitter posting and monitoring
- **Weekly CEO Briefing** - Autonomous business audits
- **Error Recovery** - Graceful degradation and retry logic
- **Comprehensive Audit Logging** - Full action tracking
- **Ralph Wiggum Loop** - Persistent autonomous task completion

---

## Gold Tier Skills Summary

| Skill | Type | Purpose | Status |
|-------|------|---------|--------|
| **odoo-mcp** | MCP Server | Odoo ERP integration (accounting, invoices, payments) | 🚧 |
| **facebook-watcher** | Watcher | Monitor Facebook/Instagram messages and mentions | 🚧 |
| **facebook-poster** | Action | Post to Facebook/Instagram | 🚧 |
| **twitter-watcher** | Watcher | Monitor Twitter mentions and DMs | 🚧 |
| **twitter-poster** | Action | Post tweets and threads | 🚧 |
| **ceo-briefing** | Utility | Generate weekly CEO briefings | 🚧 |
| **audit-logger** | Utility | Comprehensive action logging | 🚧 |
| **error-recovery** | Utility | Retry logic and graceful degradation | 🚧 |
| **ralph-wiggum** | Loop | Persistent autonomous execution | 🚧 |

Plus all Silver Tier skills:
- ✅ gmail-watcher
- ✅ whatsapp-watcher
- ✅ email-mcp
- ✅ approval-workflow
- ✅ linkedin-poster
- ✅ plan-manager
- ✅ browsing-with-playwright

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI EMPLOYEE (GOLD TIER)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PERCEPTION LAYER (Watchers)                 │   │
│  ├──────────────┬──────────────┬──────────────┬─────────────┤   │
│  │ Gmail        │ WhatsApp     │ Facebook     │ Twitter     │   │
│  │ Watcher      │ Watcher      │ Watcher      │ Watcher     │   │
│  └──────┬───────┴──────┬───────┴──────┬───────┴──────┬──────┘   │
│         │             │             │              │            │
│         └─────────────┴─────────────┴──────────────┘            │
│                           │                                      │
│                  ┌────────▼────────┐                             │
│                  │  Needs_Action/  │                             │
│                  └────────┬────────┘                             │
│                           │                                      │
│              ┌────────────▼────────────┐                         │
│              │     Qwen Code Core      │                         │
│              │  + Ralph Wiggum Loop    │                         │
│              └────────────┬────────────┘                         │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                    │
│         │                 │                 │                    │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐           │
│  │   Social     │  │   Business   │  │   Approval   │           │
│  │   Posters    │  │   Actions    │  │   Workflow   │           │
│  │ (FB/Twitter) │  │   (Odoo)     │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              SUPPORT LAYER                               │   │
│  ├──────────────────┬──────────────────┬──────────────────┤   │
│  │ Audit Logger     │ Error Recovery   │ CEO Briefing     │   │
│  │ (All Actions)    │ (Retry Logic)    │ (Weekly Report)  │   │
│  └──────────────────┴──────────────────┴──────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

Ensure all Silver Tier requirements are met first, then:

```bash
# Install Odoo MCP dependencies
pip install requests python-dotenv

# Install Facebook/Instagram dependencies
pip install facebook-business playwright
playwright install chromium

# Install Twitter dependencies
pip install tweepy

# Install Docker (for Odoo)
# Download from: https://www.docker.com/products/docker-desktop
```

### Docker Setup for Odoo

```bash
# Navigate to gold-tier/docker
cd gold-tier/docker

# Start Odoo Community
docker-compose up -d

# Verify Odoo is running
curl http://localhost:8069
```

---

## Quick Start by Skill

### Odoo MCP (Accounting Integration)

```bash
# Step 1: Start Odoo (Docker)
cd gold-tier/docker
docker-compose up -d

# Step 2: Configure Odoo connection
python odoo-mcp/scripts/odoo_config.py \
  --url http://localhost:8069 \
  --db odoo \
  --username admin \
  --password admin

# Step 3: Start Odoo MCP server
python odoo-mcp/scripts/odoo_mcp_server.py --port 8810
```

### Facebook/Instagram Integration

```bash
# Step 1: Authenticate with Meta
python facebook-integration/scripts/facebook_auth.py \
  --app-id YOUR_APP_ID \
  --app-secret YOUR_APP_SECRET

# Step 2: Start Facebook watcher
python facebook-integration/scripts/facebook_watcher.py \
  --vault ../AI_Employee_Vault \
  --interval 60

# Step 3: Post to Facebook (requires approval)
python facebook-integration/scripts/facebook_poster.py \
  --vault ../AI_Employee_Vault \
  --content "Business update..." \
  --platform facebook,instagram
```

### Twitter (X) Integration

```bash
# Step 1: Configure Twitter API
python twitter-integration/scripts/twitter_config.py \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET \
  --access-token YOUR_TOKEN \
  --access-secret YOUR_TOKEN_SECRET

# Step 2: Start Twitter watcher
python twitter-integration/scripts/twitter_watcher.py \
  --vault ../AI_Employee_Vault \
  --interval 30

# Step 3: Post tweet (requires approval)
python twitter-integration/scripts/twitter_poster.py \
  --vault ../AI_Employee_Vault \
  --content "Business update..."
```

### CEO Briefing Generator

```bash
# Generate weekly briefing
python ceo-briefing/scripts/generate_briefing.py \
  --vault ../AI_Employee_Vault \
  --period last_week

# Schedule for every Monday at 7 AM (Windows Task Scheduler)
schtasks /create /tn "CEO_Briefing" /tr "python ceo-briefing/scripts/generate_briefing.py" /sc weekly /d MON /st 07:00
```

### Audit Logger

```bash
# Start audit logging (runs with all other watchers)
python audit-logger/scripts/audit_logger.py \
  --vault ../AI_Employee_Vault \
  --log-file ../AI_Employee_Vault/Logs/audit_log.json
```

### Ralph Wiggum Loop

```bash
# Start autonomous task execution
python ralph-wiggum/scripts/ralph_loop.py \
  --vault ../AI_Employee_Vault \
  --task "Process all items in Needs_Action" \
  --max-iterations 10
```

---

## Gold Tier Requirements Checklist

| Requirement | Skill | Status |
|-------------|-------|--------|
| All Silver requirements | (See silver-tier/README.md) | ✅ |
| Full cross-domain integration | All skills integrated | 🚧 |
| Odoo accounting system | odoo-mcp | 🚧 |
| Facebook/Instagram integration | facebook-watcher, facebook-poster | 🚧 |
| Twitter (X) integration | twitter-watcher, twitter-poster | 🚧 |
| Multiple MCP servers | odoo-mcp, email-mcp, etc. | 🚧 |
| Weekly Business Audit | ceo-briefing | 🚧 |
| Error recovery | error-recovery | 🚧 |
| Comprehensive audit logging | audit-logger | 🚧 |
| Ralph Wiggum loop | ralph-wiggum | 🚧 |
| Architecture documentation | This README | 🚧 |

---

## Odoo Docker Compose Setup

### docker-compose.yml

```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0-community
    container_name: ai_employee_odoo
    ports:
      - "8069:8069"
    environment:
      - ODOO_ADMIN_PASSWORD=admin
      - ODOO_DB=odoo
    volumes:
      - odoo-data:/var/lib/odoo
      - ./odoo-config:/etc/odoo
    restart: unless-stopped

  db:
    image: postgres:15
    container_name: ai_employee_odoo_db
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  odoo-data:
  postgres-data:
```

---

## Folder Structure

```
gold-tier/
├── README.md
├── docker/
│   ├── docker-compose.yml
│   └── odoo-config/
├── odoo-mcp/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── odoo_config.py
│   │   ├── odoo_mcp_server.py
│   │   ├── odoo_client.py
│   │   └── modules/
│   │       ├── accounting.py
│   │       ├── invoices.py
│   │       └── payments.py
│   └── references/
│       └── odoo-api-docs.md
├── facebook-integration/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── facebook_auth.py
│   │   ├── facebook_watcher.py
│   │   ├── facebook_poster.py
│   │   └── instagram_poster.py
│   └── references/
│       └── graph-api-docs.md
├── twitter-integration/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── twitter_config.py
│   │   ├── twitter_watcher.py
│   │   └── twitter_poster.py
│   └── references/
│       └── twitter-api-docs.md
├── ceo-briefing/
│   ├── SKILL.md
│   └── scripts/
│       ├── generate_briefing.py
│       ├── analyze_revenue.py
│       └── identify_bottlenecks.py
├── audit-logger/
│   ├── SKILL.md
│   └── scripts/
│       └── audit_logger.py
├── error-recovery/
│   ├── SKILL.md
│   └── scripts/
│       ├── retry_handler.py
│       └── graceful_degradation.py
└── ralph-wiggum/
    ├── SKILL.md
    └── scripts/
        └── ralph_loop.py
```

---

## Usage Workflows

### Complete Invoice Processing Flow (Odoo)

```
1. WhatsApp message received: "Send invoice for January"
   ↓
2. WhatsApp Watcher creates file in Needs_Action/
   ↓
3. Qwen Code reads and creates invoice draft
   ↓
4. Odoo MCP creates invoice in Odoo (draft state)
   ↓
5. Creates approval request for sending
   ↓
6. Human approves (moves to Approved/)
   ↓
7. Email MCP sends invoice to client
   ↓
8. Odoo MCP marks invoice as posted
   ↓
9. Audit Logger records all actions
   ↓
10. Files moved to Done/
```

### Complete Social Media Posting Flow

```
1. Qwen Code generates post content based on business goals
   ↓
2. Creates draft in Pending_Approval/ for each platform
   ↓
3. Human reviews and approves
   ↓
4. Facebook/Instagram Poster publishes
   ↓
5. Twitter Poster publishes
   ↓
6. LinkedIn Poster publishes
   ↓
7. Screenshots saved, engagement tracked
   ↓
8. Audit Logger records all actions
```

### Weekly CEO Briefing Flow

```
1. Scheduled trigger (Monday 7 AM)
   ↓
2. CEO Briefing reads Business_Goals.md
   ↓
3. Analyzes Accounting/ transactions (from Odoo)
   ↓
4. Reviews Done/ folder for completed tasks
   ↓
5. Checks Needs_Action/ for bottlenecks
   ↓
6. Generates Briefings/YYYY-MM-DD_CEO_Briefing.md
   ↓
7. Creates action items for Monday
   ↓
8. Notifies human via email/WhatsApp
```

---

## API Configuration

### Meta (Facebook/Instagram) App Setup

1. Go to [Meta Developers](https://developers.facebook.com/)
2. Create new app → Business type
3. Add products: Facebook Login, Instagram Graph API
4. Get App ID and App Secret
5. Configure OAuth redirect URI
6. Generate long-lived access token

### Twitter API Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create new project and app
3. Get API Key, API Secret, Access Token, Access Secret
4. Configure callback URI
5. Set permissions (Read + Write)

### Odoo Configuration

1. Enable Developer Mode in Odoo
2. Go to Settings → Technical → API
3. Create API user with appropriate permissions
4. Note database name, URL, username, password

---

## Security Considerations

### Credential Management

```bash
# .env file (NEVER commit)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=secure_password

META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=your_long_lived_token

TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_token_secret
```

### Permission Boundaries (Gold Tier)

| Action Category | Auto-Approve | Require Approval |
|-----------------|--------------|------------------|
| Odoo Invoice Draft | ✅ | - |
| Odoo Invoice Post | - | ✅ Always |
| Odoo Payment Entry | - | ✅ Always |
| Facebook Post | - | ✅ Always |
| Instagram Post | - | ✅ Always |
| Twitter Post | - | ✅ Always |
| Email Reply (known) | ✅ | - |
| Email Reply (new) | - | ✅ |

---

## Error Recovery

### Retry Logic

```python
# Automatic retry with exponential backoff
@retry(max_attempts=3, base_delay=1, max_delay=60)
def call_odoo_api(endpoint, params):
    # May raise TransientError
    pass
```

### Graceful Degradation

| Component Failure | Degradation Strategy |
|-------------------|---------------------|
| Odoo unavailable | Queue accounting actions locally |
| Facebook API down | Skip FB, post to others |
| Twitter rate limit | Queue tweets, retry later |
| All social down | Log error, notify human |

---

## Audit Logging Format

```json
{
  "timestamp": "2026-03-08T10:30:00Z",
  "action_type": "odoo_invoice_create",
  "actor": "qwen_code",
  "target": "Client A",
  "parameters": {
    "amount": 1500.00,
    "description": "January 2026 Services"
  },
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success",
  "odoo_invoice_id": "INV/2026/0001"
}
```

---

## Troubleshooting

| Issue | Skill | Solution |
|-------|-------|----------|
| Odoo connection failed | odoo-mcp | Check Docker container, verify URL |
| Facebook auth expired | facebook-integration | Refresh long-lived token |
| Twitter rate limited | twitter-integration | Wait 15 min, reduce frequency |
| Briefing not generating | ceo-briefing | Check Odoo connection, verify data |
| Ralph loop stuck | ralph-wiggum | Check max iterations, review logs |
| Audit log full | audit-logger | Archive old logs, increase retention |

---

## Next Steps (Platinum Tier)

To upgrade to Platinum Tier, add:
- [ ] Cloud deployment (24/7 always-on)
- [ ] Cloud + Local split architecture
- [ ] A2A (Agent-to-Agent) communication
- [ ] Work-Zone Specialization
- [ ] Git-based vault sync
- [ ] Production security hardening

---

## Resources

- **Silver Tier**: `../silver-tier/README.md`
- **Hackathon Blueprint**: `../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Odoo API Docs**: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **Meta Graph API**: https://developers.facebook.com/docs/graph-api
- **Twitter API v2**: https://developer.twitter.com/en/docs/twitter-api
- **MCP Servers**: https://github.com/anthropics/mcp-servers

---

*Gold Tier Skills Package v0.1 | AI Employee Hackathon 2026*
