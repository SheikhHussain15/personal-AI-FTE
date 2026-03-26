#!/usr/bin/env python3
"""
Instagram Poster (Convenience Wrapper)

Specialized poster for Instagram Business accounts.
Wraps facebook_poster.py with Instagram-specific defaults.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from facebook_poster import FacebookPoster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class InstagramPoster(FacebookPoster):
    """Specialized poster for Instagram."""
    
    def __init__(self, vault_path: str):
        super().__init__(vault_path)
    
    def create_post_request(
        self,
        caption: str,
        image_url: str,
        scheduled_time: str = None,
    ) -> Path:
        """Create Instagram post request."""
        return super().create_post_request(
            message=caption,
            platform='instagram',
            image_url=image_url,
            scheduled_time=scheduled_time,
        )
    
    def post_direct(
        self,
        caption: str,
        image_url: str,
    ) -> dict:
        """Post directly to Instagram."""
        return super().post_direct(
            message=caption,
            platform='instagram',
            image_url=image_url,
        )


def parse_args():
    parser = argparse.ArgumentParser(description='Instagram Poster')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--caption', required=True, help='Instagram caption')
    parser.add_argument('--image-url', required=True, help='Image URL (must be publicly accessible)')
    parser.add_argument('--request', action='store_true', help='Create approval request')
    parser.add_argument('--execute', action='store_true', help='Execute approved post')
    parser.add_argument('--file', help='Path to approved post file')
    parser.add_argument('--direct', action='store_true', help='Post directly (no approval)')
    return parser.parse_args()


def main():
    args = parse_args()
    
    poster = InstagramPoster(vault_path=args.vault)
    
    # Execute approved post
    if args.execute and args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = poster.approved / args.file
        
        if filepath.exists():
            result = poster.execute_post(filepath)
            print(json.dumps(result, indent=2))
            return 0 if result.get('success') else 1
        else:
            print(f'File not found: {filepath}')
            return 1
    
    # Create approval request
    if args.request:
        filepath = poster.create_post_request(
            caption=args.caption,
            image_url=args.image_url,
        )
        print(f'Created approval request: {filepath}')
        return 0
    
    # Direct post (no approval)
    if args.direct:
        result = poster.post_direct(
            caption=args.caption,
            image_url=args.image_url,
        )
        print(json.dumps(result, indent=2))
        return 0 if result.get('success') else 1
    
    # Default: show usage
    print('Instagram Poster')
    print('=' * 50)
    print('\nUsage:')
    print('1. Create approval request:')
    print('   python instagram_poster.py --vault PATH --request \\')
    print('     --caption "New product launch! #business" \\')
    print('     --image-url "https://example.com/image.jpg"')
    print('\n2. Execute approved post:')
    print('   python instagram_poster.py --vault PATH --execute --file POST_INSTAGRAM_*.md')
    print('\n3. Direct post (no approval):')
    print('   python instagram_poster.py --vault PATH --direct \\')
    print('     --caption "Hello Instagram!" \\')
    print('     --image-url "https://example.com/image.jpg"')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
