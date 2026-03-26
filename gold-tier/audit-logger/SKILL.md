# 📝 Audit Logger Skill

**Type**: Utility / Cross-Cutting Concern  
**Purpose**: Comprehensive logging of all AI Employee actions  
**Status**: 🚧 Development  

---

## Overview

The Audit Logger provides comprehensive, tamper-evident logging of all actions taken by the AI Employee system. Every action, decision, and state change is recorded for:
- **Compliance**: Track all financial and communication actions
- **Debugging**: Understand what happened and why
- **Accountability**: Human oversight of AI decisions
- **Analytics**: Measure system performance and patterns

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AUDIT LOGGER                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  All Actions Flow Through Logger:                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Odoo    │  │ Facebook │  │ Twitter  │  │  Email   │   │
│  │  Actions │  │  Posts   │  │  Tweets  │  │  Sent    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
│                         │                                  │
│                  ┌──────▼──────┐                           │
│                  │ Audit Logger│                           │
│                  └──────┬──────┘                           │
│                         │                                  │
│                  ┌──────▼──────┐                           │
│                  │  Log Files  │                           │
│                  │  (JSON)     │                           │
│                  └─────────────┘                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Log Entry Format

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
  "odoo_invoice_id": "INV/2026/0001",
  "log_id": "uuid-here"
}
```

---

## Installation

```bash
# Install dependencies
pip install python-dotenv

# Configure log path
export AUDIT_LOG_PATH="../AI_Employee_Vault/Logs/audit_log.json"
```

---

## Usage

### Log an Action

```python
from audit_logger import AuditLogger

logger = AuditLogger(vault_path='../AI_Employee_Vault')

logger.log_action(
    action_type='facebook_post',
    actor='qwen_code',
    target='Facebook Page',
    parameters={'message': 'Hello!'},
    result='success',
    approval_status='approved',
)
```

### Query Logs

```bash
# Get today's logs
python scripts/audit_logger.py --vault ../AI_Employee_Vault --query --today

# Get logs by action type
python scripts/audit_logger.py --vault ../AI_Employee_Vault --query --type odoo_invoice_create

# Get logs by actor
python scripts/audit_logger.py --vault ../AI_Employee_Vault --query --actor qwen_code
```

### Export Logs

```bash
# Export to CSV
python scripts/audit_logger.py --vault ../AI_Employee_Vault --export csv --output report.csv

# Export to JSON
python scripts/audit_logger.py --vault ../AI_Employee_Vault --export json --output report.json
```

---

## Log Retention

| Log Age | Action |
|---------|--------|
| 0-30 days | Active in main log |
| 30-90 days | Archived to monthly files |
| 90+ days | Compressed and archived |
| 365+ days | Deleted (configurable) |

---

## Security

- Logs are append-only (no modifications)
- Each entry has a unique ID
- Timestamps are immutable
- Regular integrity checks
- Backup logs to secure location

---

## File Structure

```
audit-logger/
├── SKILL.md
└── scripts/
    └── audit_logger.py    # Main logger module
```

---

## Integration

All Gold Tier skills automatically log actions:
- Odoo MCP
- Facebook/Instagram Poster
- Twitter Poster
- LinkedIn Poster
- Email MCP
- Approval Workflow

---

*Audit Logger v0.1 | AI Employee Hackathon 2026*
