# LinkedIn Auto-Posting - User Guide

## ✅ Current Setup: Semi-Automated Mode (Option A)

This is the **recommended and working** configuration for LinkedIn posting.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│           Semi-Automated LinkedIn Posting                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Create Post → Save to Approved/ folder               │
│     ↓                                                    │
│  2. Watcher detects file (within 30 seconds)             │
│     ↓                                                    │
│  3. Watcher opens LinkedIn browser                       │
│     ↓                                                    │
│  4. Watcher clicks "Start a post"                        │
│     ↓                                                    │
│  5. Watcher fills in ALL content                         │
│     ↓                                                    │
│  6. 📢 YOU click the blue "Post" button                  │
│     ↓                                                    │
│  7. Watcher detects success & moves file to Done/        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Step 1: Create a Post File

Create a markdown file in `AI_Employee_Vault/Approved/` folder:

**Filename:** `LINKEDIN_[TOPIC]_[DATE].md`

**Example:**
```markdown
---
type: linkedin_post
category: tips
created: 2026-02-28
status: approved
---

## Content

Your post content goes here...

#Hashtag1 #Hashtag2 #Hashtag3

---
*Created by AI Employee*
```

### Step 2: Start the Watcher

Open terminal and run:
```bash
cd AI_Employee_Vault\Scripts
python linkedin_watcher.py --vault .. --interval 30
```

### Step 3: Watch Browser Open

A browser window will open automatically:
- Watcher logs into LinkedIn (session saved)
- Clicks "Start a post"
- Types all your content
- **Waits for you to click "Post"**

### Step 4: Click Post Button

When you see the post dialog with your content:
- Review the content
- Click the blue **"Post"** button
- Done! ✅

### Step 5: Verification

Watcher will:
- Take a screenshot
- Move file to `Done/LinkedIn/`
- Log success

---

## Example Posts

### Post 1: AI Automation Tips ✅
**File:** `Done/LinkedIn/LINKEDIN_AI_TIPS_20260228.md`
**Status:** Published to LinkedIn
**Result:** 4 impressions (and counting!)

### Post 2: Claude Code Power ✅
**File:** `Done/LinkedIn/LINKEDIN_CLAUDE_CODE_20260228.md`
**Status:** Published to LinkedIn

---

## Best Practices

### Content Length
- **Ideal:** 300-500 characters
- **Maximum:** 3000 characters (LinkedIn limit)
- **With hashtags:** Keep total under 3000

### Posting Frequency
- **Recommended:** 2-3 times per week
- **Maximum:** 5 posts per day
- **Best times:** Tuesday-Thursday, 9-11 AM

### Content Types
- ✅ Tips & Tutorials
- ✅ Project Updates
- ✅ Industry Insights
- ✅ Success Stories
- ✅ Thought Leadership

### Hashtags
- Use 3-10 relevant hashtags
- Mix popular and niche tags
- Examples: `#AI #Automation #Productivity`

---

## Troubleshooting

### Issue: Watcher doesn't detect post file

**Check:**
1. Filename starts with `LINKEDIN_`
2. File contains `type: linkedin_post`
3. File is in `Approved/` folder (not `Pending_Approval/`)

### Issue: Browser doesn't open

**Solution:**
```bash
# Kill existing processes
taskkill /F /IM python.exe
taskkill /F /IM chrome.exe

# Restart watcher
cd AI_Employee_Vault\Scripts
python linkedin_watcher.py --vault .. --interval 30
```

### Issue: Content not filling properly

**Solution:**
- Check for special characters (emojis work fine)
- Ensure content is after `## Content` section
- Remove any `## Instructions` section from content

### Issue: Post button click doesn't work

**This is normal!** LinkedIn requires manual confirmation for security.
- Just click the "Post" button yourself when the dialog appears
- Takes 2 seconds
- 100% reliable

---

## File Structure

```
AI_Employee_Vault/
├── Approved/
│   └── LINKEDIN_[TOPIC]_[DATE].md    ← Create posts here
├── Done/
│   └── LinkedIn/
│       └── [published posts].md       ← Completed posts
├── Logs/
│   └── linkedin_[timestamp].png       ← Screenshots
└── Scripts/
    └── linkedin_watcher.py            ← Main watcher script
```

---

## Commands Reference

### Start Watcher
```bash
cd AI_Employee_Vault\Scripts
python linkedin_watcher.py --vault .. --interval 30
```

### Start with Custom Interval
```bash
python linkedin_watcher.py --vault .. --interval 60
```

### Check Logs
```bash
type ..\Logs\watcher_*.log
```

### View Screenshots
```bash
explorer ..\Logs
```

---

## Success Metrics

| Post | Status | Impressions |
|------|--------|-------------|
| AI Automation Tips | ✅ Published | 4+ |
| Claude Code Power | ✅ Published | - |
| Test Claude | ✅ Published | - |

---

## Support

For issues or questions:
1. Check logs: `AI_Employee_Vault/Logs/watcher_*.log`
2. Check screenshots: `AI_Employee_Vault/Logs/linkedin_*.png`
3. Review this guide

---

*AI Employee System - Silver Tier*
*Last Updated: 2026-02-28*
