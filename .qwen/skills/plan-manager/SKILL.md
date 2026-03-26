---
name: plan-manager
description: |
  Create and manage Plan.md files for multi-step tasks.
  Tracks progress with checkboxes and updates Dashboard.
  Enables Qwen Code to handle complex multi-step workflows.
---

# Plan Manager Skill

Create and manage plans for multi-step tasks.

## Overview

When Qwen Code encounters a complex task requiring multiple steps,
it creates a Plan.md file to track progress. This skill manages
the creation, updating, and completion of these plans.

## Plan File Format

```markdown
---
type: plan
task: Process monthly invoices
created: 2026-02-26T10:00:00
status: in_progress
priority: high
estimated_steps: 5
completed_steps: 2
---

# Plan: Process Monthly Invoices

## Objective

Process all invoices from January 2026 and update accounting records.

## Steps

- [x] Collect all invoice PDFs from Inbox
- [x] Extract invoice data (amount, vendor, date)
- [ ] Categorize each invoice
- [ ] Enter into accounting system
- [ ] File in Accounting/2026/01/
- [ ] Update Dashboard totals
- [ ] Generate summary report

## Notes

- Found 15 invoices for January
- 3 invoices need approval (> $500)
- Vendor XYZ invoice disputed

## Blockers

None

## Related Files

- Needs_Action/FILE_invoice_*.pdf
- Accounting/2026/01/
```

## Usage

### Create Plan

```bash
python .qwen/skills/plan-manager/scripts/create_plan.py \
  --vault ../AI_Employee_Vault \
  --task "Process monthly invoices" \
  --steps "Collect invoices,Extract data,Categorize,Enter records,File,Update dashboard"
```

### Update Plan

```bash
python .qwen/skills/plan-manager/scripts/update_plan.py \
  --vault ../AI_Employee_Vault \
  --plan Plans/plan_invoices_20260226.md \
  --complete-step 2 \
  --add-note "Found 15 invoices"
```

### Get Plan Status

```bash
python .qwen/skills/plan-manager/scripts/plan_status.py \
  --vault ../AI_Employee_Vault
```

## Integration with Qwen Code

When Qwen Code identifies a multi-step task:

```bash
qwen "Create a plan for processing the invoices in Needs_Action folder"
```

Qwen Code creates Plan.md with checkboxes.

After each step, Qwen Code updates the plan.

When all checkboxes complete, moves plan to Done/.

## Dashboard Integration

Plans shown on Dashboard.md:

```markdown
## Active Plans

| Plan | Progress | Status |
|------|----------|--------|
| Process Invoices | 2/7 | In Progress |
| Setup Email | 0/5 | Not Started |
```

## Plan Templates

### Email Processing Plan

```markdown
---
type: plan
task: Email inbox processing
---

# Plan: Process Email Inbox

## Steps

- [ ] Read all emails in Needs_Action
- [ ] Categorize by urgency
- [ ] Draft replies for urgent
- [ ] Archive processed
- [ ] Update contacts database
```

### Client Onboarding Plan

```markdown
---
type: plan
task: Client onboarding
---

# Plan: Onboard New Client

## Steps

- [ ] Send welcome email
- [ ] Schedule kickoff meeting
- [ ] Create project folder
- [ ] Set up invoicing
- [ ] Add to CRM
- [ ] Assign team members
```

## Plan Lifecycle

```
1. Created in Plans/
2. Status: in_progress
3. Steps checked off as completed
4. Status: completed when all done
5. Moved to Done/Plans/
```

## Commands

| Command | Description |
|---------|-------------|
| `create_plan.py` | Create new plan |
| `update_plan.py` | Update plan progress |
| `plan_status.py` | Show all plans |
| `cleanup_plans.py` | Archive completed |

## Files

```
.qwen/skills/plan-manager/
├── SKILL.md
├── scripts/
│   ├── create_plan.py
│   ├── update_plan.py
│   ├── plan_status.py
│   └── cleanup_plans.py
└── references/
    └── plan-template.md
```

---

*Plan Manager Skill v0.2 (Silver Tier)*
