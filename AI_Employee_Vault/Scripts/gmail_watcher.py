"""
Gmail Watcher

Monitors Gmail for new important emails and creates action files
in the Needs_Action folder for Qwen Code processing.

Silver Tier - Requires Gmail API credentials.
"""

import os
import pickle
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Gmail Watcher import
import sys
from pathlib import Path

# Add AI_Employee_Vault/Scripts to path for base_watcher
vault_scripts = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault' / 'Scripts'
sys.path.insert(0, str(vault_scripts.resolve()))

from base_watcher import BaseWatcher

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new important emails.
    
    Creates action files in Needs_Action folder for each new email.
    """
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(
        self,
        vault_path: str,
        credentials_path: str = None,
        token_path: str = None,
        check_interval: int = 120
    ):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail credentials.json
            token_path: Path to store token.json
            check_interval: Seconds between checks (default: 120)
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail API libraries not installed. "
                "Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
        
        super().__init__(vault_path, check_interval)
        
        # Paths
        self.credentials_path = Path(credentials_path) if credentials_path else None
        self.token_path = Path(token_path) if token_path else self.vault_path / 'Scripts' / 'token.json'
        
        # Keywords for priority detection
        self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'important']
        
        # Gmail service
        self.service = None
        
        # Connect to Gmail
        self._connect()
        
        self.logger.info('Gmail Watcher ready')
    
    def _connect(self):
        """Authenticate and connect to Gmail API."""
        try:
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES
                )
            
            # Refresh or authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path or not self.credentials_path.exists():
                        raise FileNotFoundError(
                            f"Gmail credentials not found at {self.credentials_path}. "
                            "Run gmail_auth.py first to authenticate."
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save token
                self.token_path.write_text(creds.to_json())
                self.logger.info(f'Token saved to: {self.token_path}')
            
            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Connected to Gmail API')
            
        except Exception as e:
            self.logger.error(f'Gmail connection failed: {e}')
            raise
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new unread important messages.
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
        try:
            if not self.service:
                self._connect()
            
            # Search for unread messages (removed is:important requirement)
            # This ensures ALL unread emails are detected
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            found = results.get('messages', [])
            
            for msg in found:
                msg_id = msg['id']
                
                # Skip if already processed
                if self.is_already_processed(msg_id):
                    continue
                
                # Get full message details
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                messages.append({
                    'id': msg_id,
                    'headers': {
                        h['name']: h['value']
                        for h in message['payload']['headers']
                    },
                    'snippet': message.get('snippet', '')
                })
            
        except HttpError as e:
            if e.resp.status == 401:
                self.logger.warning('Gmail authentication expired, reconnecting...')
                self._connect()
            else:
                self.logger.error(f'Gmail API error: {e}')
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
        
        return messages
    
    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create action file for email.
        
        Args:
            item: Email message dictionary
            
        Returns:
            Path to created file
        """
        try:
            headers = item['headers']
            msg_id = item['id']
            
            # Determine priority
            subject = headers.get('Subject', '').lower()
            snippet = item.get('snippet', '').lower()
            priority = 'high' if any(
                kw in subject or kw in snippet
                for kw in self.priority_keywords
            ) else 'normal'
            
            # Parse sender
            from_email = headers.get('From', 'Unknown')
            
            # Create content
            content = f"""---
type: email
from: {from_email}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
message_id: {msg_id}
---

# Email: {headers.get('Subject', 'No Subject')}

**From:** {from_email}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Priority:** {priority.title()}

## Content

{item.get('snippet', 'No preview available')}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Create task if needed

## Notes

*Add notes or context here*

---
*Created by Gmail Watcher v0.2 (Silver Tier)*
"""
            
            # Generate filename
            safe_subject = self._safe_filename(headers.get('Subject', 'No Subject'))
            filename = f'EMAIL_{safe_subject}_{msg_id[:8]}.md'
            
            # Write file
            filepath = self.write_action_file(filename, content)
            
            # Mark as processed
            self.mark_as_processed(msg_id)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _safe_filename(self, text: str, max_length: int = 50) -> str:
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
    """Run Gmail Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--credentials', '-c',
        type=str,
        default=None,
        help='Path to Gmail credentials.json'
    )
    parser.add_argument(
        '--token', '-t',
        type=str,
        default=None,
        help='Path to token.json'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=120,
        help='Check interval in seconds'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    # Check for credentials
    credentials_path = None
    if args.credentials:
        credentials_path = Path(args.credentials)
    else:
        # Try default locations
        default_paths = [
            vault_path / 'Scripts' / 'gmail_credentials.json',
            Path.home() / '.credentials' / 'gmail' / 'credentials.json',
            Path('credentials.json')
        ]
        for p in default_paths:
            if p.exists():
                credentials_path = p
                break
    
    watcher = GmailWatcher(
        str(vault_path),
        credentials_path=credentials_path,
        token_path=args.token,
        check_interval=args.interval
    )
    watcher.run()


if __name__ == '__main__':
    main()
