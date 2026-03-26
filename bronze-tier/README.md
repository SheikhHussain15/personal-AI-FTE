# AI Employee - Bronze Tier Implementation

> **Tagline**: Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This is the **Bronze Tier** implementation of the Personal AI Employee system - the minimum viable deliverable for the hackathon.

## What is Bronze Tier?

Bronze Tier provides the foundation for your AI Employee:

- ✅ **Obsidian vault** with Dashboard.md and Company_Handbook.md
- ✅ **One working Watcher script** (File System monitoring)
- ✅ **Qwen Code integration** for reading/writing to the vault
- ✅ **Basic folder structure**: /Inbox, /Needs_Action, /Done
- ✅ **Agent Skill documentation** for vault operations

**Estimated setup time**: 8-12 hours

## Quick Start

### Windows

```batch
# Run setup script
bronze-tier\setup.bat

# Start the orchestrator
python AI_Employee_Vault\Scripts\orchestrator.py --vault ./AI_Employee_Vault

# Start the filesystem watcher (in separate terminal)
python AI_Employee_Vault\Scripts\filesystem_watcher.py --vault ./AI_Employee_Vault
```

### macOS/Linux

```bash
# Run setup (manual)
cd AI_Employee_Vault
pip install watchdog

# Start the orchestrator
python Scripts/orchestrator.py --vault ./AI_Employee_Vault

# Start the filesystem watcher (in separate terminal)
python Scripts/filesystem_watcher.py --vault ./AI_Employee_Vault --watch
```

## Directory Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Objectives and metrics
├── VAULT_SKILL.md           # Agent skill documentation
├── Inbox/                    # Drop zone for new files
├── Needs_Action/            # Items awaiting processing
├── Done/                     # Completed items
├── Plans/                    # Multi-step plans
├── Pending_Approval/        # Awaiting human decision
├── Approved/                 # Approved for action
├── Briefings/                # CEO briefings
├── Accounting/               # Financial records
├── Logs/                     # System logs
└── Scripts/                  # Python scripts
    ├── base_watcher.py      # Base class for watchers
    ├── filesystem_watcher.py # File system watcher
    └── orchestrator.py       # Main orchestrator
```

## How It Works

### 1. File Drop → Action

```
User drops file in Inbox/
        ↓
FilesystemWatcher detects it (every 30s)
        ↓
Creates copy in Needs_Action/ + metadata file
        ↓
Orchestrator updates Dashboard.md
        ↓
Claude Code processes the item
        ↓
Creates plan or takes action
        ↓
Moves to Done/ when complete
```

### 2. Qwen Code Processing

```bash
# Navigate to vault
cd AI_Employee_Vault

# Run Qwen Code with context
qwen "Process all items in Needs_Action folder. Follow Company_Handbook rules."
```

### 3. Dashboard Updates

The orchestrator automatically updates Dashboard.md with:
- Pending task counts
- Recent activity
- Completion statistics

## Usage Examples

### Example 1: Process a Document

1. Drop `invoice.pdf` in `AI_Employee_Vault/Inbox/`
2. Watcher creates `Needs_Action/FILE_invoice.pdf` + metadata
3. Run orchestrator:
   ```bash
   python Scripts/orchestrator.py --vault ./AI_Employee_Vault
   ```
4. Claude Code reads the file, categorizes it, extracts key info
5. File moved to `Done/` with notes

### Example 2: Generate Daily Briefing

```bash
# Qwen Code command
qwen "Generate a daily briefing based on completed tasks and pending items. Save to Briefings/$(date +%Y-%m-%d)_Briefing.md"
```

### Example 3: Check System Status

```bash
# Run orchestrator (updates dashboard)
python Scripts/orchestrator.py --vault ./AI_Employee_Vault

# View logs
tail -f AI_Employee_Vault/Logs/orchestrator_*.log
```

## Configuration

### Watcher Settings

```bash
# Filesystem watcher options
python Scripts/filesystem_watcher.py --help

# Options:
#   --vault, -v     Path to Obsidian vault (default: ../AI_Employee_Vault)
#   --interval, -i  Check interval in seconds (default: 30)
```

### Orchestrator Settings

```bash
# Orchestrator options
python Scripts/orchestrator.py --help

# Options:
#   --vault, -v     Path to Obsidian vault
#   --watch, -w     Run in watch mode (continuous)
#   --interval, -i  Watch interval in seconds (default: 60)
#   --dry-run, -n   Dry run (no external actions)
```

## Rules of Engagement

See `Company_Handbook.md` for complete rules. Key points:

### Always Do
- Log all actions
- Be polite and professional
- Follow filing conventions
- Update Dashboard after processing

### Never Do (Bronze Tier)
- Send emails without approval
- Process payments without approval
- Delete files without approval
- Share credentials or sensitive data

### Approval Thresholds

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Payments | < $50 recurring | All new payees, > $100 |
| Emails | Known contacts | New contacts, bulk |
| Files | Create, read | Delete, move outside vault |

## Testing

### Verify Installation

```bash
# Check Python
python --version  # Should be 3.13+

# Check dependencies
python -c "import watchdog; print('watchdog OK')"

# Test watcher (single cycle)
python Scripts/filesystem_watcher.py --vault ./AI_Employee_Vault

# Test orchestrator
python Scripts/orchestrator.py --vault ./AI_Employee_Vault
```

### Test File Processing

1. Create a test file:
   ```bash
   echo "Test content" > AI_Employee_Vault/Inbox/test.txt
   ```

2. Wait 30 seconds (or run watcher manually)

3. Check `Needs_Action/` for processed file

4. Check `Logs/` for activity log

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Watcher not detecting files | Ensure files dropped in `Inbox/` folder |
| Python errors | Check Python version (3.13+ required) |
| Dashboard not updating | Run orchestrator manually |
| Files not moving | Check file permissions |
| Qwen Code errors | Verify Qwen Code installation |

## Logging

All activity logged to `Logs/`:

- `orchestrator_YYYYMMDD.log` - Orchestrator activity
- `watcher_YYYYMMDD.log` - Watcher activity
- `action_YYYYMMDD.json` - Detailed action logs

## Next Steps (Silver Tier)

After mastering Bronze Tier, upgrade to Silver:

- [ ] Add Gmail Watcher
- [ ] Add WhatsApp Watcher
- [ ] Implement MCP server for email sending
- [ ] Create approval workflow
- [ ] Add scheduled tasks (cron)
- [ ] Auto-post to LinkedIn

## Resources

- **Main Blueprint**: `../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Vault Skill**: `AI_Employee_Vault/VAULT_SKILL.md`
- **Company Handbook**: `AI_Employee_Vault/Company_Handbook.md`
- **Qwen Code Docs**: https://code.qwen.ai/

## Support

- Weekly Research Meeting: Wednesdays at 10:00 PM
- Zoom: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- YouTube: https://www.youtube.com/@panaversity

---

*AI Employee Bronze Tier v0.1 | Built for the Personal AI Employee Hackathon 2026*
