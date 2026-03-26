#!/usr/bin/env python3
"""
Facebook/Instagram Graph API Authentication Script

Generates long-lived access tokens and configures .env.facebook file.
Uses official Meta Graph API - no Playwright required.
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from dotenv import set_key, load_dotenv


# Meta Graph API endpoints
GRAPH_API_BASE = 'https://graph.facebook.com/v19.0'
OAUTH_BASE = 'https://www.facebook.com/v19.0/dialog/oauth'
TOKEN_EXCHANGE_URL = 'https://graph.facebook.com/v19.0/oauth/access_token'


def parse_args():
    parser = argparse.ArgumentParser(description='Facebook/Instagram Graph API Authentication')
    parser.add_argument('--app-id', help='Meta App ID')
    parser.add_argument('--app-secret', help='Meta App Secret')
    parser.add_argument('--redirect-uri', default='https://localhost/', help='OAuth redirect URI')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--interactive', action='store_true', help='Interactive setup')
    return parser.parse_args()


def get_oauth_url(app_id: str, redirect_uri: str) -> str:
    """Generate OAuth URL for Facebook Login."""
    params = {
        'client_id': app_id,
        'redirect_uri': redirect_uri,
        'scope': ','.join([
            'pages_read_engagement',
            'pages_manage_posts',
            'pages_messaging',
            'pages_read_user_content',
            'instagram_basic',
            'instagram_content_publish',
            'instagram_manage_comments',
            'instagram_manage_messages',
            'publish_video',
        ]),
        'response_type': 'code',
    }
    return f"{OAUTH_BASE}?{urllib.parse.urlencode(params)}"


def get_token_from_code(app_id: str, app_secret: str, code: str, redirect_uri: str) -> Optional[str]:
    """Exchange authorization code for access token."""
    try:
        response = requests.get(
            TOKEN_EXCHANGE_URL,
            params={
                'client_id': app_id,
                'client_secret': app_secret,
                'redirect_uri': redirect_uri,
                'code': code,
            },
            timeout=10,
        )
        
        result = response.json()
        
        if 'access_token' in result:
            return result['access_token']
        else:
            print(f"❌ Token exchange failed: {result.get('error', {}).get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def exchange_for_long_lived_token(user_token: str, app_id: str, app_secret: str) -> Optional[str]:
    """
    Exchange short-lived user token for long-lived token (60 days).
    """
    try:
        response = requests.get(
            TOKEN_EXCHANGE_URL,
            params={
                'grant_type': 'fb_exchange_token',
                'client_id': app_id,
                'client_secret': app_secret,
                'fb_exchange_token': user_token,
            },
            timeout=10,
        )
        
        result = response.json()
        
        if 'access_token' in result:
            expires_in = result.get('expires_in', 5184000)
            days = expires_in // 86400
            print(f'\n✅ Long-lived token generated!')
            print(f'   Expires in: {expires_in} seconds (~{days} days)')
            return result['access_token']
        else:
            print(f'❌ Token exchange failed: {result.get("error", {}).get("message", "Unknown error")}')
            return None
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return None


def get_page_access_token(user_token: str, page_id: str) -> Optional[Dict[str, Any]]:
    """
    Get page access token from user token.
    Returns dict with page_token and page_name.
    """
    try:
        response = requests.get(
            f'{GRAPH_API_BASE}/{page_id}',
            params={
                'fields': 'access_token,name,instagram_business_account',
                'access_token': user_token,
            },
            timeout=10,
        )
        
        result = response.json()
        
        if 'access_token' in result:
            return {
                'page_token': result['access_token'],
                'page_name': result.get('name', page_id),
                'instagram_id': result.get('instagram_business_account', {}).get('id'),
            }
        else:
            print(f'❌ Failed to get page token: {result.get("error", {}).get("message", "Unknown error")}')
            return None
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return None


def get_user_info(token: str) -> Optional[Dict[str, Any]]:
    """Get authenticated user info."""
    try:
        response = requests.get(
            f'{GRAPH_API_BASE}/me',
            params={
                'fields': 'id,name,email',
                'access_token': token,
            },
            timeout=10,
        )
        
        result = response.json()
        
        if 'id' in result:
            return result
        else:
            print(f'❌ Failed to get user info: {result.get("error", {}).get("message", "Unknown error")}')
            return None
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return None


def get_user_pages(token: str) -> list:
    """Get list of pages managed by user."""
    try:
        response = requests.get(
            f'{GRAPH_API_BASE}/me/accounts',
            params={
                'fields': 'id,name,access_token,instagram_business_account',
                'access_token': token,
            },
            timeout=10,
        )
        
        result = response.json()
        
        if 'data' in result:
            return result['data']
        else:
            print(f'❌ Failed to get pages: {result.get("error", {}).get("message", "Unknown error")}')
            return []
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return []


def save_config(
    vault: str,
    app_id: str,
    app_secret: str,
    access_token: str,
    page_id: Optional[str] = None,
    page_token: Optional[str] = None,
    page_name: Optional[str] = None,
    instagram_id: Optional[str] = None,
) -> Path:
    """Save configuration to .env.facebook file."""
    vault_path = Path(vault).resolve()
    
    # Save to project root
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / '.env.facebook'
    
    # Save to .env file
    set_key(str(env_file), 'META_APP_ID', app_id)
    set_key(str(env_file), 'META_APP_SECRET', app_secret)
    set_key(str(env_file), 'META_ACCESS_TOKEN', access_token)
    set_key(str(env_file), 'META_API_VERSION', 'v19.0')
    set_key(str(env_file), 'META_CHECK_INTERVAL', '60')
    set_key(str(env_file), 'META_URGENT_KEYWORDS', 'urgent,asap,invoice,payment,help,pricing')
    
    if page_id:
        set_key(str(env_file), 'META_PAGE_ID', page_id)
    if page_token:
        set_key(str(env_file), 'META_PAGE_TOKEN', page_token)
    if page_name:
        set_key(str(env_file), 'META_PAGE_NAME', page_name)
    if instagram_id:
        set_key(str(env_file), 'META_INSTAGRAM_ID', instagram_id)
    
    # Also save to vault config
    config_dir = vault_path / 'Scripts' / 'Config'
    config_dir.mkdir(parents=True, exist_ok=True)
    vault_env = config_dir / '.env.facebook'
    
    # Copy same config to vault
    for key, value in [
        ('META_APP_ID', app_id),
        ('META_APP_SECRET', app_secret),
        ('META_ACCESS_TOKEN', access_token),
        ('META_API_VERSION', 'v19.0'),
        ('META_CHECK_INTERVAL', '60'),
        ('META_URGENT_KEYWORDS', 'urgent,asap,invoice,payment,help,pricing'),
    ]:
        set_key(str(vault_env), key, value)
    
    if page_id:
        set_key(str(vault_env), 'META_PAGE_ID', page_id)
    if page_token:
        set_key(str(vault_env), 'META_PAGE_TOKEN', page_token)
    if instagram_id:
        set_key(str(vault_env), 'META_INSTAGRAM_ID', instagram_id)
    
    return env_file


def test_connection(token: str, page_id: Optional[str] = None) -> bool:
    """Test connection to Graph API."""
    try:
        # Test user token
        user = get_user_info(token)
        
        if not user:
            return False
        
        print(f'\n✅ Connection successful!')
        print(f'   User: {user.get("name")} ({user.get("id")})')
        
        if page_id:
            # Test page access
            response = requests.get(
                f'{GRAPH_API_BASE}/{page_id}',
                params={
                    'fields': 'name',
                    'access_token': token,
                },
                timeout=10,
            )
            page_result = response.json()
            if 'name' in page_result:
                print(f'   Page: {page_result["name"]}')
            else:
                print(f'   ⚠️  Page access may be limited')
        
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False


def interactive_setup() -> Dict[str, Any]:
    """Interactive setup wizard."""
    print('\n' + '=' * 60)
    print('  FACEBOOK/INSTAGRAM GRAPH API SETUP')
    print('  AI Employee - Gold Tier')
    print('=' * 60)
    
    print('\n📋 Step 1: Get Meta Developer Credentials')
    print('-' * 60)
    print('1. Go to: https://developers.facebook.com/')
    print('2. Create a Business App (or select existing)')
    print('3. Add products: Facebook Login, Instagram Graph API')
    print('4. Go to Dashboard → Settings → Basic')
    print('5. Copy App ID and App Secret\n')
    
    app_id = input('Enter your App ID: ').strip()
    app_secret = input('Enter your App Secret: ').strip()
    
    if not app_id or not app_secret:
        print('❌ App ID and App Secret are required')
        return {}
    
    print('\n📋 Step 2: Generate Access Token')
    print('-' * 60)
    print('Option A: Use Graph API Explorer (Recommended)')
    print('  1. Go to: https://developers.facebook.com/tools/explorer/')
    print('  2. Select your app from dropdown')
    print('  3. Click "Generate Access Token"')
    print('  4. Select permissions:')
    print('     - pages_read_engagement')
    print('     - pages_manage_posts')
    print('     - pages_messaging')
    print('     - instagram_basic')
    print('     - instagram_content_publish')
    print('  5. Click Continue → Allow')
    print('  6. Copy the generated token\n')
    
    print('Option B: Use OAuth Flow')
    oauth_url = get_oauth_url(app_id, 'https://localhost/')
    print(f'  URL: {oauth_url}')
    print('  1. Open URL in browser')
    print('  2. Authorize the app')
    print('  3. Copy the code from redirect URL')
    print('  4. Enter code below\n')
    
    choice = input('Choose method (A=Explorer, B=OAuth, E=Exit): ').strip().lower()
    
    if choice == 'e':
        return {}
    
    if choice == 'a':
        user_token = input('Paste your access token: ').strip()
    else:
        webbrowser.open(oauth_url)
        code = input('Enter authorization code: ').strip()
        user_token = get_token_from_code(app_id, app_secret, code, 'https://localhost/')
        
        if not user_token:
            print('❌ Failed to get token from code')
            return {}
    
    if not user_token:
        print('❌ No token provided')
        return {}
    
    print('\n📋 Step 3: Exchange for Long-Lived Token')
    print('-' * 60)
    long_lived_token = exchange_for_long_lived_token(user_token, app_id, app_secret)
    
    if not long_lived_token:
        print('⚠️  Using short-lived token (will expire in ~1 hour)')
        long_lived_token = user_token
    
    print('\n📋 Step 4: Select Facebook Page')
    print('-' * 60)
    
    pages = get_user_pages(long_lived_token)
    
    if not pages:
        print('⚠️  No pages found. Make sure your app has page permissions.')
        page_id = input('Enter Page ID manually (or press Enter to skip): ').strip()
        page_token = None
        page_name = None
        instagram_id = None
    else:
        print('\nYour Pages:')
        for i, page in enumerate(pages, 1):
            ig_info = ''
            if page.get('instagram_business_account'):
                ig_info = ' [Instagram Connected]'
            print(f'  {i}. {page.get("name")} (ID: {page.get("id")}){ig_info}')
        
        choice = input(f'\nSelect page (1-{len(pages)}, or 0 to skip): ').strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(pages):
                selected_page = pages[idx]
                page_id = selected_page['id']
                page_token = selected_page.get('access_token', long_lived_token)
                page_name = selected_page['name']
                instagram_id = selected_page.get('instagram_business_account', {}).get('id')
                
                print(f'\n✅ Selected: {page_name}')
                if instagram_id:
                    print(f'   Instagram Business Account ID: {instagram_id}')
            else:
                page_id = page_token = page_name = instagram_id = None
        except ValueError:
            page_id = page_token = page_name = instagram_id = None
    
    return {
        'app_id': app_id,
        'app_secret': app_secret,
        'access_token': long_lived_token,
        'page_id': page_id,
        'page_token': page_token,
        'page_name': page_name,
        'instagram_id': instagram_id,
    }


def main():
    args = parse_args()
    
    # Load existing config
    load_dotenv()
    
    # Check for existing config
    existing_app_id = os.getenv('META_APP_ID')
    
    if existing_app_id and not args.interactive:
        print('\n⚠️  Existing configuration found!')
        print(f'   App ID: {existing_app_id}')
        print(f'   Page ID: {os.getenv("META_PAGE_ID", "Not set")}')
        print(f'   Instagram ID: {os.getenv("META_INSTAGRAM_ID", "Not set")}')
        
        response = input('\nReconfigure? (y/N): ').strip().lower()
        if not response.startswith('y'):
            # Test existing connection
            existing_token = os.getenv('META_ACCESS_TOKEN')
            if existing_token:
                test_connection(existing_token, os.getenv('META_PAGE_ID'))
            return 0
    
    # Interactive setup
    if args.interactive or not (args.app_id and args.app_secret):
        config = interactive_setup()
        
        if not config:
            print('\n❌ Setup cancelled')
            return 1
        
        app_id = config['app_id']
        app_secret = config['app_secret']
        access_token = config['access_token']
        page_id = config.get('page_id')
        page_token = config.get('page_token')
        page_name = config.get('page_name')
        instagram_id = config.get('instagram_id')
    else:
        app_id = args.app_id
        app_secret = args.app_secret
        
        # For CLI mode, assume user provides long-lived token
        print('\n📝 Enter your long-lived access token')
        print('   Generate at: https://developers.facebook.com/tools/explorer/')
        access_token = input('Access token: ').strip()
        
        page_id = None
        page_token = None
        page_name = None
        instagram_id = None
    
    # Save configuration
    env_file = save_config(
        args.vault,
        app_id,
        app_secret,
        access_token,
        page_id,
        page_token,
        page_name,
        instagram_id,
    )
    
    print(f'\n✅ Configuration saved to: {env_file}')
    print(f'   ⚠️  NEVER commit this file to version control!')
    
    # Test connection
    print('\n🧪 Testing connection...')
    if test_connection(access_token, page_id):
        print('\n✅ Facebook/Instagram configuration complete!')
        print('\n📚 Next steps:')
        print('1. Start Facebook watcher:')
        print('   python gold-tier/facebook-integration/scripts/facebook_watcher.py --vault AI_Employee_Vault')
        print('2. Create a test post:')
        print('   python gold-tier/facebook-integration/scripts/facebook_poster.py --vault AI_Employee_Vault --request --message "Hello!"')
        print('\n📅 Token Management:')
        print('   Your long-lived token expires in ~60 days.')
        print('   Run this script again to refresh before expiration.')
        return 0
    else:
        print('\n⚠️  Configuration saved but connection test failed')
        print('   Check your credentials and try again')
        return 1


if __name__ == '__main__':
    sys.exit(main())
