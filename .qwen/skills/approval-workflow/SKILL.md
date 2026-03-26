---
name: approval-workflow
description: |
  Human-in-the-loop approval workflow for sensitive actions.
  Manages files in Pending_Approval/Approved/Rejected folders.
  Ensures AI cannot take sensitive actions without human approval.
---

# Approval Workflow Skill

Human-in-the-loop approval system for sensitive AI actions.

## Overview

For sensitive actions (payments, sending emails, posting to social media),
the AI Employee creates an approval request file instead of acting directly.
A human must review and approve before the action is executed.

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/    # Awaiting human review
├── Approved/            # Approved - execute action
└── Rejected/            # Rejected - do not execute
```

## Approval Request Format

```markdown
---
type: approval_request
action: email_send
amount: 500.00
recipient: client@example.com
created: 2026-02-26T10:30:00
expires: 2026-02-27T10:30:00
status: pending
---

# Approval Required: Send Email

## Details

- **Action:** Send email
- **To:** client@example.com
- **Subject:** Invoice #1234
- **Amount:** $500.00

## Content

Dear Client,

Please find attached invoice #1234 for $500...

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder.

## Expires

2026-02-27 10:30 (24 hours)

---
*Created by AI Employee v0.2*
```

## Approval Thresholds

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Email send | Known contacts | New contacts, bulk |
| Payments | < $50 recurring | All new payees, > $100 |
| Social posts | Scheduled posts | Replies, ads |
| File operations | Create, read | Delete, move outside |

## Usage

### Create Approval Request

```python
from approval_workflow import create_approval_request

create_approval_request(
    vault_path='../AI_Employee_Vault',
    action_type='email_send',
    details={
        'to': 'client@example.com',
        'subject': 'Invoice #1234',
        'body': 'Please pay $500...'
    },
    amount=500.00,
    expires_in_hours=24
)
```

### Check for Approvals

```bash
# Watch for approved files
python .qwen/skills/approval-workflow/scripts/approval_watcher.py --vault ../AI_Employee_Vault
```

### Process Approved Actions

```bash
# Execute approved actions
python .qwen/skills/approval-workflow/scripts/approval_executor.py --vault ../AI_Employee_Vault
```

## Integration with Qwen Code

When AI needs approval:

```bash
qwen "Create approval request for sending invoice email to client@example.com for $500"
```

AI creates file in `Pending_Approval/`.

Human reviews and moves to `Approved/`.

Approval executor sends the email.

## Workflow

```
1. AI detects action requiring approval
2. Creates approval request in Pending_Approval/
3. Human reviews (Dashboard shows pending count)
4. Human moves file to Approved/ or Rejected/
5. Approval executor processes Approved/ files
6. Result logged in Logs/
```

## Monitoring

### Dashboard Integration

Approval status shown on Dashboard.md:

```markdown
| Pending Approvals | Status |
|-------------------|--------|
| 3 | 🔴 Review needed |
```

### Expiration Handling

- Expired approvals moved to `Rejected/expired_`
- Human notified of expired items
- AI can re-create if still needed

## Security

- All approvals logged with timestamps
- Executor verifies file was moved by human (mtime check)
- Sensitive data never logged
- Rate limiting on execution

## Files

```
.qwen/skills/approval-workflow/
├── SKILL.md
├── scripts/
│   ├── approval_watcher.py
│   ├── approval_executor.py
│   └── create_approval.py
└── references/
    └── workflow-guide.md
```

---

*Approval Workflow Skill v0.2 (Silver Tier)*
