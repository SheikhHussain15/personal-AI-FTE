#!/usr/bin/env python3
"""
Facebook Watcher

Monitors Facebook Page for new messages, comments, and mentions.
Uses official Graph API - no Playwright required.
Creates action files in Needs_Action folder for Qwen Code to process.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from facebook_client import FacebookClient, GRAPH_API_BASE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class FacebookWatcher:
    """Watcher for Facebook Page activity using Graph API."""
    
    def __init__(
        self,
        vault_path: str,
        page_id: Optional[str] = None,
        check_interval: int = 60,
        keywords: Optional[List[str]] = None,
    ):
        """
        Initialize Facebook Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            page_id: Facebook Page ID to monitor (optional, loads from .env)
            check_interval: Seconds between checks
            keywords: Keywords that trigger urgent alerts
        """
        load_dotenv()
        
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.keywords = keywords or os.getenv('META_URGENT_KEYWORDS', 'urgent,asap,invoice,payment,help,pricing').split(',')
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Initialize client
        try:
            self.client = FacebookClient(page_id=page_id)
            self.page_id = self.client.page_id
        except ValueError as e:
            logger.error(str(e))
            logger.error('Run facebook_auth.py to configure credentials')
            raise
        
        # Track processed items to avoid duplicates
        self.processed_posts: Set[str] = set()
        self.processed_comments: Set[str] = set()
        self.processed_messages: Set[str] = set()
        
        # Load previously processed IDs from cache
        self._load_cache()
    
    def _load_cache(self):
        """Load processed IDs from cache file."""
        cache_file = self.vault_path / 'Scripts' / 'facebook_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                    self.processed_posts = set(cache.get('posts', []))
                    self.processed_comments = set(cache.get('comments', []))
                    self.processed_messages = set(cache.get('messages', []))
                logger.info(f'Loaded cache: {len(self.processed_posts)} posts, '
                           f'{len(self.processed_comments)} comments, '
                           f'{len(self.processed_messages)} messages')
            except Exception as e:
                logger.warning(f'Failed to load cache: {e}')
    
    def _save_cache(self):
        """Save processed IDs to cache file."""
        cache_file = self.vault_path / 'Scripts' / 'facebook_cache.json'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(cache_file, 'w') as f:
                cache = {
                    'posts': list(self.processed_posts)[-1000:],
                    'comments': list(self.processed_comments)[-1000:],
                    'messages': list(self.processed_messages)[-1000:],
                    'updated': datetime.now().isoformat(),
                }
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.warning(f'Failed to save cache: {e}')
    
    def _is_urgent(self, text: str) -> bool:
        """Check if text contains urgent keywords."""
        if not text:
            return False
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in self.keywords)
    
    def _create_action_file(self, item_type: str, data: Dict[str, any], priority: str = 'normal') -> Path:
        """Create action file in Needs_Action folder."""
        # Generate unique ID
        item_id = data.get('id', str(datetime.now().timestamp()))
        unique_hash = hashlib.md5(f'{item_type}:{item_id}'.encode()).hexdigest()[:8]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'FACEBOOK_{item_type.upper()}_{unique_hash}_{timestamp}.md'
        filepath = self.needs_action / filename
        
        # Format content
        from_author = data.get('from', {})
        if isinstance(from_author, dict):
            author_name = from_author.get('name', 'Unknown')
        else:
            author_name = 'Unknown'
        
        content = f'''---
type: facebook_{item_type}
platform: Facebook
item_id: {item_id}
from: {author_name}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
urgency: {"high" if priority == "high" else "normal"}
---

# Facebook {item_type.title()} Alert

## Details
- **From**: {author_name}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Platform**: Facebook Page (Graph API)
- **Priority**: {priority.upper()}

## Content
{data.get('message', data.get('body', 'No content'))}

## Metadata
- **Post/Comment ID**: {item_id}
- **Permalink**: {data.get('permalink', 'N/A')}
- **Created**: {data.get('created_time', 'N/A')}

## Suggested Actions
- [ ] Review and respond to {item_type}
- [ ] Escalate if urgent
- [ ] Log interaction
- [ ] Move to Done when complete

---
*Generated by Facebook Watcher (Graph API) | AI Employee v0.3 (Gold Tier)*
'''
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f'Created action file: {filepath.name}')
        
        return filepath
    
    def check_messages(self) -> List[Path]:
        """Check for new page messages via Graph API."""
        created_files = []
        
        try:
            messages = self.client.get_page_messages(page_id=self.page_id, limit=10)
            
            for conv in messages:
                conv_id = conv.get('id', '')
                messages_list = conv.get('messages', {}).get('data', [])
                
                for msg in messages_list:
                    msg_id = msg.get('id', '')
                    
                    if msg_id in self.processed_messages:
                        continue
                    
                    message_text = msg.get('message', '')
                    from_data = msg.get('from', {})
                    
                    # Check if urgent
                    priority = 'high' if self._is_urgent(message_text) else 'normal'
                    
                    # Create action file
                    action_data = {
                        'id': msg_id,
                        'conversation_id': conv_id,
                        'message': message_text,
                        'from': from_data,
                        'created_time': msg.get('created_time', ''),
                        'permalink': conv.get('link', ''),
                    }
                    
                    filepath = self._create_action_file('message', action_data, priority)
                    created_files.append(filepath)
                    
                    self.processed_messages.add(msg_id)
            
            if created_files:
                logger.info(f'Found {len(created_files)} new messages')
                
        except Exception as e:
            logger.error(f'Error checking messages: {e}')
        
        return created_files
    
    def check_comments(self) -> List[Path]:
        """Check for new comments on recent posts via Graph API."""
        created_files = []
        
        try:
            # Get recent posts
            posts = self.client.get_page_posts(page_id=self.page_id, limit=5)
            
            for post in posts:
                post_id = post.get('id', '')
                
                if post_id in self.processed_posts:
                    continue
                
                # Get comments on this post
                comments = self.client.get_post_comments(post_id, limit=10)
                
                for comment in comments:
                    comment_id = comment.get('id', '')
                    
                    if comment_id in self.processed_comments:
                        continue
                    
                    comment_text = comment.get('message', '')
                    from_data = comment.get('from', {})
                    
                    # Check if urgent
                    priority = 'high' if self._is_urgent(comment_text) else 'normal'
                    
                    # Create action file
                    action_data = {
                        'id': comment_id,
                        'post_id': post_id,
                        'message': comment_text,
                        'from': from_data,
                        'created_time': comment.get('created_time', ''),
                        'permalink': post.get('permalink_url', ''),
                    }
                    
                    filepath = self._create_action_file('comment', action_data, priority)
                    created_files.append(filepath)
                    
                    self.processed_comments.add(comment_id)
                
                self.processed_posts.add(post_id)
            
            if created_files:
                logger.info(f'Found {len(created_files)} new comments')
                
        except Exception as e:
            logger.error(f'Error checking comments: {e}')
        
        return created_files
    
    def run(self):
        """Run the watcher loop."""
        logger.info(f'Starting Facebook Watcher (Graph API)')
        logger.info(f'Vault: {self.vault_path}')
        logger.info(f'Page ID: {self.page_id}')
        logger.info(f'Check interval: {self.check_interval}s')
        logger.info(f'Urgent keywords: {", ".join(self.keywords)}')
        
        try:
            # Test connection first
            page_info = self.client.get_page_info()
            logger.info(f'Connected to Facebook Page: {page_info.get("name")}')
            
            while True:
                try:
                    # Check for new activity
                    new_messages = self.check_messages()
                    new_comments = self.check_comments()
                    
                    total_new = len(new_messages) + len(new_comments)
                    
                    if total_new > 0:
                        logger.info(f'Total new items: {total_new}')
                        # Save cache after finding new items
                        self._save_cache()
                    
                    # Wait for next check
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    logger.info('Watcher stopped by user')
                    self._save_cache()
                    break
                except Exception as e:
                    logger.error(f'Error in watcher loop: {e}')
                    time.sleep(self.check_interval)
                    
        except Exception as e:
            logger.error(f'Watcher error: {e}')
            return 1
        
        return 0


def parse_args():
    parser = argparse.ArgumentParser(description='Facebook Watcher (Graph API)')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--page-id', help='Facebook Page ID (default: from .env)')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--keywords', nargs='+', help='Urgent keywords')
    return parser.parse_args()


def main():
    args = parse_args()
    
    try:
        watcher = FacebookWatcher(
            vault_path=args.vault,
            page_id=args.page_id,
            check_interval=args.interval,
            keywords=args.keywords,
        )
        return watcher.run()
    except Exception as e:
        logger.error(f'Failed to start watcher: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
