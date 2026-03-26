"""
Simple Email Sender Test

Tests Gmail API sending directly without MCP server.
"""

import sys
import base64
from pathlib import Path
from email.mime.text import MIMEText

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("Gmail API libraries not installed.")
    sys.exit(1)


def send_email(vault_path: str, to: str, subject: str, body: str):
    """Send email via Gmail API."""
    
    vault = Path(vault_path)
    token_path = vault / 'Scripts' / 'token.json'
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose'
    ]
    
    print("=" * 60)
    print("EMAIL SENDER TEST")
    print("=" * 60)
    print()
    
    # Load token
    if not token_path.exists():
        print(f"ERROR: Token not found at {token_path}")
        print("Run email_auth.py first!")
        return False
    
    print(f"Loading token from: {token_path}")
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Check if valid
    if not creds.valid:
        print("ERROR: Token is invalid or expired")
        print("Run email_auth.py again!")
        return False
    
    print("Token loaded successfully!")
    print()
    
    # Connect to Gmail API
    print("Connecting to Gmail API...")
    service = build('gmail', 'v1', credentials=creds)
    print("Connected!")
    print()
    
    # Create message
    print(f"Creating email to: {to}")
    message = MIMEText(body)
    message['to'] = to
    message['from'] = 'me'
    message['subject'] = subject
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    # Send email
    print("Sending email...")
    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print()
        print("=" * 60)
        print("EMAIL SENT SUCCESSFULLY!")
        print("=" * 60)
        print()
        print(f"Message ID: {sent_message['id']}")
        print(f"Thread ID: {sent_message['threadId']}")
        print()
        print("Check your Gmail inbox!")
        return True
        
    except Exception as e:
        print()
        print(f"ERROR: Failed to send email: {e}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Email Sender Test')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--to', '-t',
        type=str,
        required=True,
        help='Recipient email address'
    )
    parser.add_argument(
        '--subject', '-s',
        type=str,
        default='Test Email',
        help='Email subject'
    )
    parser.add_argument(
        '--body', '-b',
        type=str,
        default='This is a test email from the AI Employee System.',
        help='Email body'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    success = send_email(
        str(vault_path),
        args.to,
        args.subject,
        args.body
    )
    
    if success:
        print("Email sending test PASSED!")
        sys.exit(0)
    else:
        print("Email sending test FAILED!")
        sys.exit(1)


if __name__ == '__main__':
    main()
