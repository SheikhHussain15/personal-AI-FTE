#!/usr/bin/env python3
"""
Generate Facebook OAuth URL with BASIC permissions (no app review required).
"""

import os
import sys
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# Load .env.facebook
project_root = Path(__file__).parent.parent.parent.parent
env_file = project_root / '.env.facebook'

if env_file.exists():
    load_dotenv(str(env_file))

APP_ID = os.getenv('META_APP_ID', '')

print('=' * 70)
print('  FACEBOOK OAUTH URL - BASIC PERMISSIONS')
print('  (No App Review Required)')
print('=' * 70)

# Basic permissions that don't require app review
permissions = [
    'public_profile',
    'email',
]

# Generate OAuth URL
oauth_url = (
    f'https://www.facebook.com/v19.0/dialog/oauth'
    f'?client_id={APP_ID}'
    f'&redirect_uri=https://localhost/'
    f'&scope={",".join(permissions)}'
    f'&response_type=token'
)

print(f'\nApp ID: {APP_ID}')
print(f'\nPermissions requested (basic, no review):')
for perm in permissions:
    print(f'  ✓ {perm}')

print('\n' + '-' * 70)
print('CLICK THIS URL:')
print('-' * 70)
print(oauth_url)
print('-' * 70)

# Try to open browser
try:
    webbrowser.open(oauth_url)
    print('\n[Opened in browser]')
except Exception:
    pass

print('\n\n' + '=' * 70)
print('  IMPORTANT: FOR POSTING TO FACEBOOK PAGES')
print('=' * 70)
print('''
The basic permissions above only allow reading your public profile.

TO POST TO FACEBOOK PAGES, you need to use Graph API Explorer:

1. Go to: https://developers.facebook.com/tools/explorer/

2. Select your app: 4389496281335954

3. Click "Generate Access Token" button

4. In the permissions dialog, select:
   ✓ pages_read_engagement
   ✓ pages_manage_posts  
   ✓ pages_messaging

5. Click "Continue" → "Allow"

6. Copy the generated token

7. Update .env.facebook:
   META_ACCESS_TOKEN=YOUR_TOKEN_HERE

8. Test posting:
   python facebook_poster.py --vault ../../../AI_Employee_Vault --direct --message "Test"
''')
print('\n')
