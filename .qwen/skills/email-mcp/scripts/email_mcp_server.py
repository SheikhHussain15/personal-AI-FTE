"""
Email MCP Server

Sends emails via Gmail API using MCP (Model Context Protocol).
Provides tools for sending, drafting, and searching emails.

Silver Tier - Requires Gmail API with send permissions.
"""

import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from email.mime.text import MIMEText
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("Gmail API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class EmailMCPServer:
    """
    MCP Server for Gmail email operations.
    
    Exposes tools for:
    - email_send: Send email immediately
    - email_draft: Create draft without sending
    - email_search: Search Gmail messages
    """
    
    # Gmail API scopes - includes send permission
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose'
    ]
    
    def __init__(self, vault_path: str, token_path: str = None, port: int = 8809):
        """
        Initialize Email MCP Server.
        
        Args:
            vault_path: Path to Obsidian vault
            token_path: Path to Gmail token.json
            port: MCP server port (default: 8809)
        """
        if not EMAIL_AVAILABLE:
            raise ImportError("Gmail API libraries not installed")
        
        self.vault_path = Path(vault_path)
        self.token_path = Path(token_path) if token_path else self.vault_path / 'Scripts' / 'token.json'
        self.port = port
        self.service = None
        
        # Connect to Gmail
        self._connect()
        
        print(f'Email MCP Server initialized on port {port}')
    
    def _connect(self):
        """Authenticate and connect to Gmail API."""
        try:
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES
                )
            
            # Refresh or authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # For now, assume token exists with correct scope
                    # In production, would run OAuth flow here
                    raise FileNotFoundError(
                        f"Gmail token not found at {self.token_path}. "
                        "Run email_auth.py first to authenticate with send scope."
                    )
            
            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            print('Connected to Gmail API')
            
        except Exception as e:
            print(f'Gmail connection failed: {e}')
            raise
    
    def email_send(self, to: str, subject: str, body: str, cc: str = None) -> Dict[str, Any]:
        """
        Send an email immediately.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            cc: Optional CC email address
            
        Returns:
            Dict with status and message_id
        """
        try:
            if not self.service:
                self._connect()
            
            # Create message
            message = self._create_message(to, subject, body, cc)
            
            # Send email
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId'],
                'status': 'sent',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def email_draft(self, to: str, subject: str, body: str, cc: str = None) -> Dict[str, Any]:
        """
        Create a draft email without sending.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            cc: Optional CC email address
            
        Returns:
            Dict with draft_id and status
        """
        try:
            if not self.service:
                self._connect()
            
            # Create message
            message = self._create_message(to, subject, body, cc)
            
            # Create draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={
                    'message': message
                }
            ).execute()
            
            return {
                'success': True,
                'draft_id': draft['id'],
                'message_id': draft['message']['id'],
                'status': 'draft',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    def email_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search Gmail for messages.
        
        Args:
            query: Gmail search query (e.g., "is:unread from:client@example.com")
            max_results: Maximum number of results (default: 10)
            
        Returns:
            Dict with list of matching messages
        """
        try:
            if not self.service:
                self._connect()
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full details for each message
            email_list = []
            for msg in messages:
                msg_details = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg_details['payload']['headers']}
                email_list.append({
                    'id': msg['id'],
                    'thread_id': msg['threadId'],
                    'from': headers.get('From', 'Unknown'),
                    'to': headers.get('To', 'Unknown'),
                    'subject': headers.get('Subject', 'No Subject'),
                    'date': headers.get('Date', 'Unknown'),
                    'snippet': msg_details.get('snippet', '')
                })
            
            return {
                'success': True,
                'count': len(email_list),
                'messages': email_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'messages': []
            }
    
    def _create_message(self, to: str, subject: str, body: str, cc: str = None) -> Dict[str, Any]:
        """Create Gmail API message."""
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def handle_tool_call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP tool call.
        
        Args:
            tool_name: Name of tool to call
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        tools = {
            'email_send': self.email_send,
            'email_draft': self.email_draft,
            'email_search': self.email_search
        }
        
        if tool_name not in tools:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }
        
        return tools[tool_name](**params)


def main():
    """Run Email MCP Server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email MCP Server for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--token', '-t',
        type=str,
        default=None,
        help='Path to token.json'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8809,
        help='MCP server port (default: 8809)'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    server = EmailMCPServer(
        str(vault_path),
        token_path=args.token,
        port=args.port
    )
    
    print(f'Email MCP Server running on port {args.port}')
    print('Available tools: email_send, email_draft, email_search')
    print('Press Ctrl+C to stop')
    
    # Simple interactive loop for testing
    try:
        while True:
            # In production, this would be an MCP protocol server
            # For now, accept JSON commands via stdin
            try:
                line = input()
                if line.strip():
                    request = json.loads(line)
                    tool_name = request.get('tool')
                    params = request.get('params', {})
                    
                    result = server.handle_tool_call(tool_name, params)
                    print(json.dumps(result))
            except json.JSONDecodeError:
                print(json.dumps({'error': 'Invalid JSON'}))
            except KeyboardInterrupt:
                break
    except KeyboardInterrupt:
        pass
    finally:
        print('Email MCP Server stopped')


if __name__ == '__main__':
    main()
