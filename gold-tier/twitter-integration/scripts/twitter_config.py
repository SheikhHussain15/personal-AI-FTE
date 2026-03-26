#!/usr/bin/env python3
"""
Twitter Configuration Script

Sets up Twitter API credentials and tests connection.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import set_key, load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from twitter_client import TwitterClient


def parse_args():
    parser = argparse.ArgumentParser(description='Configure Twitter API')
    parser.add_argument('--api-key', help='Twitter API Key')
    parser.add_argument('--api-secret', help='Twitter API Secret')
    parser.add_argument('--access-token', help='Access Token')
    parser.add_argument('--access-token-secret', help='Access Token Secret')
    parser.add_argument('--bearer-token', help='Bearer Token')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--interactive', action='store_true', help='Interactive setup')
    return parser.parse_args()


def get_input(prompt: str, required: bool = True) -> str:
    """Get user input with optional validation."""
    while True:
        value = input(f'{prompt}: ').strip()
        if value or not required:
            return value
        print('This field is required. Please enter a value.')


def save_config(
    vault: str,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
    bearer_token: str,
):
    """Save configuration to .env file."""
    vault_path = Path(vault).resolve()
    config_dir = vault_path / 'Scripts' / 'Config'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    env_file = config_dir / '.env.twitter'
    
    # Save to .env file
    set_key(str(env_file), 'TWITTER_API_KEY', api_key)
    set_key(str(env_file), 'TWITTER_API_SECRET', api_secret)
    set_key(str(env_file), 'TWITTER_ACCESS_TOKEN', access_token)
    set_key(str(env_file), 'TWITTER_ACCESS_TOKEN_SECRET', access_token_secret)
    set_key(str(env_file), 'TWITTER_BEARER_TOKEN', bearer_token)
    
    print(f'\n✅ Configuration saved to: {env_file}')
    print(f'   ⚠️  NEVER commit this file to version control!')
    
    # Also save to project root .env
    project_root = Path(__file__).parent.parent.parent.parent
    root_env = project_root / '.env.twitter'
    set_key(str(root_env), 'TWITTER_API_KEY', api_key)
    set_key(str(root_env), 'TWITTER_API_SECRET', api_secret)
    set_key(str(root_env), 'TWITTER_ACCESS_TOKEN', access_token)
    set_key(str(root_env), 'TWITTER_ACCESS_TOKEN_SECRET', access_token_secret)
    set_key(str(root_env), 'TWITTER_BEARER_TOKEN', bearer_token)
    
    print(f'   Also saved to: {root_env}')


def test_connection() -> bool:
    """Test Twitter API connection."""
    try:
        client = TwitterClient()
        me = client.get_me()
        print(f'\n✅ Connection successful!')
        print(f'   Username: @{me["username"]}')
        print(f'   Name: {me["name"]}')
        print(f'   ID: {me["id"]}')
        return True
    except Exception as e:
        print(f'\n❌ Connection failed: {e}')
        print('\nTroubleshooting:')
        print('1. Verify all credentials are correct')
        print('2. Ensure app has required permissions')
        print('3. Check if developer account is approved')
        return False


def main():
    args = parse_args()
    
    print('\n🐦 Twitter API Configuration')
    print('=' * 60)
    
    # Load existing config
    load_dotenv()
    
    # Interactive mode or use provided args
    if args.interactive or not all([args.api_key, args.api_secret]):
        print('\n📝 Enter your Twitter API credentials')
        print('Get these from: https://developer.twitter.com/en/portal/dashboard\n')
        
        api_key = args.api_key or get_input('API Key')
        api_secret = args.api_secret or get_input('API Secret')
        access_token = args.access_token or get_input('Access Token')
        access_token_secret = args.access_token_secret or get_input('Access Token Secret')
        bearer_token = args.bearer_token or get_input('Bearer Token')
    else:
        api_key = args.api_key
        api_secret = args.api_secret
        access_token = args.access_token
        access_token_secret = args.access_token_secret
        bearer_token = args.bearer_token or ''
    
    # Save configuration
    save_config(
        args.vault,
        api_key,
        api_secret,
        access_token,
        access_token_secret,
        bearer_token,
    )
    
    # Test connection
    print('\n🧪 Testing connection...')
    if test_connection():
        print('\n✅ Twitter configuration complete!')
        print('\nNext steps:')
        print('1. Start Twitter watcher:')
        print('   python scripts/twitter_watcher.py --vault ../AI_Employee_Vault')
        print('2. Post a tweet:')
        print('   python scripts/twitter_poster.py --vault ../AI_Employee_Vault --text "Hello Twitter!"')
        return 0
    else:
        print('\n⚠️  Configuration saved but connection test failed')
        print('   You can fix credentials and try again')
        return 1


if __name__ == '__main__':
    sys.exit(main())
