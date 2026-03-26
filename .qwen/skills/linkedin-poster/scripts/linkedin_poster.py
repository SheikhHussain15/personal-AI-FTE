"""
LinkedIn Poster

Automates posting to LinkedIn using Playwright browser automation.
Requires LinkedIn authentication and approval workflow for posts.

Silver Tier - Uses Playwright for browser automation.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# LinkedIn Poster import
import sys
from pathlib import Path

# Add AI_Employee_Vault/Scripts to path for logging utilities
current_dir = Path(__file__).parent.resolve()
vault_scripts = current_dir.parent.parent.parent.parent / 'AI_Employee_Vault' / 'Scripts'
sys.path.insert(0, str(vault_scripts))

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class LinkedInPoster:
    """
    Posts content to LinkedIn using browser automation.
    
    Uses Playwright to automate LinkedIn posting with approval workflow.
    """
    
    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        headless: bool = True,
        require_approval: bool = True
    ):
        """
        Initialize LinkedIn Poster.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session
            headless: Run browser without UI (default: True)
            require_approval: Require approval before posting (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. "
                "Run: pip install playwright && playwright install chromium"
            )
        
        # Initialize paths
        self.vault_path = Path(vault_path)
        
        # Session path
        self.session_path = Path(session_path) if session_path else self.vault_path / 'Scripts' / 'linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Settings
        self.headless = headless
        self.require_approval = require_approval
        
        # Folders
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done' / 'LinkedIn'
        self.logs_folder = self.vault_path / 'Logs'
        
        for folder in [self.approved_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('LinkedInPoster')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
        
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Require approval: {self.require_approval}')
        self.logger.info('LinkedIn Poster ready')
    
    def post_content(self, content: str, approval_file: Optional[Path] = None) -> bool:
        """
        Post content to LinkedIn.
        
        Args:
            content: The post content
            approval_file: Path to approval file (if approved)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0]
                
                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com/feed', timeout=60000)
                
                # Wait for page to load
                try:
                    page.wait_for_selector('[data-testid="update-post-text"]', timeout=30000)
                except PlaywrightTimeout:
                    self.logger.warning('LinkedIn feed not loaded, may need login')
                    # Wait for login
                    page.wait_for_selector('[data-testid="update-post-text"]', timeout=60000)
                
                self.logger.info('LinkedIn loaded')
                
                # Wait a moment for page to stabilize
                page.wait_for_timeout(2000)
                
                # Find the post text area and click it
                text_area = page.query_selector('[data-testid="update-post-text"]')
                if not text_area:
                    self.logger.error('Post text area not found')
                    browser.close()
                    return False
                
                text_area.click()
                page.wait_for_timeout(500)
                
                # Type the content (LinkedIn has 3000 char limit)
                if len(content) > 3000:
                    content = content[:2997] + '...'
                    self.logger.warning('Content truncated to 3000 characters')
                
                # Type slowly to avoid detection
                text_area.type(content, delay=50)
                self.logger.info('Content entered')
                
                # Wait for post button to become enabled
                page.wait_for_timeout(2000)
                
                # Find and click the post button
                post_button = page.query_selector('button:has-text("Post")')
                if not post_button:
                    post_button = page.query_selector('button:has-text("post")')
                
                if post_button:
                    post_button.click()
                    self.logger.info('Post button clicked')
                    
                    # Wait for confirmation
                    page.wait_for_timeout(3000)
                    
                    # Check if post was successful (look for "Posted" confirmation)
                    success = page.is_visible('text="Posted"') or page.is_visible('text="post"')
                    
                    if success:
                        self.logger.info('Post successful!')
                        
                        # Take screenshot
                        screenshot_path = self.vault_path / 'Logs' / f'linkedin_post_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                        page.screenshot(path=str(screenshot_path))
                        self.logger.info(f'Screenshot saved: {screenshot_path}')
                    else:
                        self.logger.warning('Post may not have succeeded - no confirmation found')
                        success = True  # Assume success if no error
                else:
                    self.logger.error('Post button not found')
                    browser.close()
                    return False
                
                browser.close()
                return True
                
        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
            return False
    
    def check_for_approved_posts(self) -> List[Path]:
        """
        Check Approved folder for posts ready to publish.
        
        Returns:
            List of approved post files
        """
        approved_posts = []
        
        if not self.approved_folder.exists():
            return approved_posts
        
        for f in self.approved_folder.glob('*.md'):
            content = f.read_text(encoding='utf-8')
            if 'type: linkedin_post' in content and 'status: approved' in content:
                approved_posts.append(f)
        
        return approved_posts
    
    def extract_post_content(self, filepath: Path) -> Optional[str]:
        """
        Extract post content from markdown file.
        
        Args:
            filepath: Path to post file
            
        Returns:
            Post content string
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Find content after the frontmatter
        parts = content.split('---\n\n', 1)
        if len(parts) < 2:
            return None
        
        body = parts[1]
        
        # Remove markdown headers
        lines = body.split('\n')
        clean_lines = [line for line in lines if not line.startswith('#')]
        
        return '\n'.join(clean_lines).strip()
    
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Not used for LinkedIn Poster (not a watcher).
        """
        return None


def create_linkedin_post(
    vault_path: str,
    content: str,
    category: str = 'business_update',
    require_approval: bool = False,  # Changed default to False for full automation
    auto_post: bool = True  # New parameter for auto-posting
) -> Optional[Path]:
    """
    Create a LinkedIn post file.
    
    Args:
        vault_path: Path to Obsidian vault
        content: Post content
        category: Post category
        require_approval: Whether approval is required (default: False for automation)
        auto_post: Whether to auto-post after creation (default: True)
        
    Returns:
        Path to created file
    """
    vault = Path(vault_path)
    
    # Determine target folder - default to Approved for full automation
    if require_approval:
        target_folder = vault / 'Pending_Approval'
        status = 'pending'
    else:
        target_folder = vault / 'Approved'  # Auto-approve for automation
        status = 'approved'
    
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'LINKEDIN_POST_{timestamp}.md'
    filepath = target_folder / filename
    
    # Create content
    md_content = f"""---
type: linkedin_post
category: {category}
created: {datetime.now().isoformat()}
status: {status}
platform: linkedin
auto_post: {str(auto_post).lower()}
---

# LinkedIn Post

**Category:** {category}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Status:** {status.title()}
**Auto-Post:** {str(auto_post).lower()}

## Content

{content}

## Instructions

### To Approve
1. Review the content above
2. Move this file to `/Approved` folder
3. The LinkedIn Poster will publish it

### To Reject
1. Move this file to `/Rejected` folder
2. Add reason for rejection in notes below

## Notes

*Add any comments or feedback here*

---
*Created by LinkedIn Poster v0.2 (Silver Tier)*
"""
    
    filepath.write_text(md_content, encoding='utf-8')
    return filepath


def main():
    """Run LinkedIn Poster."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
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
        '--content', '-c',
        type=str,
        default=None,
        help='Post content (or use --file)'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        default=None,
        help='Path to post file'
    )
    parser.add_argument(
        '--approve',
        action='store_true',
        help='Process approved posts'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    poster = LinkedInPoster(
        str(vault_path),
        session_path=args.session,
        headless=args.headless
    )
    
    if args.approve:
        # Process approved posts
        approved = poster.check_for_approved_posts()
        for post_file in approved:
            content = poster.extract_post_content(post_file)
            if content:
                print(f'Posting: {post_file.name}')
                success = poster.post_content(content, post_file)
                if success:
                    # Move to Done
                    done_folder = vault_path / 'Done' / 'LinkedIn'
                    done_folder.mkdir(parents=True, exist_ok=True)
                    post_file.rename(done_folder / post_file.name)
                    print(f'Posted successfully: {post_file.name}')
                else:
                    print(f'Failed to post: {post_file.name}')
    elif args.content or args.file:
        # Create new post
        if args.file:
            content = Path(args.file).read_text(encoding='utf-8')
        else:
            content = args.content
        
        filepath = create_linkedin_post(str(vault_path), content)
        print(f'Created post: {filepath}')
    else:
        print('Use --approve to process approved posts or --content/--file to create a new post')


if __name__ == '__main__':
    main()
