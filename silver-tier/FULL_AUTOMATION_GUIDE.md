# 🚀 Silver Tier - Fully Automated Setup

## Complete Automation Guide

This guide shows you how to set up **fully automated** LinkedIn posting with the AI Employee Silver Tier.

---

## Quick Start (3 Steps)

### Step 1: Login to LinkedIn (One Time Only)

```bash
# Open LinkedIn and login
start https://www.linkedin.com/feed
```

**Important:** Stay logged in for 30 seconds so the session is saved.

### Step 2: Run Auto-Post

```bash
# One command to do everything
silver-tier\auto-post.bat
```

Enter your post content when prompted.

**That's it!** The script will:
1. ✅ Create the post
2. ✅ Auto-approve it (skip Pending_Approval)
3. ✅ Start LinkedIn Watcher
4. ✅ Post to LinkedIn automatically
5. ✅ Move to Done/ when complete

---

## What Gets Automated

```
┌─────────────────────────────────────────────────────────────┐
│              Full Automation Flow                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. You enter post content                                   │
│     ↓                                                        │
│  2. Post created in Approved/ (NOT Pending_Approval)         │
│     ↓                                                        │
│  3. LinkedIn Watcher detects (within 30 seconds)             │
│     ↓                                                        │
│  4. Auto-posts to LinkedIn                                   │
│     ↓                                                        │
│  5. Screenshot saved to Logs/                                │
│     ↓                                                        │
│  6. Moved to Done/LinkedIn/                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Commands Reference

### Fully Automated Posting

```bash
# Batch file (easiest)
silver-tier\auto-post.bat

# Python script
python AI_Employee_Vault\Scripts\auto_run.py ^
  --vault AI_Employee_Vault ^
  --content "Your post content here"
```

### Start All Watchers

```bash
# Start all 4 watchers (Filesystem, Gmail, LinkedIn, Orchestrator)
silver-tier\start-watchers.bat
```

### Manual LinkedIn Poster

```bash
# Create post (auto-approved)
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py ^
  --vault AI_Employee_Vault ^
  --content "Your content"

# Start watcher (monitors Approved/ folder)
python AI_Employee_Vault\Scripts\linkedin_watcher.py ^
  --vault AI_Employee_Vault ^
  --interval 30
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Approved/                  ← Posts go here (auto-approved)
│   └── LINKEDIN_POST_*.md
├── Done/
│   └── LinkedIn/              ← Completed posts
│       └── LINKEDIN_POST_*.md
├── Logs/                      ← Screenshots & logs
│   └── linkedin_*.png
└── Scripts/
    ├── auto_run.py            ← Master automation script
    └── linkedin_watcher.py    ← Watches Approved/ folder
```

---

## Configuration

### Change Posting Interval

Edit `auto_run.py`:
```python
# Line ~100
'LinkedIn': ['linkedin_watcher.py', '--interval', '30'],  # Change 30 to desired seconds
```

### Require Manual Approval

If you want to review posts before posting:

```bash
# Create post with approval required
python .qwen/skills/linkedin-poster/scripts/linkedin_poster.py ^
  --vault AI_Employee_Vault ^
  --content "Your content" ^
  --approve  # This flag requires approval
```

Then manually move from `Pending_Approval/` to `Approved/`.

---

## Troubleshooting

### Issue: "LinkedIn requires login"

**Solution:**
```bash
# 1. Open LinkedIn and login
start https://www.linkedin.com/feed

# 2. Stay logged in for 30 seconds

# 3. Close browser

# 4. Run automation again
silver-tier\auto-post.bat
```

### Issue: "Browser won't start"

**Solution:**
```bash
# Reinstall Playwright browsers
playwright install chromium

# Test
python AI_Employee_Vault\Scripts\linkedin_watcher.py --vault AI_Employee_Vault
```

### Issue: "Post not appearing on LinkedIn"

**Check logs:**
```bash
# View latest logs
type AI_Employee_Vault\Logs\*.log | more

# View screenshots
dir AI_Employee_Vault\Logs\linkedin_*.png
```

---

## Example Usage

### Post Business Update

```bash
silver-tier\auto-post.bat

