#!/usr/bin/env python3
"""
Quick Token Generator for Facebook Graph API

Generates a direct URL to get a new access token.
"""

import io
import os
import sys
import webbrowser
from pathlib import Path
from dotenv import load_dotenv, set_key

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load .env.facebook
project_root = Path(__file__).parent.parent.parent.parent
env_file = project_root / '.env.facebook'

if env_file.exists():
    load_dotenv(str(env_file))
else:
    print(f'ERROR: .env.facebook not found at {env_file}')
    sys.exit(1)

APP_ID = os.getenv('META_APP_ID', '')
APP_SECRET = os.getenv('META_APP_SECRET', '')

print('=' * 70)
print('  FACEBOOK TOKEN GENERATOR')
print('  AI Employee - Gold Tier')
print('=' * 70)

print(f'\nApp ID: {APP_ID}')

# Generate OAuth URL
oauth_url = (
    f'https://www.facebook.com/v19.0/dialog/oauth'
    f'?client_id={APP_ID}'
    f'&redirect_uri=https://localhost/'
    f'&scope=pages_read_engagement,pages_manage_posts,pages_messaging,'
    f'instagram_basic,instagram_content_publish,instagram_manage_comments'
    f'&response_type=token'
    f'&auth_type=reauthorize'
)

print('\n' + '-' * 70)
print('STEP 1: Open this URL in your browser:')
print('-' * 70)
print(oauth_url)
print('-' * 70)

# Try to open browser
try:
    webbrowser.open(oauth_url)
    print('\n[Opened in browser]')
except Exception:
    pass

print('\n\nSTEP 2: Authorize the app')
print('  1. Log in to Facebook (if not already logged in)')
print('  2. Click "Continue as [Your Name]"')
print('  3. Click "Allow" to grant permissions')
print('  4. You will be redirected to a URL like:')
print('     https://localhost/#access_token=EAAC...&expires_in=5184000')
print('\nSTEP 3: Copy the access_token value from the URL')
print('  (It starts with "EAAC" or "EAA" and is a long string)')

print('\n' + '-' * 70)
new_token = input('Paste your new access token here: ').strip()

if new_token:
    # Save to .env.facebook
    set_key(str(env_file), 'META_ACCESS_TOKEN', new_token)
    print(f'\n✅ Token saved to: {env_file}')
    
    # Test the new token
    print('\nTesting new token...')
    import requests
    
    r = requests.get(
        'https://graph.facebook.com/v19.0/me',
        params={'fields': 'id,name', 'access_token': new_token}
    )
    result = r.json()
    
    if 'id' in result:
        print(f'✅ Token valid! User: {result.get("name")} ({result.get("id")})')
        
        # Check for pages
        r = requests.get(
            'https://graph.facebook.com/v19.0/me/accounts',
            params={'fields': 'id,name,access_token,instagram_business_account', 'access_token': new_token}
        )
        pages = r.json()
        
        if 'data' in pages and pages['data']:
            print(f'\n✅ Found {len(pages["data"])} Facebook Page(s):')
            for i, page in enumerate(pages['data'], 1):
                ig_status = ' [Instagram Connected]' if page.get('instagram_business_account') else ''
                print(f'  {i}. {page.get("name")}{ig_status}')
                print(f'     Page ID: {page.get("id")}')
            
            # Auto-configure first page
            if len(pages['data']) == 1:
                selected = pages['data'][0]
                set_key(str(env_file), 'META_PAGE_ID', selected['id'])
                if selected.get('access_token'):
                    set_key(str(env_file), 'META_PAGE_TOKEN', selected['access_token'])
                if selected.get('instagram_business_account'):
                    set_key(str(env_file), 'META_INSTAGRAM_ID', selected['instagram_business_account']['id'])
                print(f'\n✅ Auto-configured Page: {selected["name"]} (ID: {selected["id"]})')
            else:
                choice = input('\nSelect page number to configure (or Enter to skip): ').strip()
                if choice.isdigit() and 1 <= int(choice) <= len(pages['data']):
                    selected = pages['data'][int(choice) - 1]
                    set_key(str(env_file), 'META_PAGE_ID', selected['id'])
                    if selected.get('access_token'):
                        set_key(str(env_file), 'META_PAGE_TOKEN', selected['access_token'])
                    if selected.get('instagram_business_account'):
                        set_key(str(env_file), 'META_INSTAGRAM_ID', selected['instagram_business_account']['id'])
                    print(f'✅ Configured Page: {selected["name"]}')
        else:
            print('\n⚠️  No Facebook Pages found.')
            print('Make sure you have a Facebook Page and granted page permissions.')
        
        print('\n' + '=' * 70)
        print('  SUCCESS! Facebook integration is ready.')
        print('=' * 70)
        print('\nNext steps:')
        print('1. Start Facebook Watcher:')
        print(f'   python gold-tier/facebook-integration/scripts/facebook_watcher.py --vault AI_Employee_Vault')
        print('\n2. Create a test post:')
        print(f'   python gold-tier/facebook-integration/scripts/facebook_poster.py --vault AI_Employee_Vault --request --message "Hello World!"')
        print()
    else:
        print(f'❌ Token invalid: {result.get("error", {}).get("message", "Unknown error")}')
        print('Please try again with a different token.')
else:
    print('\n❌ No token entered. Setup cancelled.')

print()
