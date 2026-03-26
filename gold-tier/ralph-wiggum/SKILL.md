# 🔄 Ralph Wiggum Persistence Loop Skill

**Type**: Loop Controller / Orchestrator  
**Purpose**: Keep AI agent iterating until tasks are complete  
**Status**: 🚧 Development  

---

## Overview

The Ralph Wiggum pattern is a **Stop hook** that intercepts the AI agent's exit and re-injects the prompt if the task is not complete. This enables autonomous multi-step task execution without human intervention.

Named after the Simpsons character who persistently says "I'm gonna keep doing this until I get it right," this pattern ensures the AI keeps working until the job is done.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RALPH WIGGUM LOOP                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Orchestrator creates state file with prompt             │
│                                                              │
│  2. AI Agent (Qwen Code) works on task                      │
│                                                              │
│  3. AI tries to exit                                        │
│                                                              │
│  4. Stop Hook checks: Is task complete?                     │
│     - YES → Allow exit                                      │
│     - NO → Block exit, re-inject prompt                     │
│                                                              │
│  5. Repeat until complete or max iterations                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Completion Strategies

### 1. File Movement Detection (Recommended)

Task is complete when file moves from `/Needs_Action/` to `/Done/`:

```bash
# Start Ralph loop
python scripts/ralph_loop.py \
  --vault ../AI_Employee_Vault \
  --task "Process all files in Needs_Action" \
  --completion-file-movement
```

### 2. Promise-Based Detection

Task is complete when AI outputs specific promise tag:

```bash
python scripts/ralph_loop.py \
  --vault ../AI_Employee_Vault \
  --task "Generate weekly report" \
  --completion-promise "TASK_COMPLETE"
```

---

## Usage Examples

### Process Needs_Action Folder

```bash
python scripts/ralph_loop.py \
  --vault ../AI_Employee_Vault \
  --task "Process all files in Needs_Action, move to Done when complete" \
  --max-iterations 10
```

### Generate CEO Briefing

```bash
python scripts/ralph_loop.py \
  --vault ../AI_Employee_Vault \
  --task "Generate weekly CEO briefing with revenue analysis and bottleneck report" \
  --completion-promise "BRIEFING_COMPLETE" \
  --max-iterations 5
```

### Multi-Step Business Audit

```bash
python scripts/ralph_loop.py \
  --vault ../AI_Employee_Vault \
  --task "Audit business: 1) Check Odoo invoices 2) Review social media 3) Identify bottlenecks 4) Generate recommendations" \
  --max-iterations 15 \
  --output-log audit_log.md
```

---

## Configuration

```json
{
  "max_iterations": 10,
  "completion_promise": "TASK_COMPLETE",
  "file_movement": {
    "source_folder": "Needs_Action",
    "target_folder": "Done"
  },
  "timeout_minutes": 60,
  "retry_on_error": true,
  "log_all_iterations": true
}
```

---

## State File Format

```markdown
---
type: ralph_state
task: Process all files in Needs_Action
created: 2026-03-08T10:00:00Z
iteration: 1
max_iterations: 10
status: in_progress
---

# Ralph Wiggum Loop State

## Task
Process all files in Needs_Action, move to Done when complete

## Current Iteration
1 / 10

## Previous Output
[AI's previous response]

## Next Action
Continue processing remaining files...
```

---

## File Structure

```
ralph-wiggum/
├── SKILL.md
└── scripts/
    └── ralph_loop.py    # Main loop controller
```

---

## Integration with Qwen Code

The Ralph Wiggum loop works with Qwen Code's plugin system:

```bash
# In Qwen Code settings
/plugins/ralph-wiggum/enable

# Or via command line
qwen --plugin ralph-wiggum --task "..."
```

---

## Best Practices

1. **Set reasonable max_iterations**: Prevent infinite loops
2. **Use file movement detection**: More reliable than promise parsing
3. **Log all iterations**: For debugging and audit
4. **Set timeout**: Prevent runaway processes
5. **Monitor resource usage**: CPU, memory, API calls

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Loop never completes | Check completion criteria, increase max_iterations |
| Loop exits too early | Verify file movement or promise output |
| High API usage | Reduce max_iterations, add delays |
| State file corrupted | Delete state file, restart loop |

---

## References

- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Claude Code Plugins](https://claude.com/docs/plugins)

---

*Ralph Wiggum Persistence Loop v0.1 | AI Employee Hackathon 2026*