# When prompted:
Enter your LinkedIn post content: Excited to announce our AI Employee Silver Tier! 

Features:
- Gmail integration
- Auto LinkedIn posting  
- Approval workflows
- Multi-step plans

#AI #Automation #Innovation
```

### Post from File

```bash
# Create post content file
echo "Your post content here" > post_content.txt

# Run automation
python AI_Employee_Vault\Scripts\auto_run.py ^
  --vault AI_Employee_Vault ^
  --content "Content from file" ^
  --category business_update
```

---

## Monitoring

### Check Posted Content

```bash
# View completed posts
dir AI_Employee_Vault\Done\LinkedIn\

# Open latest post
type AI_Employee_Vault\Done\LinkedIn\LINKEDIN_POST_*.md
```

### View Activity Logs

```bash
# Latest activity
type AI_Employee_Vault\Logs\*.log | Select-Object -Last 50

# LinkedIn specific
type AI_Employee_Vault\Logs\*.log | Select-String "LinkedIn"
```

### View Screenshots

```bash
# List screenshots
dir AI_Employee_Vault\Logs\linkedin_*.png

# Open latest
powershell -c "Invoke-Item (Get-ChildItem AI_Employee_Vault\Logs\linkedin_*.png | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName"
```

---

## Complete Workflow Example

```bash
# 1. Login to LinkedIn (first time only)
start https://www.linkedin.com/feed
# [Login and wait 30 seconds]

# 2. Run automation
silver-tier\auto-post.bat

# 3. Enter post content
Enter your LinkedIn post content: 🎉 Silver Tier Complete!

Our AI Employee now features:
✅ Gmail monitoring
✅ Auto LinkedIn posting
✅ Approval workflows
✅ Multi-step plans

#AI #Automation

# 4. Wait for completion (max 5 minutes)
# Script will:
# - Create post in Approved/
# - Start LinkedIn Watcher
# - Auto-post to LinkedIn
# - Save screenshot
# - Move to Done/LinkedIn/

# 5. Verify
dir AI_Employee_Vault\Done\LinkedIn\
```

---

## Advanced: Custom Automation

### Create Custom Script

```python
# my_automation.py
from pathlib import Path
import sys

sys.path.insert(0, 'AI_Employee_Vault/Scripts')
from auto_run import AIEmployeeAutoRunner

# Initialize
runner = AIEmployeeAutoRunner('AI_Employee_Vault')

# Post to LinkedIn
runner.create_linkedin_post(
    content="My custom post!",
    category='thought_leadership'
)

# Start all watchers
processes = runner.start_all_watchers()

# Keep running
import time
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    for proc in processes.values():
        proc.terminate()
```

### Run Custom Script

```bash
python my_automation.py
```

---

## Best Practices

### Content Guidelines

| Do | Don't |
|----|-------|
| Keep posts 100-300 words | Post walls of text |
| Use 3-5 hashtags | Use 20+ hashtags |
| Include call-to-action | Post without purpose |
| Review logs regularly | Ignore error messages |

### Posting Frequency

```
Recommended:
- 2-3 posts per week
- Not more than 1 post per day
- Avoid weekends for business content
```

### Session Management

```
- Login to LinkedIn once every 30 days
- Don't clear browser cookies/session
- Use same browser for manual LinkedIn access
```

---

## Security Notes

⚠️ **Important:**

1. **Session files are sensitive** - Never share `linkedin_session/` folder
2. **Don't commit to git** - Already in `.gitignore`
3. **Rate limiting** - Don't post more than 5 times per day
4. **LinkedIn ToS** - Use responsibly

---

## Support

### Logs Location
```
AI_Employee_Vault/Logs/
├── auto_run_YYYYMMDD.log
├── linkedin_watcher_*.log
└── linkedin_YYYYMMDD_HHMMSS.png (screenshots)
```

### Common Issues

| Issue | Log File | Solution |
|-------|----------|----------|
| Login failed | auto_run.log | Login manually first |
| Browser crash | linkedin_watcher.log | Reinstall Playwright |
| Post failed | auto_run.log | Check content length |

---

**Fully Automated LinkedIn Posting is ready!** 🚀

Run `silver-tier\auto-post.bat` to get started!
