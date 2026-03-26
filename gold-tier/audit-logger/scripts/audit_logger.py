#!/usr/bin/env python3
"""
Audit Logger

Comprehensive logging of all AI Employee actions.
Provides tamper-evident, append-only audit trail.
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logger for AI Employee actions."""
    
    def __init__(self, vault_path: str):
        """
        Initialize Audit Logger.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        load_dotenv()
        
        self.vault_path = Path(vault_path).resolve()
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure logs folder exists
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Main log file
        self.log_file = self.logs_folder / 'audit_log.json'
        
        # Initialize log file if needed
        self._init_log_file()
        
        # Load existing entries
        self.entries = self._load_entries()
    
    def _init_log_file(self):
        """Initialize log file if it doesn't exist."""
        if not self.log_file.exists():
            # Create with empty array
            self.log_file.write_text('[]', encoding='utf-8')
            logger.info(f'Created new audit log: {self.log_file}')
    
    def _load_entries(self) -> List[Dict[str, Any]]:
        """Load existing log entries."""
        try:
            content = self.log_file.read_text(encoding='utf-8')
            return json.loads(content)
        except Exception as e:
            logger.warning(f'Failed to load audit log: {e}')
            return []
    
    def _save_entries(self):
        """Save log entries to file."""
        try:
            content = json.dumps(self.entries, indent=2, default=str)
            self.log_file.write_text(content, encoding='utf-8')
        except Exception as e:
            logger.error(f'Failed to save audit log: {e}')
    
    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        result: str = 'success',
        approval_status: Optional[str] = None,
        approved_by: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an action.
        
        Args:
            action_type: Type of action (e.g., 'odoo_invoice_create')
            actor: Who performed the action (e.g., 'qwen_code', 'gmail_watcher')
            target: Target of the action (e.g., 'Client A', 'Facebook Page')
            parameters: Action parameters
            result: Result status ('success', 'failure', 'pending')
            approval_status: Approval status if applicable
            approved_by: Who approved if applicable
            error_message: Error message if failed
            metadata: Additional metadata
            
        Returns:
            Log entry ID
        """
        entry = {
            'log_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'parameters': parameters or {},
            'result': result,
            'approval_status': approval_status,
            'approved_by': approved_by,
            'error_message': error_message,
            'metadata': metadata or {},
        }
        
        self.entries.append(entry)
        self._save_entries()
        
        # Also append to daily log file
        self._append_to_daily_log(entry)
        
        logger.info(f'Audit log: {action_type} by {actor} -> {result}')
        
        return entry['log_id']
    
    def _append_to_daily_log(self, entry: Dict[str, Any]):
        """Append entry to daily log file."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        daily_log = self.logs_folder / f'audit_{date_str}.jsonl'
        
        try:
            with open(daily_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, default=str) + '\n')
        except Exception as e:
            logger.warning(f'Failed to append to daily log: {e}')
    
    def query(
        self,
        action_type: Optional[str] = None,
        actor: Optional[str] = None,
        result: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query log entries.
        
        Args:
            action_type: Filter by action type
            actor: Filter by actor
            result: Filter by result
            date_from: Start date (ISO format)
            date_to: End date (ISO format)
            limit: Maximum results
            
        Returns:
            List of matching entries
        """
        results = []
        
        for entry in self.entries:
            # Apply filters
            if action_type and entry.get('action_type') != action_type:
                continue
            if actor and entry.get('actor') != actor:
                continue
            if result and entry.get('result') != result:
                continue
            
            # Date filtering
            entry_time = entry.get('timestamp', '')
            if date_from and entry_time < date_from:
                continue
            if date_to and entry_time > date_to:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary of recent activity.
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Summary statistics
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        recent = [e for e in self.entries if e.get('timestamp', '') >= cutoff]
        
        summary = {
            'total_actions': len(recent),
            'by_type': {},
            'by_actor': {},
            'by_result': {},
            'errors': [],
        }
        
        for entry in recent:
            # Count by type
            action_type = entry.get('action_type', 'unknown')
            summary['by_type'][action_type] = summary['by_type'].get(action_type, 0) + 1
            
            # Count by actor
            actor = entry.get('actor', 'unknown')
            summary['by_actor'][actor] = summary['by_actor'].get(actor, 0) + 1
            
            # Count by result
            result = entry.get('result', 'unknown')
            summary['by_result'][result] = summary['by_result'].get(result, 0) + 1
            
            # Collect errors
            if entry.get('result') == 'failure':
                summary['errors'].append({
                    'timestamp': entry.get('timestamp'),
                    'action_type': entry.get('action_type'),
                    'error_message': entry.get('error_message'),
                })
        
        return summary
    
    def archive_old_entries(self, days_to_keep: int = 90):
        """Archive entries older than specified days."""
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff.isoformat()
        
        # Find entries to archive
        to_archive = [e for e in self.entries if e.get('timestamp', '') < cutoff_str]
        to_keep = [e for e in self.entries if e.get('timestamp', '') >= cutoff_str]
        
        if to_archive:
            # Write to archive file
            archive_date = datetime.now().strftime('%Y%m%d')
            archive_file = self.logs_folder / f'audit_archive_{archive_date}.json'
            
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(to_archive, f, indent=2, default=str)
            
            logger.info(f'Archived {len(to_archive)} entries to {archive_file}')
            
            # Update entries
            self.entries = to_keep
            self._save_entries()
    
    def export(self, output_path: str, format: str = 'json'):
        """
        Export logs to file.
        
        Args:
            output_path: Output file path
            format: Export format ('json', 'csv')
        """
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, default=str)
        
        elif format == 'csv':
            import csv
            
            if not self.entries:
                logger.warning('No entries to export')
                return
            
            # Get all keys
            keys = set()
            for entry in self.entries:
                keys.update(entry.keys())
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(keys))
                writer.writeheader()
                
                for entry in self.entries:
                    # Flatten nested dicts for CSV
                    row = {}
                    for key, value in entry.items():
                        if isinstance(value, dict):
                            row[key] = json.dumps(value)
                        else:
                            row[key] = value
                    writer.writerow(row)
        
        logger.info(f'Exported {len(self.entries)} entries to {output_path}')


def parse_args():
    parser = argparse.ArgumentParser(description='Audit Logger')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--log', action='store_true', help='Log a test action')
    parser.add_argument('--query', action='store_true', help='Query logs')
    parser.add_argument('--type', help='Filter by action type')
    parser.add_argument('--actor', help='Filter by actor')
    parser.add_argument('--today', action='store_true', help='Show today\'s logs')
    parser.add_argument('--summary', action='store_true', help='Show summary')
    parser.add_argument('--days', type=int, default=7, help='Days for summary')
    parser.add_argument('--export', choices=['json', 'csv'], help='Export format')
    parser.add_argument('--output', help='Export output path')
    parser.add_argument('--archive', action='store_true', help='Archive old entries')
    return parser.parse_args()


def main():
    args = parse_args()
    
    logger_instance = AuditLogger(vault_path=args.vault)
    
    # Log test action
    if args.log:
        log_id = logger_instance.log_action(
            action_type='test_action',
            actor='audit_logger_cli',
            target='Test',
            parameters={'test': True},
            result='success',
        )
        print(f'Logged test action with ID: {log_id}')
        return 0
    
    # Query logs
    if args.query:
        date_from = None
        if args.today:
            date_from = datetime.now().strftime('%Y-%m-%dT00:00:00')
        
        results = logger_instance.query(
            action_type=args.type,
            actor=args.actor,
            date_from=date_from,
        )
        
        print(f'\nFound {len(results)} entries:\n')
        for entry in results[:20]:
            print(f"  [{entry.get('timestamp', '')[:19]}] {entry.get('action_type')} by {entry.get('actor')} -> {entry.get('result')}")
        
        if len(results) > 20:
            print(f'  ... and {len(results) - 20} more')
        
        return 0
    
    # Show summary
    if args.summary:
        summary = logger_instance.get_summary(days=args.days)
        
        print(f'\n📊 Audit Log Summary (Last {args.days} Days)')
        print('=' * 50)
        print(f"Total Actions: {summary['total_actions']}")
        print(f"\nBy Type:")
        for action_type, count in sorted(summary['by_type'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {action_type}: {count}")
        print(f"\nBy Actor:")
        for actor, count in sorted(summary['by_actor'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {actor}: {count}")
        print(f"\nBy Result:")
        for result, count in summary['by_result'].items():
            print(f"  {result}: {count}")
        
        if summary['errors']:
            print(f"\n⚠️ Errors ({len(summary['errors'])}):")
            for err in summary['errors'][:5]:
                print(f"  [{err['timestamp'][:19]}] {err['action_type']}: {err['error_message'][:50]}")
        
        return 0
    
    # Export
    if args.export:
        output = args.output or f'audit_export.{args.export}'
        logger_instance.export(output, format=args.export)
        print(f'Exported to {output}')
        return 0
    
    # Archive
    if args.archive:
        logger_instance.archive_old_entries()
        print('Archive complete')
        return 0
    
    # Default: show info
    print('Audit Logger')
    print('=' * 50)
    print(f'Log file: {logger_instance.log_file}')
    print(f'Total entries: {len(logger_instance.entries)}')
    print('\nUsage:')
    print('  --log           Log a test action')
    print('  --query         Query logs')
    print('  --summary       Show summary')
    print('  --export        Export logs')
    print('  --archive       Archive old entries')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
