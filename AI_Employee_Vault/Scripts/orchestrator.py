"""
Orchestrator Module

Main coordination script for the AI Employee system.
Manages watchers, triggers Claude Code processing, and updates the dashboard.

Bronze Tier: Basic orchestration with file-based task management.
"""

import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import re


@dataclass
class TaskStats:
    """Statistics about tasks in the vault."""
    inbox_count: int = 0
    needs_action_count: int = 0
    pending_approval_count: int = 0
    done_today: int = 0
    done_total: int = 0


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Responsibilities:
    - Monitor vault folders for changes
    - Trigger Claude Code processing when items need attention
    - Update Dashboard.md with current status
    - Log all orchestration actions
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the Orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path).resolve()
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.logs = self.vault_path / 'Logs'
        self.scripts = self.vault_path / 'Scripts'
        
        # Ensure directories exist
        for directory in [self.inbox, self.needs_action, self.done, 
                          self.pending_approval, self.approved, self.logs, self.scripts]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info(f'Orchestrator initialized')
        self.logger.info(f'Vault: {self.vault_path}')
    
    def _setup_logging(self):
        """Configure logging."""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y%m%d")}.log'
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_stats(self) -> TaskStats:
        """
        Get current task statistics.
        
        Returns:
            TaskStats object with current counts
        """
        stats = TaskStats()
        
        try:
            # Count files in each folder
            stats.inbox_count = len(list(self.inbox.glob('*'))) if self.inbox.exists() else 0
            stats.needs_action_count = len([
                f for f in self.needs_action.glob('*.md') 
                if not f.name.endswith('.meta.md')
            ]) if self.needs_action.exists() else 0
            stats.pending_approval_count = len(list(self.pending_approval.glob('*.md'))) if self.pending_approval.exists() else 0
            stats.done_total = len(list(self.done.glob('*.md'))) if self.done.exists() else 0
            
            # Count today's completed
            today = datetime.now().strftime('%Y%m%d')
            stats.done_today = len([
                f for f in self.done.glob('*.md')
                if today in f.stem
            ])
            
        except Exception as e:
            self.logger.error(f'Error getting stats: {e}')
        
        return stats
    
    def update_dashboard(self):
        """
        Update the Dashboard.md with current status.
        """
        try:
            stats = self.get_stats()
            
            # Determine status indicators
            needs_action_status = '✅' if stats.needs_action_count == 0 else '⚠️'
            approvals_status = '✅' if stats.pending_approval_count == 0 else '🔴'
            
            # Read current dashboard
            if self.dashboard.exists():
                content = self.dashboard.read_text(encoding='utf-8')
            else:
                content = self._create_default_dashboard()
            
            # Update stats section
            content = self._update_section(
                content, 'Quick Stats',
                f'''| Metric | Value | Status |
|--------|-------|--------|
| Pending Tasks | {stats.needs_action_count} | {needs_action_status} |
| Items Needing Action | {stats.inbox_count} | {needs_action_status} |
| Pending Approvals | {stats.pending_approval_count} | {approvals_status} |
| Completed Today | {stats.done_today} | - |'''
            )
            
            # Update activity section
            recent_items = self._get_recent_items()
            activity_content = self._format_recent_activity(recent_items)
            content = self._update_section(content, 'Recent Activity', activity_content)
            
            # Update timestamp
            content = re.sub(
                r'last_updated: .*',
                f'last_updated: {datetime.now().isoformat()}',
                content
            )
            
            # Write updated dashboard
            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')
            
        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')
    
    def _create_default_dashboard(self) -> str:
        """Create default dashboard content."""
        return '''---
type: dashboard
last_updated: 2026-02-26T00:00:00Z
version: 0.1
---

# 🏢 AI Employee Dashboard

> **Status**: 🟢 Operational | **Mode**: Bronze Tier

---

## 📊 Quick Stats

| Metric | Value | Status |
|--------|-------|--------|
| Pending Tasks | 0 | ✅ |

---

## 📝 Recent Activity

*No recent activity*

---

*Last updated by: AI Employee v0.1 (Bronze)*
'''
    
    def _update_section(self, content: str, section_header: str, new_content: str) -> str:
        """
        Update a section in the markdown content.
        
        Args:
            content: Full markdown content
            section_header: Header to find
            new_content: New content for the section
            
        Returns:
            Updated markdown content
        """
        # Find section
        pattern = rf'(## {re.escape(section_header)}\n\n)(.*?)(\n---|\n## |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Replace section content
            start = match.start(2)
            end = match.end(2)
            content = content[:start] + new_content + content[end:]
        
        return content
    
    def _get_recent_items(self) -> List[Dict[str, Any]]:
        """Get recent items from Needs_Action folder."""
        items = []
        
        try:
            if self.needs_action.exists():
                files = sorted(
                    self.needs_action.glob('*.md'),
                    key=lambda f: f.stat().st_mtime,
                    reverse=True
                )[:5]  # Last 5 items
                
                for f in files:
                    items.append({
                        'name': f.name,
                        'time': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
                        'type': self._extract_type(f)
                    })
        except Exception as e:
            self.logger.error(f'Error getting recent items: {e}')
        
        return items
    
    def _extract_type(self, filepath: Path) -> str:
        """Extract type from markdown frontmatter."""
        try:
            content = filepath.read_text(encoding='utf-8')[:500]
            match = re.search(r'type:\s*(\w+)', content)
            return match.group(1) if match else 'unknown'
        except:
            return 'unknown'
    
    def _format_recent_activity(self, items: List[Dict[str, Any]]) -> str:
        """Format recent activity as markdown."""
        if not items:
            return '*No recent activity*'
        
        lines = ['| Time | Item | Type |', '|------|------|------|']
        for item in items:
            lines.append(f"| {item['time']} | {item['name']} | {item['type']} |")
        
        return '\n'.join(lines)
    
    def process_needs_action(self, dry_run: bool = False) -> int:
        """
        Process items in Needs_Action folder.
        
        In Bronze tier, this generates a prompt for Claude Code
        and logs what needs processing.
        
        Args:
            dry_run: If True, only log what would be done
            
        Returns:
            Number of items to process
        """
        items_to_process = []
        
        try:
            if not self.needs_action.exists():
                return 0
            
            # Find all action files (not meta files)
            for f in self.needs_action.glob('*.md'):
                if not f.name.endswith('.meta.md'):
                    items_to_process.append(f)
            
            if items_to_process:
                self.logger.info(f'Found {len(items_to_process)} items to process')

                # Create processing prompt for Qwen Code
                prompt = self._create_qwen_prompt(items_to_process)
                prompt_file = self.logs / f'qwen_prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
                prompt_file.write_text(prompt, encoding='utf-8')
                self.logger.info(f'Created Qwen prompt: {prompt_file}')
                
                if not dry_run:
                    self.logger.info('Run Qwen Code with the generated prompt')
            else:
                self.logger.debug('No items need processing')
                
        except Exception as e:
            self.logger.error(f'Error processing needs_action: {e}')
        
        return len(items_to_process)
    
    def _create_qwen_prompt(self, items: List[Path]) -> str:
        """
        Create a prompt for Qwen Code to process items.
        
        Args:
            items: List of action files to process
            
        Returns:
            Formatted prompt string
        """
        items_list = '\n'.join([f'- {f.name}' for f in items])
        
        return f'''# AI Employee Task Processing

## Items Requiring Action

The following files are in the `/Needs_Action` folder and need processing:

{items_list}

## Your Task

1. **Read** each file in `/Needs_Action`
2. **Analyze** what action is needed based on:
   - The file type and content
   - Rules in `/Company_Handbook.md`
   - Current goals in `/Business_Goals.md`
3. **Create a plan** for each item:
   - Write to `/Plans/` with checkboxes
   - Or update `Dashboard.md` with status
4. **Take action** based on the tier:
   - Bronze: Organize, categorize, and suggest next steps
   - Do NOT take external actions (email, payments) without approval
5. **Move completed items** to `/Done` after processing

## Rules

- Always be polite and professional
- Flag anything over $500 for approval
- When in doubt, create an approval request in `/Pending_Approval`
- Log all actions taken

## Output

After processing, update the Dashboard.md with:
- Summary of actions taken
- Any items requiring human approval
- Suggestions for improvement

---
*Generated by Orchestrator v0.1*
'''
    
    def run_cycle(self):
        """
        Run one complete orchestration cycle.
        
        1. Update dashboard stats
        2. Check for items needing action
        3. Generate Claude prompt if needed
        4. Log cycle completion
        """
        self.logger.info('Starting orchestration cycle')
        
        # Update dashboard
        self.update_dashboard()
        
        # Process needs action
        count = self.process_needs_action()
        
        self.logger.info(f'Cycle complete. {count} items need processing.')
    
    def start_watchers(self):
        """
        Start all watcher processes.
        
        Returns:
            List of started process objects
        """
        processes = []
        
        try:
            # Start filesystem watcher
            watcher_script = self.scripts / 'filesystem_watcher.py'
            if watcher_script.exists():
                cmd = ['python', str(watcher_script), '--vault', str(self.vault_path)]
                proc = subprocess.Popen(cmd)
                processes.append(proc)
                self.logger.info(f'Started filesystem watcher (PID: {proc.pid})')
            
        except Exception as e:
            self.logger.error(f'Error starting watchers: {e}')
        
        return processes


def main():
    """Run the Orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Run in watch mode (continuous)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Watch interval in seconds'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Dry run (no external actions)'
    )
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    orchestrator = Orchestrator(str(vault_path))
    
    if args.watch:
        import time
        orchestrator.logger.info(f'Starting watch mode (interval: {args.interval}s)')
        try:
            while True:
                orchestrator.run_cycle()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            orchestrator.logger.info('Watch mode stopped')
    else:
        # Single cycle
        orchestrator.run_cycle()


if __name__ == '__main__':
    main()
