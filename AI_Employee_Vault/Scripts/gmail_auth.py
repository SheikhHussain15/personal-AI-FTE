"""
Gmail Authentication Helper

Authenticate with Gmail API and save token for Gmail Watcher.
Run this script once to set up authentication.
"""

import os
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def authenticate_gmail(
    credentials_path: str,
    token_path: str,
    scopes: list = None
):
    """
    Authenticate with Gmail API.
    
    Args:
        credentials_path: Path to credentials.json from Google Cloud
        token_path: Path to save token.json
        scopes: Gmail API scopes
    """
    if scopes is None:
        scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    credentials_path = Path(credentials_path)
    token_path = Path(token_path)
    
    # Check credentials file
    if not credentials_path.exists():
        print(f"ERROR: Credentials file not found: {credentials_path}")
        print("\nTo get credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        return False
    
    creds = None
    
    # Load existing token
    if token_path.exists():
        print(f"Loading existing token from {token_path}")
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        except Exception as e:
            print(f"Error loading token: {e}")
            token_path.unlink()
    
    # Refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("Token refreshed successfully!")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            print("\nStarting Gmail authentication...")
            print("A browser window will open. Sign in with your Google account.")
            print("Grant permissions when prompted.\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), scopes
            )
            creds = flow.run_local_server(port=0)
            print("\nAuthentication successful!")
    
    # Save token
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())
    
    # Set secure permissions (Unix only)
    try:
        os.chmod(token_path, 0o600)
    except:
        pass  # Windows doesn't support chmod
    
    print(f"\nToken saved to: {token_path}")
    print("\nYou can now run gmail_watcher.py")
    print("Keep this token file secure - it provides access to your Gmail!")
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Authenticate with Gmail API for AI Employee'
    )
    parser.add_argument(
        '--credentials', '-c',
        type=str,
        default='credentials.json',
        help='Path to Gmail credentials.json from Google Cloud'
    )
    parser.add_argument(
        '--token', '-t',
        type=str,
        default=None,
        help='Path to save token.json (default: Scripts/token.json)'
    )
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    # Determine paths
    credentials_path = Path(args.credentials)
    token_path = Path(args.token) if args.token else vault_path / 'Scripts' / 'token.json'
    
    print("=" * 60)
    print("Gmail Authentication for AI Employee")
    print("=" * 60)
    print(f"\nCredentials: {credentials_path}")
    print(f"Token will be saved to: {token_path}")
    print()
    
    success = authenticate_gmail(str(credentials_path), str(token_path))
    
    if success:
        print("\n[SUCCESS] Gmail authentication complete!")
        print("\nNext steps:")
        print("1. Start Gmail Watcher:")
        print(f"   python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault {vault_path}")
        print("\n2. Check for new emails in Needs_Action folder")
    else:
        print("\n[FAILED] Authentication failed")
        print("Please check credentials and try again")


if __name__ == '__main__':
    main()
