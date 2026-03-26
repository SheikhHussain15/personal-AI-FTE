"""
WhatsApp Watcher

Monitors WhatsApp Web for urgent messages using Playwright browser automation.
Creates action files in Needs_Action folder for Qwen Code processing.

Silver Tier - Uses Playwright for browser automation.

WARNING: Be aware of WhatsApp's Terms of Service when using automation.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for base_watcher import
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault' / 'Scripts'))

from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for urgent messages.
    
    Uses Playwright to automate WhatsApp Web and detect messages
    containing priority keywords.
    """
    
    # Default keywords to detect
    DEFAULT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'important']
    
    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        check_interval: int = 30,
        keywords: List[str] = None,
        headless: bool = True
    ):
        """
        Initialize WhatsApp Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session
            check_interval: Seconds between checks (default: 30)
            keywords: Keywords to detect (default: DEFAULT_KEYWORDS)
            headless: Run browser without UI (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. "
                "Run: pip install playwright && playwright install chromium"
            )
        
        super().__init__(vault_path, check_interval)
        
        # Session path
        self.session_path = Path(session_path) if session_path else self.vault_path / 'Scripts' / 'whatsapp_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Keywords
        self.keywords = keywords if keywords else self.DEFAULT_KEYWORDS
        
        # Browser settings
        self.headless = headless
        
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Keywords: {self.keywords}')
        self.logger.info('WhatsApp Watcher ready')
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new messages with keywords.
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0]
                
                # Navigate to WhatsApp Web
                self.logger.debug('Navigating to WhatsApp Web...')
                page.goto('https://web.whatsapp.com', timeout=60000)
                
                # Wait for chat list to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                except PlaywrightTimeout:
                    self.logger.warning('WhatsApp Web not loaded, may need QR scan')
                    browser.close()
                    return messages
                
                # Give time for messages to load
                page.wait_for_timeout(3000)
                
                # Find unread messages
                self.logger.debug('Scanning for unread messages...')
                
                # Get all chat items
                chat_items = page.query_selector_all('[data-testid="chat-list"] > div')
                
                for chat in chat_items:
                    try:
                        # Get chat name
                        chat_name_elem = chat.query_selector('[data-testid="chat-info"]')
                        chat_name = chat_name_elem.inner_text() if chat_name_elem else 'Unknown'
                        
                        # Check for unread indicator
                        aria_label = chat.get_attribute('aria-label', '')
                        
                        if 'unread' in aria_label.lower() or 'unread' in chat.inner_text().lower():
                            # Get message text
                            message_text = chat.inner_text().lower()
                            
                            # Check for keywords
                            matched_keywords = [
                                kw for kw in self.keywords
                                if kw in message_text
                            ]
                            
                            if matched_keywords:
                                messages.append({
                                    'chat': chat_name,
                                    'text': chat.inner_text(),
                                    'keywords': matched_keywords,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.logger.info(f'Found message with keywords: {matched_keywords}')
                    
                    except Exception as e:
                        self.logger.debug(f'Error processing chat: {e}')
                        continue
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error checking WhatsApp: {e}')
        
        return messages
    
    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create action file for WhatsApp message.
        
        Args:
            item: Message dictionary
            
        Returns:
            Path to created file
        """
        try:
            # Generate unique ID from content
            msg_id = f"{item['chat']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create content
            content = f"""---
type: whatsapp
from: {item['chat']}
received: {datetime.now().isoformat()}
priority: high
status: pending
keywords: {', '.join(item['keywords'])}
message_id: {msg_id}
---

# WhatsApp Message

**From:** {item['chat']}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Priority:** High
**Keywords:** {', '.join(item['keywords'])}

## Message Content

{item['text']}

## Suggested Actions

- [ ] Reply on WhatsApp
- [ ] Take required action
- [ ] Follow up if needed

## Notes

*Add notes or context here*

---
*Created by WhatsApp Watcher v0.2 (Silver Tier)*
"""
            
            # Generate filename
            safe_chat = self._safe_filename(item['chat'])
            filename = f'WHATSAPP_{safe_chat}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            
            # Write file
            filepath = self.write_action_file(filename, content)
            
            # Mark as processed
            self.mark_as_processed(msg_id)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _safe_filename(self, text: str, max_length: int = 30) -> str:
        """Convert text to safe filename."""
        # Remove invalid characters
        invalid = '<>:"/\\|？*'
        for char in invalid:
            text = text.replace(char, '_')
        
        # Truncate
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()


def main():
    """Run WhatsApp Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
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
        default=30,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--keywords', '-k',
        type=str,
        default=None,
        help='Comma-separated keywords to detect'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    # Parse keywords
    keywords = None
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
    
    watcher = WhatsAppWatcher(
        str(vault_path),
        session_path=args.session,
        check_interval=args.interval,
        keywords=keywords,
        headless=args.headless
    )
    watcher.run()


if __name__ == '__main__':
    main()
