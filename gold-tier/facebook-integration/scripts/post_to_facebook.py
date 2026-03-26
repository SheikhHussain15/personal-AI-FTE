#!/usr/bin/env python3
"""
Post to Facebook Page - Test Script
"""

import io
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load .env.facebook
project_root = Path(__file__).parent.parent.parent.parent
env_file = project_root / '.env.facebook'

if env_file.exists():
    load_dotenv(str(env_file))

user_token = os.getenv('META_ACCESS_TOKEN', '')
page_id = os.getenv('META_PAGE_ID', '')

print('=' * 70)
print('  FACEBOOK POST TEST')
print('=' * 70)

# Step 1: Get Page Access Token
print(f'\nStep 1: Getting Page Access Token for Page ID: {page_id}')
r = requests.get(
    f'https://graph.facebook.com/v19.0/{page_id}',
    params={'fields': 'access_token,name', 'access_token': user_token}
)
result = r.json()

if 'error' in result:
    print(f"Error getting page token: {result['error']}")
    sys.exit(1)

page_name = result.get('name', 'Unknown')
page_token = result.get('access_token', '')

print(f'Page Name: {page_name}')
print(f'Page Token: {page_token[:30]}...')

if not page_token:
    print('❌ Failed to get page access token')
    sys.exit(1)

print('✅ Page access token obtained!')

# Step 2: Post to Page
print('\nStep 2: Posting to Facebook Page...')
message = '🤖 AI Employee Test Post - Facebook Gold Tier integration is working!'

r = requests.post(
    f'https://graph.facebook.com/v19.0/{page_id}/feed',
    data={
        'message': message,
        'access_token': page_token
    }
)

post_result = r.json()

print('\n' + '=' * 70)
print('  RESULT')
print('=' * 70)

if 'id' in post_result:
    print('✅ SUCCESS! Post created!')
    print(f'Post ID: {post_result["id"]}')
    print(f'View at: https://facebook.com/{post_result["id"]}')
    print(f'\nCheck your Facebook Page: "{page_name}"')
else:
    print('❌ Failed to post:')
    print(f'Error: {post_result.get("error", {}).get("message", "Unknown error")}')
    print(f'Error Code: {post_result.get("error", {}).get("code", "Unknown")}')
    print(f'Error Type: {post_result.get("error", {}).get("type", "Unknown")}')
    
    print('\nTroubleshooting:')
    print('1. Make sure you are an admin of the Facebook Page')
    print('2. Check if the page token has pages_manage_posts permission')
    print('3. Try generating a new page token from Graph API Explorer')

print()
