#!/usr/bin/env python3
"""
Twitter Watcher

Monitors Twitter for mentions, DMs, and keyword mentions.
Creates action files in Needs_Action folder for Qwen Code to process.
"""

import argparse
import hashlib
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from twitter_client import TwitterClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class TwitterWatcher:
    """Watcher for Twitter activity."""
    
    def __init__(
        self,
        vault_path: str,
        check_interval: int = 30,
        keywords: Optional[List[str]] = None,
    ):
        """
        Initialize Twitter Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks
            keywords: Keywords that trigger urgent alerts
        """
        load_dotenv()
        
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing']
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Initialize client
        self.client = TwitterClient()
        
        # Track processed items to avoid duplicates
        self.processed_mentions: Set[str] = set()
        self.processed_dms: Set[str] = set()
        
        # Load previously processed IDs from cache
        self._load_cache()
    
    def _load_cache(self):
        """Load processed IDs from cache file."""
        cache_file = self.vault_path / 'Scripts' / 'twitter_cache.json'
        if cache_file.exists():
            try:
                import json
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                    self.processed_mentions = set(cache.get('mentions', []))
                    self.processed_dms = set(cache.get('dms', []))
                logger.info(f'Loaded cache: {len(self.processed_mentions)} mentions, '
                           f'{len(self.processed_dms)} DMs')
            except Exception as e:
                logger.warning(f'Failed to load cache: {e}')
    
    def _save_cache(self):
        """Save processed IDs to cache file."""
        cache_file = self.vault_path / 'Scripts' / 'twitter_cache.json'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import json
            cache = {
                'mentions': list(self.processed_mentions),
                'dms': list(self.processed_dms),
                'updated': datetime.now().isoformat(),
            }
            # Keep only last 1000 IDs to prevent unbounded growth
            for key in ['mentions', 'dms']:
                cache[key] = cache[key][-1000:]
            
            with open(cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.warning(f'Failed to save cache: {e}')
    
    def _is_urgent(self, text: str) -> bool:
        """Check if text contains urgent keywords."""
        if not text:
            return False
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.keywords)
    
    def _create_action_file(self, item_type: str, data: Dict[str, any], priority: str = 'normal') -> Path:
        """Create action file in Needs_Action folder."""
        # Generate unique ID
        item_id = data.get('id', str(datetime.now().timestamp()))
        unique_hash = hashlib.md5(f'{item_type}:{item_id}'.encode()).hexdigest()[:8]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'TWITTER_{item_type.upper()}_{unique_hash}_{timestamp}.md'
        filepath = self.needs_action / filename
        
        content = f'''---
type: twitter_{item_type}
platform: Twitter
item_id: {item_id}
from: {data.get('author_username', 'Unknown')}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
urgency: {"high" if priority == "high" else "normal"}
---

# Twitter {item_type.title()} Alert

## Details
- **From**: @{data.get('author_username', 'Unknown')}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Platform**: Twitter/X
- **Priority**: {priority.upper()}

## Content
{data.get('text', 'No content')}

## Metrics
- **Likes**: {data.get('likes', 0)}
- **Retweets**: {data.get('retweets', 0)}
- **Replies**: {data.get('replies', 0)}

## Metadata
- **Tweet ID**: {item_id}
- **Permalink**: {data.get('permalink', 'N/A')}
- **Created**: {data.get('created_at', 'N/A')}

## Suggested Actions
- [ ] Review and respond to {item_type}
- [ ] Escalate if urgent
- [ ] Log interaction
- [ ] Move to Done when complete

---
*Generated by Twitter Watcher | AI Employee v0.3 (Gold Tier)*
'''
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f'Created action file: {filepath.name}')
        
        return filepath
    
    def check_mentions(self) -> List[Path]:
        """Check for new mentions."""
        created_files = []
        
        try:
            mentions = self.client.get_mentions(limit=10)
            
            for mention in mentions:
                mention_id = mention.get('id', '')
                
                if mention_id in self.processed_mentions:
                    continue
                
                text = mention.get('text', '')
                
                # Check if urgent
                priority = 'high' if self._is_urgent(text) else 'normal'
                
                # Create action file
                action_data = {
                    'id': mention_id,
                    'text': text,
                    'author_username': mention.get('author_username', 'Unknown'),
                    'created_at': mention.get('created_at', ''),
                    'permalink': f'https://twitter.com/i/web/status/{mention_id}',
                    'likes': mention.get('metrics', {}).get('like_count', 0),
                    'retweets': mention.get('metrics', {}).get('retweet_count', 0),
                    'replies': mention.get('metrics', {}).get('reply_count', 0),
                }
                
                filepath = self._create_action_file('mention', action_data, priority)
                created_files.append(filepath)
                
                self.processed_mentions.add(mention_id)
            
            if created_files:
                logger.info(f'Found {len(created_files)} new mentions')
                
        except Exception as e:
            logger.error(f'Error checking mentions: {e}')
        
        return created_files
    
    def check_dms(self) -> List[Path]:
        """Check for new direct messages."""
        created_files = []
        
        try:
            dms = self.client.get_dms(limit=10)
            
            for dm in dms:
                dm_id = dm.get('id', '')
                
                if dm_id in self.processed_dms:
                    continue
                
                text = dm.get('text', '')
                
                # Check if urgent
                priority = 'high' if self._is_urgent(text) else 'normal'
                
                # Create action file
                action_data = {
                    'id': dm_id,
                    'text': text,
                    'author_username': 'Unknown',  # DM API doesn't provide sender info easily
                    'created_at': dm.get('created_at', ''),
                    'permalink': 'N/A',
                }
                
                filepath = self._create_action_file('dm', action_data, priority)
                created_files.append(filepath)
                
                self.processed_dms.add(dm_id)
            
            if created_files:
                logger.info(f'Found {len(created_files)} new DMs')
                
        except Exception as e:
            logger.error(f'Error checking DMs: {e}')
        
        return created_files
    
    def run(self):
        """Run the watcher loop."""
        logger.info(f'Starting Twitter Watcher')
        logger.info(f'Vault: {self.vault_path}')
        logger.info(f'Check interval: {self.check_interval}s')
        logger.info(f'Urgent keywords: {", ".join(self.keywords)}')
        
        try:
            # Test connection first
            me = self.client.get_me()
            logger.info(f'Connected as: @{me["username"]}')
            
            while True:
                try:
                    # Check for new activity
                    new_mentions = self.check_mentions()
                    new_dms = self.check_dms()
                    
                    total_new = len(new_mentions) + len(new_dms)
                    
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
    parser = argparse.ArgumentParser(description='Twitter Watcher')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--keywords', nargs='+', help='Urgent keywords')
    return parser.parse_args()


def main():
    args = parse_args()
    
    try:
        watcher = TwitterWatcher(
            vault_path=args.vault,
            check_interval=args.interval,
            keywords=args.keywords,
        )
        return watcher.run()
    except Exception as e:
        logger.error(f'Failed to start watcher: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
