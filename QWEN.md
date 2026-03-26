# Personal AI Employee (Digital FTE)

## Project Overview

This repository contains a blueprint and implementation framework for building a **Personal AI Employee** (also called a **Digital FTE** - Full-Time Equivalent). It's a local-first, autonomous AI agent system that manages personal and business affairs 24/7 using:

- **Claude Code** as the reasoning engine
- **Obsidian** (Markdown) as the dashboard and long-term memory
- **Python Watcher scripts** for monitoring inputs (Gmail, WhatsApp, filesystems)
- **MCP (Model Context Protocol) servers** for external actions
- **Playwright** for browser automation

The architecture follows a **Perception → Reasoning → Action** pattern with human-in-the-loop approval for sensitive operations.

## Directory Structure

```
personal-AI-FTE/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint document
├── skills-lock.json          # Installed skill dependencies
├── .qwen/skills/             # Qwen agent skills
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Playwright MCP skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool schemas
│       └── scripts/
│           ├── mcp-client.py    # MCP client for tool calls
│           ├── start-server.sh  # Start Playwright MCP server
│           ├── stop-server.sh   # Stop Playwright MCP server
│           └── verify.py        # Server health check
└── .gitattributes
```

## Key Concepts

### Architecture Layers

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine, task execution |
| **Memory/GUI** | Obsidian Vault | Dashboard, knowledge base, task tracking |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser, payments) |

### Core Patterns

1. **Watcher Pattern**: Lightweight Python scripts continuously monitor inputs and create `.md` files in `/Needs_Action/` folder
2. **Ralph Wiggum Loop**: A Stop hook that keeps Claude iterating until tasks are complete
3. **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval/` → `/Approved/`)
4. **Business Handover**: Autonomous weekly audits generating "Monday Morning CEO Briefing"

### Folder Structure (Obsidian Vault)

```
Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items requiring processing
├── In_Progress/<agent>/ # Claimed tasks (prevents double-work)
├── Pending_Approval/   # Awaiting human approval
├── Approved/           # Approved actions ready for execution
├── Done/               # Completed tasks
├── Plans/              # Generated plans with checkboxes
├── Briefings/          # CEO briefings and reports
├── Accounting/         # Bank transactions, invoices
└── Business_Goals.md   # Objectives and metrics
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts, orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Hardware Requirements

- **Minimum**: 8GB RAM, 4-core CPU, 20GB free disk
- **Recommended**: 16GB RAM, 8-core CPU, SSD storage
- **For always-on**: Dedicated mini-PC or cloud VM

### Setup Commands

```bash
# 1. Create Obsidian vault
mkdir AI_Employee_Vault
cd AI_Employee_Vault
mkdir -p Inbox Needs_Action Done Plans Pending_Approval Approved Briefings Accounting

# 2. Verify Claude Code
claude --version

# 3. Start Playwright MCP server (for browser automation)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# 4. Verify server
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# 5. Stop server when done
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Server Configuration

Configure in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

### Running the Ralph Wiggum Loop

```bash
# Start autonomous task execution
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Development Conventions

### Coding Style

- **Python**: Use type hints, follow PEP 8
- **Markdown**: Use YAML frontmatter for metadata
- **Scripts**: Include docstrings and logging

### Testing Practices

- Each Watcher script should have error handling
- Use the `verify.py` script to check server health
- Test human-in-the-loop workflow before production use

### Security Rules

- **Never commit secrets**: `.env`, tokens, WhatsApp sessions, banking credentials stay local
- **Vault sync**: Only markdown/state files sync; secrets excluded via `.gitignore`
- **Cloud/Local split**: Cloud drafts only; Local executes sensitive actions

## Available Tools

### Playwright MCP Tools (22 tools)

Key tools for browser automation:

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to URL |
| `browser_snapshot` | Get accessibility snapshot (element refs) |
| `browser_click` | Click element |
| `browser_type` | Type text into field |
| `browser_fill_form` | Fill multiple fields |
| `browser_take_screenshot` | Capture screenshot |
| `browser_evaluate` | Execute JavaScript |
| `browser_run_code` | Run Playwright code snippet |
| `browser_wait_for` | Wait for text/time |

See `.qwen/skills/browsing-with-playwright/references/playwright-tools.md` for full schema.

### MCP Client Usage

```bash
# Navigate to URL
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Get page snapshot
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_snapshot -p '{}'

# Click element (use ref from snapshot)
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_click -p '{"element": "Submit button", "ref": "e42"}'
```

## Hackathon Tiers

| Tier | Description | Time |
|------|-------------|------|
| **Bronze** | Foundation (1 Watcher, basic vault) | 8-12 hrs |
| **Silver** | Functional (2+ Watchers, MCP, HITL) | 20-30 hrs |
| **Gold** | Autonomous (full integration, Odoo, Ralph loop) | 40+ hrs |
| **Platinum** | Production (Cloud + Local, 24/7, A2A) | 60+ hrs |

## Resources

- **Main Blueprint**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Skill**: `.qwen/skills/browsing-with-playwright/SKILL.md`
- **Ralph Wiggum Pattern**: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Agent Skills**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **MCP Servers**: https://github.com/AlanOgic/mcp-odoo-adv

## Weekly Research Meeting

- **When**: Wednesdays at 10:00 PM
- **Zoom**: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube**: https://www.youtube.com/@panaversity
