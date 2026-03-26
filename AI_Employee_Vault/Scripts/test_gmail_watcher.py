"""
Test Gmail Watcher Connection

Verifies Gmail API connection and checks for emails.
"""

import sys
from pathlib import Path

# Add Scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from gmail_watcher import GmailWatcher

print("=" * 60)
print("GMAIL WATCHER - CONNECTION TEST")
print("=" * 60)
print()

vault_path = Path(__file__).parent.parent.resolve()
token_path = vault_path / 'Scripts' / 'token.json'

print(f"Vault Path: {vault_path}")
print(f"Token Path: {token_path}")
print(f"Token Exists: {token_path.exists()}")
print()

try:
    print("Initializing Gmail Watcher...")
    watcher = GmailWatcher(str(vault_path))
    
    print("[OK] Gmail Watcher initialized successfully!")
    print()
    
    print("Checking for emails...")
    emails = watcher.check_for_updates()
    
    print(f"[OK] Found {len(emails)} unread, important email(s)")
    print()
    
    if emails:
        print("Email Summary:")
        print("-" * 60)
        for email in emails:
            headers = email.get('headers', {})
            print(f"From: {headers.get('From', 'Unknown')}")
            print(f"Subject: {headers.get('Subject', 'No Subject')}")
            print(f"Date: {headers.get('Date', 'Unknown')}")
            print(f"Snippet: {email.get('snippet', '')[:100]}...")
            print("-" * 60)
    else:
        print("No new unread important emails found.")
        print("(This is normal if all emails have been read)")
    
    print()
    print("=" * 60)
    print("TEST PASSED - Gmail Watcher is working correctly!")
    print("=" * 60)
    
except Exception as e:
    print(f"[FAIL] TEST FAILED: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
