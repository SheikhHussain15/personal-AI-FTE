"""
LinkedIn Session Checker

This script checks if the LinkedIn session is properly saved and working.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright

vault_path = Path(__file__).parent.parent.resolve()
session_path = vault_path / 'Scripts' / 'linkedin_session'
logs_path = vault_path / 'Logs'

session_path.mkdir(parents=True, exist_ok=True)
logs_path.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("LINKEDIN SESSION CHECKER")
print("=" * 60)
print()
print(f"Session path: {session_path}")
print()

try:
    with sync_playwright() as p:
        print("Launching browser (VISIBLE)...")
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--window-size=1280,800'
            ]
        )
        print("Browser launched!")
        
        page = browser.pages[0]
        
        print("Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        print(f"Current URL: {page.url}")
        print()
        
        # Wait for page to load
        print("Waiting 10 seconds for page to fully load...")
        page.wait_for_timeout(10000)
        
        # Take screenshot
        screenshot_path = logs_path / f'linkedin_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}")
        print()
        
        # Check page content
        print("Checking page elements...")
        
        # Check for login page
        if 'login' in page.url.lower():
            print("✗ You are on the LOGIN page")
            print()
            print("ACTION NEEDED:")
            print("1. Login to LinkedIn in the browser window")
            print("2. Make sure to check 'Keep me signed in'")
            print("3. Wait until you see your feed")
            print("4. Then close the browser manually")
        else:
            print(f"✓ Not on login page")
            
            # Check for feed
            if page.is_visible('[data-testid="update-post-text"]', timeout=5000):
                print("✓ Feed text area found - you are logged in!")
            else:
                print("? Feed text area not visible")
        
        print()
        print("=" * 60)
        print("KEEP THIS WINDOW OPEN")
        print("=" * 60)
        print()
        print("If you need to login, do it now in the browser window.")
        print("After logging in, the session will be saved.")
        print()
        input("Press ENTER to close browser and exit...")
        
        browser.close()
        print("Done!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
