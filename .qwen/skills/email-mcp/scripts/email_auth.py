"""
Email Authentication Script

Authenticates with Gmail API including send permissions.
Creates token.json for Email MCP Server.

Silver Tier - Requires Gmail API credentials.
"""

import os
import pickle
import logging
from pathlib import Path
from datetime import datetime

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("Gmail API libraries not installed.")
    print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    import sys
    sys.exit(1)


def authenticate_email(vault_path: str, credentials_path: str = None):
    """
    Authenticate with Gmail API including send permissions.
    
    Args:
        vault_path: Path to Obsidian vault
        credentials_path: Path to credentials.json
    """
    vault = Path(vault_path)
    token_path = vault / 'Scripts' / 'token.json'
    
    # Find credentials
    if credentials_path:
        cred_path = Path(credentials_path)
    else:
        # Try default locations
        default_paths = [
            vault / 'Scripts' / 'gmail_credentials.json',
            vault.parent / 'credentials.json',
            Path('credentials.json')
        ]
        cred_path = None
        for p in default_paths:
            if p.exists():
                cred_path = p
                break
    
    if not cred_path or not cred_path.exists():
        print(f"ERROR: Gmail credentials not found!")
        print(f"Searched:")
        for p in default_paths:
            print(f"  - {p}")
        print()
        print("Please place credentials.json in one of these locations")
        print("or specify with --credentials flag")
        return False
    
    # Gmail API scopes - INCLUDES SEND PERMISSION
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose'
    ]
    
    print("=" * 60)
    print("GMAIL EMAIL AUTHENTICATION")
    print("=" * 60)
    print()
    print(f"Credentials: {cred_path}")
    print(f"Token will be saved to: {token_path}")
    print()
    print("Permissions requested:")
    print("  - Send emails")
    print("  - Read emails")
    print("  - Create drafts")
    print("  - Compose messages")
    print()
    print("IMPORTANT: This grants send access. Keep token.json secure!")
    print()
    
    try:
        creds = None
        
        # Load existing token
        if token_path.exists():
            print("Loading existing token...")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            if creds and creds.valid:
                print("✓ Existing token is valid")
            elif creds and creds.expired and creds.refresh_token:
                print("Refreshing expired token...")
                creds.refresh(Request())
                print("✓ Token refreshed")
            else:
                print("Token invalid, will authenticate fresh")
                creds = None
        
        # Authenticate if needed
        if not creds:
            print()
            print("Starting authentication flow...")
            print("1. Browser will open automatically")
            print("2. Login to Gmail")
            print("3. Grant permissions")
            print("4. Browser will redirect to localhost")
            print()
            print("Opening browser in 3 seconds...")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(cred_path), SCOPES
            )
            creds = flow.run_local_server(port=0, open_browser=True)
            
            print("Authentication successful!")
        
        # Save token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
        
        print()
        print("=" * 60)
        print("AUTHENTICATION COMPLETE!")
        print("=" * 60)
        print()
        print(f"Token saved to: {token_path}")
        print()
        print("Next steps:")
        print("1. Start Email MCP Server:")
        print(f"   python .qwen/skills/email-mcp/scripts/email_mcp_server.py --vault ../AI_Employee_Vault --port 8809")
        print()
        print("2. Configure in Qwen Code MCP settings")
        print()
        print("3. Test sending emails:")
        print("   python .qwen/skills/email-mcp/scripts/mcp_client.py call -u http://localhost:8809 -t email_send -p '{\"to\": \"test@example.com\", \"subject\": \"Test\", \"body\": \"Hello\"}'")
        print()
        
        return True
        
    except Exception as e:
        print()
        print(f"ERROR: Authentication failed: {e}")
        print()
        print("Troubleshooting:")
        print("  - Check credentials.json is valid")
        print("  - Ensure Gmail API is enabled in Google Cloud Console")
        print("  - Try deleting token.json and re-authenticating")
        return False


def main():
    """Run email authentication."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Email Authentication for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--credentials', '-c',
        type=str,
        default=None,
        help='Path to credentials.json'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    success = authenticate_email(str(vault_path), args.credentials)
    
    if success:
        print("Email authentication complete!")
    else:
        print("Email authentication failed!")
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
