#!/usr/bin/env python3
"""
Test posting to Facebook personal profile (not Page).
This works without app review.
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

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN', '')
PAGE_ID = os.getenv('META_PAGE_ID', '')

print('=' * 70)
print('  FACEBOOK POST TEST')
print('=' * 70)

# First, get user ID
print('\nGetting user info...')
r = requests.get(
    'https://graph.facebook.com/v19.0/me',
    params={'fields': 'id,name', 'access_token': ACCESS_TOKEN}
)
user = r.json()

if 'id' not in user:
    print(f"Error: {user}")
    sys.exit(1)

print(f"User: {user['name']} ({user['id']})")

# Try posting to user's feed
print('\nAttempting to post to your personal profile...')
message = "🤖 Test post from AI Employee! This is an automated test."

r = requests.post(
    f'https://graph.facebook.com/v19.0/{user["id"]}/feed',
    data={
        'message': message,
        'access_token': ACCESS_TOKEN
    }
)

result = r.json()

if 'id' in result:
    print(f'\n✅ SUCCESS! Post created!')
    print(f'Post ID: {result["id"]}')
    print(f'View at: https://facebook.com/{result["id"]}')
else:
    print(f'\n❌ Failed to post:')
    print(f'Error: {result.get("error", {}).get("message", "Unknown error")}')
    
    print('\n' + '=' * 70)
    print('  ALTERNATIVE: Manual Posting Workflow')
    print('=' * 70)
    print('''
Since Facebook requires App Review for programmatic posting, you can:

1. USE META BUSINESS SUITE (Free):
   - Go to: https://business.facebook.com
   - Create posts manually
   - Schedule posts in advance

2. AI EMPLOYEE CAN STILL:
   - Read messages and comments (you have these permissions)
   - Monitor page insights
   - Send/receive messages via Messenger
   - Draft posts for manual publishing

3. FOR APP REVIEW:
   - Go to: https://developers.facebook.com
   - Select your app: 4389496281335954
   - Go to App Review → Start Review
   - Request: pages_manage_posts
   - Provide business justification
''')

print()
