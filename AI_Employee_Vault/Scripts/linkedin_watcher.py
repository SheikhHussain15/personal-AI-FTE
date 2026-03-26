"""
LinkedIn Watcher

Automatically monitors Approved/ folder for LinkedIn posts and publishes them.
Runs continuously and posts content when human approves.

Silver Tier - Fully automated LinkedIn posting with Playwright.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import time
import sys

# Add AI_Employee_Vault/Scripts to path
current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class LinkedInWatcher(BaseWatcher):
    """
    Watches Approved/ folder for LinkedIn posts and publishes them automatically.
    
    Workflow:
    1. Monitors Approved/ folder every 60 seconds
    2. When post file appears, reads content
    3. Launches browser with saved LinkedIn session
    4. Posts content to LinkedIn
    5. Takes screenshot
    6. Moves file to Done/LinkedIn/
    """
    
    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        check_interval: int = 60,
        headless: bool = False  # Changed default to False for LinkedIn compatibility
    ):
        """
        Initialize LinkedIn Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session
            check_interval: Seconds between checks (default: 60)
            headless: Run browser without UI (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. "
                "Run: pip install playwright && playwright install chromium"
            )
        
        super().__init__(vault_path, check_interval)
        
        # Session path
        self.session_path = Path(session_path) if session_path else self.vault_path / 'Scripts' / 'linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Approved and Done folders
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done' / 'LinkedIn'
        self.logs_folder = self.vault_path / 'Logs'
        
        for folder in [self.approved_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Settings
        self.headless = headless

        # Track processed files
        self.processed_files: set = set()

        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Watching: {self.approved_folder}')
        self.logger.info(f'Check interval: {check_interval}s')
        self.logger.info('LinkedIn Watcher ready - will auto-post approved content')
    
    def check_for_updates(self) -> List[Path]:
        """
        Check Approved/ folder for new posts to publish.

        Returns:
            List of post files to process
        """
        posts = []

        try:
            if not self.approved_folder.exists():
                return posts

            # Find all LinkedIn post files (any file starting with LINKEDIN_)
            for f in self.approved_folder.glob('LINKEDIN_*.md'):
                # Skip if already processed
                if str(f) in self.processed_files:
                    continue

                # Verify it's a LinkedIn post
                content = f.read_text(encoding='utf-8')
                if 'type: linkedin_post' in content:
                    posts.append(f)
                    self.logger.info(f'Found approved post: {f.name}')

        except Exception as e:
            self.logger.error(f'Error checking Approved folder: {e}')

        return posts
    
    def create_action_file(self, item: Path) -> Optional[Path]:
        """
        Not used - we process directly instead of creating action files.
        This method is required by BaseWatcher but we override the workflow.
        """
        return None
    
    def process_post(self, filepath: Path) -> bool:
        """
        Process and publish a LinkedIn post.
        
        Args:
            filepath: Path to post file
            
        Returns:
            True if successful
        """
        try:
            # Read post content
            content = filepath.read_text(encoding='utf-8')
            
            # Extract post body (after frontmatter)
            parts = content.split('---\n\n', 1)
            if len(parts) < 2:
                self.logger.error(f'Invalid post format: {filepath.name}')
                return False
            
            body = parts[1]
            
            # Remove markdown headers
            lines = body.split('\n')
            clean_lines = []
            for line in lines:
                if line.startswith('##') or line.startswith('**'):
                    continue
                if line.startswith('# ') and 'LinkedIn' in line:
                    continue
                clean_lines.append(line)
            
            post_content = '\n'.join(clean_lines).strip()
            
            # Remove instructions section
            if '## Instructions' in post_content:
                post_content = post_content.split('## Instructions')[0].strip()
            
            if not post_content:
                self.logger.error(f'No content found in: {filepath.name}')
                return False
            
            self.logger.info(f'Posting content from: {filepath.name}')
            self.logger.info(f'Content length: {len(post_content)} characters')
            
            # Post to LinkedIn
            success = self._post_to_linkedin(post_content, filepath.name)
            
            if success:
                # Move to Done folder
                dest = self.done_folder / filepath.name
                filepath.rename(dest)
                self.logger.info(f'Post published and moved to: {dest}')
                
                # Mark as processed
                self.processed_files.add(str(filepath))
                
                return True
            else:
                self.logger.error(f'Failed to post: {filepath.name}')
                return False
                
        except Exception as e:
            self.logger.error(f'Error processing post: {e}')
            return False
    
    def _post_to_linkedin(self, content: str, filename: str) -> bool:
        """
        Post content to LinkedIn using Playwright.

        Args:
            content: Post content
            filename: For logging

        Returns:
            True if successful
        """
        try:
            self.logger.info('Launching browser...')
            with sync_playwright() as p:
                # Launch browser with persistent session
                # Use headless=False for first run to allow login
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                self.logger.info('Browser launched')

                page = browser.pages[0]

                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com/feed', timeout=60000)
                self.logger.info(f'Current URL: {page.url}')

                # Wait for page to load - give more time for LinkedIn
                self.logger.info('Waiting for LinkedIn feed to load (up to 60 seconds)...')
                
                # Define selectors upfront
                post_selectors = [
                    '[data-testid="update-post-text"]',
                    '[data-testid="update-post-input"]',
                    'div[contenteditable="true"][role="textbox"]',
                    '.ql-editor[contenteditable="true"]',
                    'button:has-text("Start a post")',
                    'div.share-box-feed-entry__trigger'
                ]
                
                try:
                    # First wait for navigation to complete
                    page.wait_for_load_state('networkidle', timeout=30000)
                    self.logger.info('Page loaded, waiting for feed element...')
                    
                    # Wait for the post text area - try multiple selectors
                    found_selector = None
                    for selector in post_selectors:
                        try:
                            page.wait_for_selector(selector, timeout=5000)
                            found_selector = selector
                            self.logger.info(f'Found post element with: {selector}')
                            break
                        except PlaywrightTimeout:
                            continue
                    
                    if not found_selector:
                        raise PlaywrightTimeout('No post selector matched')
                        
                    self.logger.info('LinkedIn feed loaded successfully')
                except PlaywrightTimeout:
                    self.logger.error('LinkedIn feed not loaded - login may be required')
                    self.logger.error(f'Current URL: {page.url}')
                    if 'login' in page.url.lower():
                        self.logger.error('*** YOU NEED TO LOGIN TO LINKEDIN ***')
                        self.logger.error('Keep this window open and login manually.')
                        self.logger.error('After login, the watcher will detect it on next cycle.')
                        # Wait for user to login (up to 2 minutes)
                        try:
                            self.logger.info('Waiting for login (120 seconds)...')
                            page.wait_for_selector('[data-testid="update-post-text"]', timeout=120000)
                            self.logger.info('Login successful!')
                        except PlaywrightTimeout:
                            self.logger.error('Login timeout - please restart watcher and try again')
                            browser.close()
                            return False
                    else:
                        # Not on login page but feed not found - page might still be loading
                        self.logger.info('Feed not found yet, waiting additional 30 seconds...')
                        try:
                            # Try alternative selectors again
                            for selector in post_selectors:
                                try:
                                    page.wait_for_selector(selector, timeout=5000)
                                    self.logger.info(f'Found post element with: {selector}')
                                    break
                                except PlaywrightTimeout:
                                    continue
                            self.logger.info('LinkedIn feed loaded!')
                        except PlaywrightTimeout:
                            self.logger.error('Feed element still not found after waiting')
                            # Take debug screenshot
                            debug_path = self.logs_folder / f'linkedin_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                            page.screenshot(path=str(debug_path))
                            self.logger.info(f'Debug screenshot: {debug_path}')
                            browser.close()
                            return False

                # Wait for page to stabilize
                page.wait_for_timeout(3000)

                # Close any popups/carousels first (like "Prepare for your job search")
                self.logger.info('Checking for popups/carousels...')
                try:
                    close_buttons = [
                        'button[aria-label="Close"]',
                        'button[aria-label="Dismiss"]',
                        '.msg-overlay-list__header button',
                        'button[data-control-name="overlay_close"]'
                    ]
                    for close_selector in close_buttons:
                        try:
                            close_btn = page.wait_for_selector(close_selector, timeout=3000)
                            if close_btn:
                                close_btn.click()
                                self.logger.info(f'Closed popup with: {close_selector}')
                                page.wait_for_timeout(1000)
                        except:
                            pass  # No popup with this selector
                except Exception as e:
                    self.logger.debug(f'No popups to close: {e}')

                # LinkedIn has a "Start a post" button that opens a dialog
                # First click the button, then type in the dialog
                self.logger.info('Looking for "Start a post" button...')
                
                # Try multiple approaches to find the "Start a post" button
                start_post_button = None
                
                # Method 1: Use locator (most robust)
                try:
                    locator = page.locator('text=Start a post').first
                    if locator.count() > 0:
                        start_post_button = locator
                        self.logger.info('Found "Start a post" via locator')
                except Exception as e:
                    self.logger.debug(f'Locator failed: {e}')
                
                # Method 2: Direct query selector
                if not start_post_button:
                    start_post_button = page.query_selector('button:has-text("Start a post")')
                    if start_post_button:
                        self.logger.info('Found "Start a post" via query_selector')
                
                # Method 3: Look for div with that text
                if not start_post_button:
                    start_post_button = page.query_selector('div:has-text("Start a post")')
                    if start_post_button:
                        self.logger.info('Found "Start a post" div')
                
                if start_post_button:
                    self.logger.info('Clicking "Start a post" button...')
                    
                    # Try multiple click methods
                    try:
                        # First try normal click
                        if hasattr(start_post_button, 'click'):
                            start_post_button.click(force=True)
                        else:
                            # It's a locator
                            start_post_button.click(force=True)
                        
                        self.logger.info('Click sent, waiting for dialog...')
                        page.wait_for_timeout(5000)
                        
                        # Check if dialog opened by looking for overlay/backdrop
                        dialog_indicators = [
                            'div.share-box-feed-entry__dialog',
                            'div.share-box-feed-entry__modal',
                            '[role="dialog"]',
                            'div.MuiModal-root',
                            'div[aria-label*="Create a post"]'
                        ]
                        
                        dialog_open = False
                        for indicator in dialog_indicators:
                            if page.is_visible(indicator):
                                dialog_open = True
                                self.logger.info(f'Dialog detected: {indicator}')
                                break
                        
                        if not dialog_open:
                            self.logger.info('Dialog not detected, trying alternative click...')
                            # Try clicking again with different approach
                            page.evaluate('''() => {
                                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Start a post'));
                                if (btn) btn.click();
                            }''')
                            page.wait_for_timeout(5000)
                        
                    except Exception as e:
                        self.logger.error(f'Click failed: {e}')
                        # Try JavaScript click
                        page.evaluate('''() => {
                            const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Start a post'));
                            if (btn) btn.click();
                        }''')
                        page.wait_for_timeout(5000)
                    
                    # Now look for the text area in the dialog
                    self.logger.info('Looking for text area in dialog...')
                    
                    # The dialog has a contenteditable div - wait for it
                    text_area = None
                    text_selectors = [
                        'div[contenteditable="true"]',
                        'div[role="textbox"]',
                        'div.ql-editor',
                        '[data-testid="update-post-text"]',
                        'div.share-box-feed-entry__textbox'
                    ]
                    
                    for selector in text_selectors:
                        try:
                            text_area = page.wait_for_selector(selector, timeout=3000)
                            if text_area:
                                self.logger.info(f'Found text area with: {selector}')
                                break
                        except PlaywrightTimeout:
                            continue
                    
                    if not text_area:
                        self.logger.error('Post text area not found in dialog')
                        # Take screenshot to see what's in the dialog
                        debug_path = self.logs_folder / f'linkedin_debug_dialog_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                        page.screenshot(path=str(debug_path))
                        self.logger.info(f'Debug screenshot: {debug_path}')
                        browser.close()
                        return False
                else:
                    self.logger.warn('"Start a post" button not found - page may have changed')
                    # Take screenshot to see current state
                    debug_path = self.logs_folder / f'linkedin_debug_nobutton_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                    page.screenshot(path=str(debug_path))
                    self.logger.info(f'Debug screenshot: {debug_path}')
                    browser.close()
                    return False

                self.logger.info('Focusing post text area...')
                text_area.click()
                page.wait_for_timeout(2000)

                # Truncate if needed (LinkedIn 3000 char limit)
                if len(content) > 3000:
                    content = content[:2997] + '...'
                    self.logger.warning('Content truncated to 3000 characters')

                # Type content slowly to avoid detection
                self.logger.info('Typing post content...')
                try:
                    # Try using fill first (faster, handles special chars better)
                    text_area.fill(content)
                    self.logger.info('Content entered via fill')
                except Exception as e:
                    self.logger.info(f'Fill failed: {e}, trying type...')
                    # Fallback to type
                    text_area.type(content, delay=50)
                    self.logger.info('Content entered via type')

                # Wait for post button to become enabled
                page.wait_for_timeout(3000)

                # Find and click post button
                self.logger.info('Looking for Post button...')
                
                post_button = None
                post_selectors = [
                    'button:has-text("Post")',
                    'button:has-text("post")',
                    '[aria-label="Post"]',
                    'div.share-box-feed-entry__submit button'
                ]
                
                for selector in post_selectors:
                    post_button = page.query_selector(selector)
                    if post_button:
                        self.logger.info(f'Found Post button with: {selector}')
                        break
                
                if post_button:
                    self.logger.info('Clicking Post button...')
                    try:
                        # Try normal click first
                        post_button.click(timeout=10000)
                    except Exception as e:
                        self.logger.info(f'Normal click failed: {e}')
                        self.logger.info('Trying force click...')
                        try:
                            post_button.click(force=True, timeout=10000)
                        except Exception as e2:
                            self.logger.info(f'Force click failed: {e2}')
                            self.logger.info('Using JavaScript click...')
                            # Fallback to JavaScript click
                            page.evaluate('''() => {
                                const btn = Array.from(document.querySelectorAll('button')).find(b => 
                                    b.textContent.includes('Post') && b.offsetParent !== null
                                );
                                if (btn) btn.click();
                            }''')
                    
                    self.logger.info('Post button clicked, waiting for confirmation...')

                    # Wait for confirmation - dialog should close or show "Posted" message
                    page.wait_for_timeout(8000)
                    
                    # Take screenshot to verify post was submitted
                    screenshot_path = self.logs_folder / f'linkedin_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                    page.screenshot(path=str(screenshot_path))
                    self.logger.info(f'Screenshot saved: {screenshot_path}')
                    
                    # Check if dialog is still open (post may not have submitted)
                    dialog_check = page.query_selector('div[role="dialog"]')
                    if dialog_check:
                        self.logger.warning('Dialog still open - post may not have been submitted!')
                        self.logger.warning('LinkedIn may require manual confirmation for the final post.')
                        # Don't mark as success - keep the file for retry
                        browser.close()
                        return False

                    # Close browser
                    browser.close()
                    self.logger.info('Post published successfully!')
                    return True
                else:
                    self.logger.error('Post button not found')
                    # Take screenshot for debugging
                    debug_path = self.logs_folder / f'linkedin_debug_nopostbtn_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                    page.screenshot(path=str(debug_path))
                    self.logger.info(f'Debug screenshot: {debug_path}')
                    browser.close()
                    return False

        except Exception as e:
            import traceback
            self.logger.error(f'Error posting to LinkedIn: {e}')
            self.logger.error(f'Traceback: {traceback.format_exc()}')
            return False
    
    def run(self):
        """
        Override run method to process posts directly instead of creating action files.
        """
        self.logger.info(f'Starting LinkedIn Watcher')
        self.logger.info(f'Watching for approved posts every {self.check_interval} seconds')
        
        try:
            while True:
                try:
                    # Check for new posts
                    posts = self.check_for_updates()
                    
                    if posts:
                        self.logger.info(f'Found {len(posts)} post(s) to process')
                        
                        for post_file in posts:
                            try:
                                success = self.process_post(post_file)
                                if success:
                                    self.logger.info(f'[OK] Posted: {post_file.name}')
                                else:
                                    self.logger.error(f'[FAIL] Failed: {post_file.name}')
                            except Exception as e:
                                self.logger.error(f'[ERROR] Error processing {post_file.name}: {e}')
                    else:
                        self.logger.debug('No posts to process')
                    
                except Exception as e:
                    self.logger.error(f'Error in check cycle: {e}')
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('LinkedIn Watcher stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
        finally:
            self.logger.info('LinkedIn Watcher shutting down')


def main():
    """Run LinkedIn Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--session', '-s',
        type=str,
        default=None,
        help='Path to session directory'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=False,
        help='Run browser in headless mode (default: visible)'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    watcher = LinkedInWatcher(
        str(vault_path),
        session_path=args.session,
        check_interval=args.interval,
        headless=args.headless
    )
    watcher.run()


if __name__ == '__main__':
    main()
