#!/usr/bin/env python3
"""
Facebook Connection Test Script

Tests your Facebook Graph API credentials and helps you get Page ID.
"""

import io
import os
import sys
import requests
import webbrowser
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv, find_dotenv

# Load .env.facebook from project root
project_root = Path(__file__).parent.parent.parent.parent
env_file = project_root / '.env.facebook'

if env_file.exists():
    load_dotenv(str(env_file))
    print(f'Loaded: {env_file}')
else:
    print(f'ERROR: .env.facebook not found at {env_file}')
    sys.exit(1)

# Get credentials
APP_ID = os.getenv('META_APP_ID', '')
APP_SECRET = os.getenv('META_APP_SECRET', '')
ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', '')
PAGE_ID = os.getenv('META_PAGE_ID', '')

print('\n' + '=' * 60)
print('  FACEBOOK GRAPH API CONNECTION TEST')
print('  AI Employee - Gold Tier')
print('=' * 60)

print('\n📋 Current Configuration:')
print('-' * 60)
print(f'App ID: {APP_ID[:10]}...{APP_ID[-5:] if len(APP_ID) > 15 else APP_ID}')
print(f'App Secret: {"*" * 10}...{APP_SECRET[-5:] if len(APP_SECRET) > 15 else APP_SECRET}')
print(f'Access Token: {ACCESS_TOKEN[:20]}...{ACCESS_TOKEN[-5:] if len(ACCESS_TOKEN) > 25 else ACCESS_TOKEN}')
print(f'Page ID: {PAGE_ID}')

# Test 1: Token Info
print('\nTest 1: Token Validation')
print('-' * 60)
try:
    # Use access token directly for debug_token
    r = requests.get(
        'https://graph.facebook.com/v19.0/debug_token',
        params={'input_token': ACCESS_TOKEN, 'access_token': ACCESS_TOKEN}
    )
    result = r.json()
    
    if 'data' in result:
        data = result['data']
        is_valid = data.get('is_valid', False)
        expires_at = data.get('expires_at', 'Unknown')
        scopes = data.get('scopes', [])
        app_id = data.get('app_id', 'Unknown')
        
        print(f'Token Valid: {"YES" if is_valid else "NO"}')
        print(f'Expires At: {expires_at}')
        print(f'App ID: {app_id}')
        print(f'Scopes: {", ".join(scopes)}')
        
        if not is_valid:
            print('\nToken is invalid. Run facebook_auth.py to get a new token.')
            sys.exit(1)
    else:
        print(f'Error: {result}')
        # Continue anyway to test other endpoints
        
except Exception as e:
    print(f'Error: {e}')
    print('Continuing with other tests...')

# Test 2: User Info
print('\nTest 2: User Info')
print('-' * 60)
try:
    r = requests.get(
        'https://graph.facebook.com/v19.0/me',
        params={'fields': 'id,name,email', 'access_token': ACCESS_TOKEN}
    )
    user = r.json()
    
    if 'id' in user:
        print(f'User ID: {user["id"]}')
        print(f'Name: {user.get("name", "N/A")}')
        if 'email' in user:
            print(f'Email: {user["email"]}')
    else:
        print(f'Error: {user}')
        
except Exception as e:
    print(f'Error: {e}')

# Test 3: Pages
print('\nTest 3: Facebook Pages')
print('-' * 60)
try:
    r = requests.get(
        'https://graph.facebook.com/v19.0/me/accounts',
        params={'fields': 'id,name,access_token,instagram_business_account', 'access_token': ACCESS_TOKEN}
    )
    pages = r.json()
    
    if 'data' in pages and pages['data']:
        print(f'Found {len(pages["data"])} page(s):\n')
        for i, page in enumerate(pages['data'], 1):
            ig_status = '[Instagram Connected]' if page.get('instagram_business_account') else ''
            print(f'{i}. {page.get("name")} {ig_status}')
            print(f'   Page ID: {page.get("id")}')
            if page.get('access_token'):
                print(f'   Access Token: {page.get("access_token", "")[:30]}...')
            print()
        
        print('ACTION REQUIRED:')
        print('Copy the Page ID from above and add it to your .env.facebook:')
        print('   META_PAGE_ID=YOUR_PAGE_ID_HERE')
        print()
        
        # Ask user to select a page
        if len(pages['data']) == 1:
            selected = pages['data'][0]
            print(f'\nAuto-selecting: {selected["name"]}')
            print(f'   Page ID: {selected["id"]}')
            
            # Update .env.facebook
            from dotenv import set_key
            set_key(str(env_file), 'META_PAGE_ID', selected['id'])
            if selected.get('access_token'):
                set_key(str(env_file), 'META_PAGE_TOKEN', selected['access_token'])
            if selected.get('instagram_business_account'):
                set_key(str(env_file), 'META_INSTAGRAM_ID', selected['instagram_business_account']['id'])
            
            print('   Updated .env.facebook automatically!')
        else:
            choice = input('\nSelect page number (or Enter to skip): ').strip()
            if choice.isdigit() and 1 <= int(choice) <= len(pages['data']):
                selected = pages['data'][int(choice) - 1]
                from dotenv import set_key
                set_key(str(env_file), 'META_PAGE_ID', selected['id'])
                if selected.get('access_token'):
                    set_key(str(env_file), 'META_PAGE_TOKEN', selected['access_token'])
                if selected.get('instagram_business_account'):
                    set_key(str(env_file), 'META_INSTAGRAM_ID', selected['instagram_business_account']['id'])
                print(f'Updated .env.facebook with page: {selected["name"]}')
    else:
        print('No pages found.')
        print('\nPossible reasons:')
        print('1. Your token doesn\'t have page permissions')
        print('2. You don\'t manage any Facebook Pages')
        print('\nTo get page permissions:')
        print('1. Go to: https://developers.facebook.com/tools/explorer/')
        print('2. Select your app')
        print('3. Click "Generate Access Token"')
        print('4. Add permissions: pages_read_engagement, pages_manage_posts')
        print('5. Run facebook_auth.py again')
        
except Exception as e:
    print(f'Error: {e}')

# Test 4: Test with Page ID if configured
if PAGE_ID and PAGE_ID != 'your_page_id_here':
    print('\nTest 4: Page Info (using configured Page ID)')
    print('-' * 60)
    try:
        r = requests.get(
            f'https://graph.facebook.com/v19.0/{PAGE_ID}',
            params={'fields': 'id,name,about,website,followers_count', 'access_token': ACCESS_TOKEN}
        )
        page_info = r.json()
        
        if 'id' in page_info:
            print(f'Page Connected!')
            print(f'Name: {page_info.get("name")}')
            print(f'About: {page_info.get("about", "N/A")}')
            print(f'Website: {page_info.get("website", "N/A")}')
            print(f'Followers: {page_info.get("followers_count", "N/A")}')
        else:
            print(f'Error: {page_info}')
            
    except Exception as e:
        print(f'Error: {e}')
else:
    print('\nSkipped Test 4: Page ID not configured')

print('\n' + '=' * 60)
print('  TEST COMPLETE')
print('=' * 60)

# Next steps
print('\nNext Steps:')
if PAGE_ID == 'your_page_id_here' or not PAGE_ID:
    print('1. Run this script again after adding META_PAGE_ID to .env.facebook')
else:
    print('1. Facebook integration is ready!')
    print('2. Start the watcher:')
    print('   python gold-tier/facebook-integration/scripts/facebook_watcher.py --vault AI_Employee_Vault')

print('\n')
