"""
LinkedIn Manual Authentication and Test Post

Run this script ONCE to:
1. Open browser with visible UI
2. Login to LinkedIn manually
3. Test posting
4. Save session for future automated runs

Usage:
    python linkedin_auth_test.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add Scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
vault_path = Path(__file__).parent.parent.resolve()
session_path = vault_path / 'Scripts' / 'linkedin_session'
logs_path = vault_path / 'Logs'

session_path.mkdir(parents=True, exist_ok=True)
logs_path.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("LINKEDIN AUTHENTICATION & TEST")
print("=" * 60)
print()
print(f"Session path: {session_path}")
print()
print("INSTRUCTIONS:")
print("1. A browser window will open")
print("2. Login to LinkedIn if prompted")
print("3. Wait until you see your feed")
print("4. The script will test posting")
print("5. Session will be saved for future runs")
print()
input("Press ENTER to continue...")
print()

try:
    with sync_playwright() as p:
        # Launch visible browser
        print("Launching browser (VISIBLE - you should see it)...")
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,  # VISIBLE browser
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--window-size=1280,800'
            ]
        )
        print("Browser launched!")
        
        page = browser.pages[0]
        
        # Navigate to LinkedIn
        print("Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/login', timeout=60000)
        print(f"Current URL: {page.url}")
        print()
        print("=" * 60)
        print("IMPORTANT: LOGIN TO LINKEDIN IN THE BROWSER WINDOW")
        print("=" * 60)
        print()
        print("Waiting for you to login... (up to 3 minutes)")
        print()
        
        # Wait for login - check every 5 seconds
        max_wait = 180  # 3 minutes
        logged_in = False
        
        for i in range(max_wait // 5):
            try:
                # Check if we're on feed page or have post text area
                if page.is_visible('[data-testid="update-post-text"]', timeout=3000):
                    print("✓ LinkedIn feed detected - you're logged in!")
                    logged_in = True
                    break
            except:
                pass
            
            # Show progress
            if (i + 1) % 12 == 0:  # Every minute
                print(f"  Still waiting... ({(i + 1) // 12} minute(s))")
            
            page.wait_for_timeout(5000)
        
        if not logged_in:
            print("✗ Login timeout - no feed detected")
            print("Please run the script again and login faster.")
            browser.close()
            sys.exit(1)
        
        # Wait a bit for page to stabilize
        page.wait_for_timeout(3000)
        
        # Take a screenshot to verify
        screenshot_path = logs_path / f'linkedin_authenticated_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}")
        print()
        
        # Test: Click the post text area
        print("Testing post creation...")
        text_area = page.query_selector('[data-testid="update-post-text"]')
        if text_area:
            print("✓ Post text area found")
            text_area.click()
            page.wait_for_timeout(1000)
            
            # Type test content
            test_content = f"Test post from AI Employee - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            print(f"Typing: {test_content}")
            text_area.type(test_content, delay=50)
            page.wait_for_timeout(2000)
            
            # Look for post button
            post_button = page.query_selector('button:has-text("Post")')
            if not post_button:
                post_button = page.query_selector('button:has-text("post")')
            if not post_button:
                post_button = page.query_selector('[aria-label="Post"]')
            
            if post_button:
                print("✓ Post button found")
                # DON'T actually post - just verify we can
                print()
                print("=" * 60)
                print("SUCCESS! LinkedIn authentication working!")
                print("=" * 60)
                print()
                print("The session is now saved. Future automated posts will work.")
                print()
                print("To close the browser:")
                print("  - Press ENTER to exit and close browser")
                print("  - Or keep it open for the watcher to auto-post")
                print()
                
                # Wait for user to decide
                input("Press ENTER to close browser and exit...")
                browser.close()
                print("Browser closed. Done!")
            else:
                print("✗ Post button not found")
                browser.close()
        else:
            print("✗ Post text area not found")
            browser.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
