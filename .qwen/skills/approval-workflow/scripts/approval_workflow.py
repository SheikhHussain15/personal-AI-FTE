"""
Approval Workflow

Human-in-the-loop approval system for sensitive AI actions.
Manages files in Pending_Approval/Approved/Rejected folders.

Silver Tier - Approval workflow management.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re
import shutil


class ApprovalWorkflow:
    """
    Manages approval workflow for sensitive actions.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize Approval Workflow.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        
        # Folders
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        
        for folder in [self.pending_folder, self.approved_folder, 
                       self.rejected_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('ApprovalWorkflow')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            
            # Also log to file
            file_handler = logging.FileHandler(
                self.logs_folder / f'approval_{datetime.now().strftime("%Y%m%d")}.log'
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)
    
    def create_approval_request(
        self,
        action_type: str,
        details: Dict,
        amount: Optional[float] = None,
        recipient: Optional[str] = None,
        expires_in_hours: int = 24,
        content: Optional[str] = None
    ) -> Path:
        """
        Create an approval request file.
        
        Args:
            action_type: Type of action (email_send, payment, post, etc.)
            details: Action details
            amount: Amount if financial
            recipient: Recipient if applicable
            expires_in_hours: Hours until expiration
            content: Additional content/body
            
        Returns:
            Path to created file
        """
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_action = self._safe_filename(action_type)
        safe_recipient = self._safe_filename(recipient or 'unknown')[:20]
        filename = f'APPROVAL_{safe_action}_{safe_recipient}_{timestamp}.md'
        filepath = self.pending_folder / filename
        
        # Calculate expiry
        from datetime import timedelta
        expires = datetime.now() + timedelta(hours=expires_in_hours)
        
        # Create content
        md_content = f"""---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {expires.isoformat()}
status: pending
amount: {amount if amount else 'N/A'}
recipient: {recipient if recipient else 'N/A'}
---

# Approval Required: {self._format_action_name(action_type)}

## Details

| Field | Value |
|-------|-------|
| **Action** | {self._format_action_name(action_type)} |
| **Created** | {datetime.now().strftime('%Y-%m-%d %H:%M')} |
| **Expires** | {expires.strftime('%Y-%m-%d %H:%M')} ({expires_in_hours} hours) |
| **Amount** | ${amount if amount else 'N/A'} |
| **Recipient** | {recipient if recipient else 'N/A'} |

## Content

{content if content else '*No additional content*'}

## Details JSON

```json
{self._format_details(details)}
```

## Instructions

### To Approve
1. Review the details above carefully
2. Move this file to `/Approved` folder
3. The AI Employee will execute the action

### To Reject
1. Add reason in the Notes section below
2. Move this file to `/Rejected` folder

## Notes

*Add comments or feedback here*

---
*Created by Approval Workflow v0.2 (Silver Tier)*
"""
        
        filepath.write_text(md_content, encoding='utf-8')
        self.logger.info(f'Approval request created: {filepath}')
        return filepath
    
    def check_pending(self) -> List[Dict]:
        """
        Check pending approvals.
        
        Returns:
            List of pending approval info
        """
        pending = []
        
        for f in self.pending_folder.glob('*.md'):
            info = self._parse_approval_file(f)
            if info:
                # Check if expired
                if info.get('expires') and datetime.fromisoformat(info['expires']) < datetime.now():
                    info['expired'] = True
                    self.logger.warning(f'Approval expired: {f.name}')
                else:
                    info['expired'] = False
                pending.append(info)
        
        return pending
    
    def process_approved(self) -> List[Dict]:
        """
        Process approved actions.
        
        Returns:
            List of processed actions
        """
        processed = []
        
        for f in self.approved_folder.glob('*.md'):
            info = self._parse_approval_file(f)
            if info:
                info['path'] = str(f)
                processed.append(info)
                
                # Log processing
                self.logger.info(f'Processing approved: {f.name} (Action: {info.get("action")})')
        
        return processed
    
    def reject_request(self, filepath: Path, reason: str = '') -> bool:
        """
        Reject an approval request.
        
        Args:
            filepath: Path to approval file
            reason: Reason for rejection
            
        Returns:
            True if successful
        """
        if not filepath.exists():
            return False
        
        # Add rejection reason
        content = filepath.read_text(encoding='utf-8')
        content = content.replace(
            'status: pending',
            f'status: rejected\nrejected_reason: {reason}'
        )
        content = content.replace(
            '*Add comments or feedback here*',
            f'*Add comments or feedback here*\n\n**REJECTED:** {reason}"
        )
        
        # Move to rejected folder
        self.rejected_folder.mkdir(parents=True, exist_ok=True)
        dest = self.rejected_folder / filepath.name
        filepath.write_text(content, encoding='utf-8')
        shutil.move(str(filepath), str(dest))
        
        self.logger.info(f'Rejection recorded: {filepath.name} - {reason}')
        return True
    
    def _parse_approval_file(self, filepath: Path) -> Optional[Dict]:
        """Parse approval file frontmatter."""
        content = filepath.read_text(encoding='utf-8')
        
        # Extract frontmatter
        match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        frontmatter = match.group(1)
        
        return {
            'file': filepath.name,
            'type': self._extract_field(frontmatter, 'type'),
            'action': self._extract_field(frontmatter, 'action'),
            'status': self._extract_field(frontmatter, 'status'),
            'created': self._extract_field(frontmatter, 'created'),
            'expires': self._extract_field(frontmatter, 'expires'),
            'amount': self._extract_field(frontmatter, 'amount'),
            'recipient': self._extract_field(frontmatter, 'recipient'),
        }
    
    def _extract_field(self, frontmatter: str, field: str) -> str:
        """Extract field from frontmatter."""
        match = re.search(rf'{field}:\s*(.+)', frontmatter)
        return match.group(1).strip() if match else ''
    
    def _format_action_name(self, action: str) -> str:
        """Format action name for display."""
        return action.replace('_', ' ').title()
    
    def _format_details(self, details: Dict) -> str:
        """Format details as JSON string."""
        import json
        return json.dumps(details, indent=2)
    
    def _safe_filename(self, text: str, max_length: int = 30) -> str:
        """Convert text to safe filename."""
        if not text:
            return 'unknown'
        invalid = '<>:"/\\|？*'
        for char in invalid:
            text = text.replace(char, '_')
        if len(text) > max_length:
            text = text[:max_length]
        return text.strip()


def main():
    """Approval Workflow CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Approval Workflow for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create approval request')
    create_parser.add_argument('--action', '-a', type=str, required=True, help='Action type')
    create_parser.add_argument('--amount', type=float, help='Amount if financial')
    create_parser.add_argument('--recipient', '-r', type=str, help='Recipient')
    create_parser.add_argument('--content', '-c', type=str, help='Content/body')
    create_parser.add_argument('--expires', '-e', type=int, default=24, help='Expires in hours')
    
    # List command
    subparsers.add_parser('list', help='List pending approvals')
    
    # Process command
    subparsers.add_parser('process', help='Process approved actions')
    
    # Reject command
    reject_parser = subparsers.add_parser('reject', help='Reject approval')
    reject_parser.add_argument('--file', '-f', type=str, required=True, help='File to reject')
    reject_parser.add_argument('--reason', type=str, required=True, help='Rejection reason')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    workflow = ApprovalWorkflow(str(vault_path))
    
    if args.command == 'create':
        filepath = workflow.create_approval_request(
            action_type=args.action,
            details={'content': args.content},
            amount=args.amount,
            recipient=args.recipient,
            expires_in_hours=args.expires,
            content=args.content
        )
        print(f'Approval request created: {filepath}')
    
    elif args.command == 'list':
        pending = workflow.check_pending()
        if pending:
            print(f'\n{"File":<50} {"Action":<20} {"Expires":<20} {"Status":<10}')
            print('-' * 100)
            for p in pending:
                expires = p.get('expires', 'N/A')[:16] if p.get('expires') else 'N/A'
                status = 'EXPIRED' if p.get('expired') else p.get('status', 'pending')
                print(f'{p["file"]:<50} {p.get("action", "N/A"):<20} {expires:<20} {status:<10}')
        else:
            print('No pending approvals')
    
    elif args.command == 'process':
        approved = workflow.process_approved()
        if approved:
            print(f'\nApproved actions ready for processing:')
            for a in approved:
                print(f'  - {a["file"]} ({a.get("action", "unknown")})')
        else:
            print('No approved actions pending')
    
    elif args.command == 'reject':
        filepath = Path(args.file)
        if workflow.reject_request(filepath, args.reason):
            print(f'Rejected: {filepath.name}')
        else:
            print(f'Failed to reject: {filepath}')
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
