# 📊 CEO Briefing Generator Skill

**Type**: Utility / Report Generator  
**Purpose**: Generate weekly business audit reports and CEO briefings  
**Status**: 🚧 Development  

---

## Overview

This skill automatically generates comprehensive business briefings by analyzing:
- **Financial Data**: Revenue, expenses, profit from Odoo ERP
- **Task Completion**: Completed tasks from Done/ folder
- **Social Media Performance**: Posts, engagement from Facebook, Twitter, LinkedIn
- **Communication**: Emails, WhatsApp, messages processed
- **Bottlenecks**: Delayed tasks, pending approvals
- **Proactive Suggestions**: Cost optimization, action items

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CEO BRIEFING GENERATOR                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Odoo       │  │   Vault      │  │   Social     │      │
│  │   (Finance)  │  │   (Tasks)    │  │   Media      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │  Briefing       │                        │
│                  │  Generator      │                        │
│                  └────────┬────────┘                        │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │  CEO Briefing   │                        │
│                  │  (Markdown)     │                        │
│                  └─────────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
# Install dependencies
pip install python-dotenv pyyaml

# Ensure Odoo MCP is configured
python ../odoo-mcp/scripts/odoo_config.py --url http://localhost:8069 --db odoo --username admin --password admin
```

---

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `generate_briefing` | Generate weekly CEO briefing | period, vault_path |
| `analyze_revenue` | Analyze revenue trends | period, compare_previous |
| `identify_bottlenecks` | Find delayed tasks | threshold_days |
| `get_social_summary` | Summarize social media performance | period, platforms |

---

## Usage Examples

### Generate Weekly Briefing

```bash
python scripts/generate_briefing.py \
  --vault ../AI_Employee_Vault \
  --period last_week
```

### Generate Monthly Briefing

```bash
python scripts/generate_briefing.py \
  --vault ../AI_Employee_Vault \
  --period last_month
```

### Schedule Weekly (Monday 7 AM)

**Windows Task Scheduler:**
```batch
schtasks /create /tn "CEO_Briefing" /tr "python gold-tier/ceo-briefing/scripts/generate_briefing.py --vault AI_Employee_Vault" /sc weekly /d MON /st 07:00
```

**Linux cron:**
```bash
# Edit crontab
crontab -e

# Add line for Monday 7 AM
0 7 * * 1 cd /path/to/personal-AI-FTE && python gold-tier/ceo-briefing/scripts/generate_briefing.py --vault AI_Employee_Vault
```

---

## Briefing Sections

The generated briefing includes:

1. **Executive Summary**: High-level overview
2. **Revenue**: Income, trends, projections
3. **Expenses**: Costs, subscriptions, alerts
4. **Completed Tasks**: What was accomplished
5. **Bottlenecks**: Delays and blockers
6. **Social Media**: Posts, engagement
7. **Communication**: Messages processed
8. **Proactive Suggestions**: AI recommendations
9. **Upcoming Deadlines**: What's due soon
10. **Action Items**: What needs attention

---

## Output Location

Briefings are saved to:
```
AI_Employee_Vault/Briefings/YYYY-MM-DD_CEO_Briefing.md
```

---

## Configuration

```json
{
  "briefing_day": "monday",
  "briefing_time": "07:00",
  "revenue_target_monthly": 10000,
  "expense_alert_threshold": 600,
  "bottleneck_delay_days": 3,
  "include_social_media": true,
  "include_odoo_data": true
}
```

---

## File Structure

```
ceo-briefing/
├── SKILL.md
└── scripts/
    ├── generate_briefing.py    # Main briefing generator
    ├── analyze_revenue.py      # Revenue analysis
    ├── identify_bottlenecks.py # Bottleneck detection
    └── social_summary.py       # Social media summary
```

---

## Sample Output

See `AI_Employee_Vault/Briefings/` for examples.

---

## References

- [Business Goals Template](../../AI_Employee_Vault/Business_Goals.md)
- [Odoo MCP](../odoo-mcp/SKILL.md)

---

*CEO Briefing Generator v0.1 | AI Employee Hackathon 2026*
