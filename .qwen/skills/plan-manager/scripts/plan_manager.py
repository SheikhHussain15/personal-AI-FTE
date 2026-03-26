"""
Plan Manager

Create and manage Plan.md files for multi-step tasks.
Enables Qwen Code to handle complex multi-step workflows.

Silver Tier - Plan management utility.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re


class PlanManager:
    """
    Manages Plan.md files for multi-step tasks.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize Plan Manager.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.plans_folder = self.vault_path / 'Plans'
        self.plans_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logs_folder = self.vault_path / 'Logs'
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('PlanManager')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
    
    def create_plan(
        self,
        task: str,
        steps: List[str],
        priority: str = 'normal',
        objective: str = '',
        notes: str = ''
    ) -> Path:
        """
        Create a new plan.
        
        Args:
            task: Task name
            steps: List of step descriptions
            priority: Priority level (low, normal, high, urgent)
            objective: Objective description
            notes: Additional notes
            
        Returns:
            Path to created plan file
        """
        # Generate filename
        safe_task = self._safe_filename(task)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'PLAN_{safe_task}_{timestamp}.md'
        filepath = self.plans_folder / filename
        
        # Create steps markdown
        steps_md = '\n'.join([f'- [ ] {step.strip()}' for step in steps])
        
        # Create content
        content = f"""---
type: plan
task: {task}
created: {datetime.now().isoformat()}
status: in_progress
priority: {priority}
estimated_steps: {len(steps)}
completed_steps: 0
---

# Plan: {task}

## Objective

{objective if objective else f'Complete the task: {task}'}

## Steps

{steps_md}

## Progress

0% complete (0/{len(steps)} steps)

## Notes

{notes if notes else '*Add notes or context here*'}

## Blockers

None

## Related Files

*Link related files here*

---
*Created by Plan Manager v0.2 (Silver Tier)*
"""
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Plan created: {filepath}')
        return filepath
    
    def update_plan(
        self,
        plan_path: Path,
        complete_step: Optional[int] = None,
        add_step: Optional[str] = None,
        remove_step: Optional[int] = None,
        add_note: Optional[str] = None,
        set_status: Optional[str] = None
    ) -> bool:
        """
        Update an existing plan.
        
        Args:
            plan_path: Path to plan file
            complete_step: Step number to mark complete (1-indexed)
            add_step: New step to add
            remove_step: Step number to remove
            add_note: Note to add
            set_status: New status
            
        Returns:
            True if successful
        """
        if not plan_path.exists():
            self.logger.error(f'Plan not found: {plan_path}')
            return False
        
        content = plan_path.read_text(encoding='utf-8')
        
        # Parse current state
        lines = content.split('\n')
        new_lines = []
        in_steps = False
        step_count = 0
        completed_count = 0
        steps_modified = []
        
        for i, line in enumerate(lines):
            # Handle step completion
            if complete_step and line.strip().startswith('- [ ]') and in_steps:
                step_count += 1
                if step_count == complete_step:
                    line = line.replace('- [ ]', '- [x]')
                    self.logger.info(f'Marked step {complete_step} as complete')
            
            # Count steps
            if line.strip().startswith('- [x]'):
                completed_count += 1
            elif line.strip().startswith('- [ ]'):
                step_count += 1
            
            # Track if in steps section
            if line.strip() == '## Steps':
                in_steps = True
            elif line.startswith('##') and in_steps:
                in_steps = False
            
            new_lines.append(line)
        
        # Recalculate totals
        total_steps = sum(1 for l in new_lines if l.strip().startswith('- [ ]') or l.strip().startswith('- [x]'))
        completed = sum(1 for l in new_lines if l.strip().startswith('- [x]'))
        
        # Update progress section
        content = '\n'.join(new_lines)
        progress_pattern = r'(\d+)% complete \((\d+)/(\d+) steps\)'
        if total_steps > 0:
            percent = int(100 * completed / total_steps)
            content = re.sub(
                progress_pattern,
                f'{percent}% complete ({completed}/{total_steps} steps)',
                content
            )
        
        # Update status if completed
        if total_steps > 0 and completed == total_steps:
            content = re.sub(r'status: \w+', 'status: completed', content)
            content = re.sub(r'Progress:.*', f'{100}% complete ({completed}/{total_steps} steps)', content)
        
        # Add note if provided
        if add_note:
            content = content.replace(
                '*Add notes or context here*',
                f'*Add notes or context here*\n\n- {datetime.now().strftime("%Y-%m-%d")}: {add_note}'
            )
        
        # Set status if provided
        if set_status:
            content = re.sub(r'status: \w+', f'status: {set_status}', content)
        
        plan_path.write_text(content, encoding='utf-8')
        self.logger.info(f'Plan updated: {plan_path}')
        return True
    
    def get_plan_status(self, plan_path: Path) -> Optional[Dict]:
        """
        Get plan status.
        
        Args:
            plan_path: Path to plan file
            
        Returns:
            Dictionary with plan status
        """
        if not plan_path.exists():
            return None
        
        content = plan_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        frontmatter = match.group(1)
        
        # Parse fields
        status = {
            'path': str(plan_path),
            'task': self._extract_field(frontmatter, 'task'),
            'status': self._extract_field(frontmatter, 'status'),
            'priority': self._extract_field(frontmatter, 'priority'),
            'created': self._extract_field(frontmatter, 'created'),
        }
        
        # Count steps
        total = len(re.findall(r'- \[.\]', content))
        completed = len(re.findall(r'- \[x\]', content))
        status['total_steps'] = total
        status['completed_steps'] = completed
        status['progress'] = f'{int(100 * completed / total) if total > 0 else 0}%'
        
        return status
    
    def list_plans(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        List all plans.
        
        Args:
            status_filter: Filter by status (in_progress, completed, etc.)
            
        Returns:
            List of plan status dictionaries
        """
        plans = []
        
        for f in self.plans_folder.glob('*.md'):
            plan_status = self.get_plan_status(f)
            if plan_status:
                if status_filter is None or plan_status.get('status') == status_filter:
                    plans.append(plan_status)
        
        return plans
    
    def _extract_field(self, frontmatter: str, field: str) -> str:
        """Extract field from frontmatter."""
        match = re.search(rf'{field}:\s*(.+)', frontmatter)
        return match.group(1).strip() if match else ''
    
    def _safe_filename(self, text: str, max_length: int = 30) -> str:
        """Convert text to safe filename."""
        invalid = '<>:"/\\|？*'
        for char in invalid:
            text = text.replace(char, '_')
        
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()


def main():
    """Plan Manager CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plan Manager for AI Employee')
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new plan')
    create_parser.add_argument('--task', '-t', type=str, required=True, help='Task name')
    create_parser.add_argument('--steps', '-s', type=str, required=True, help='Comma-separated steps')
    create_parser.add_argument('--priority', '-p', type=str, default='normal', help='Priority level')
    create_parser.add_argument('--objective', '-o', type=str, default='', help='Objective')
    create_parser.add_argument('--notes', '-n', type=str, default='', help='Notes')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update plan')
    update_parser.add_argument('--plan', type=str, required=True, help='Plan file path')
    update_parser.add_argument('--complete-step', type=int, help='Step to complete')
    update_parser.add_argument('--add-note', type=str, help='Add note')
    update_parser.add_argument('--status', type=str, help='Set status')
    
    # List command
    subparsers.add_parser('list', help='List plans')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get plan status')
    status_parser.add_argument('--plan', type=str, required=True, help='Plan file path')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    manager = PlanManager(str(vault_path))
    
    if args.command == 'create':
        steps = [s.strip() for s in args.steps.split(',')]
        filepath = manager.create_plan(
            task=args.task,
            steps=steps,
            priority=args.priority,
            objective=args.objective,
            notes=args.notes
        )
        print(f'Plan created: {filepath}')
    
    elif args.command == 'update':
        plan_path = Path(args.plan)
        manager.update_plan(
            plan_path=plan_path,
            complete_step=args.complete_step,
            add_note=args.add_note,
            set_status=args.status
        )
        print(f'Plan updated: {plan_path}')
    
    elif args.command == 'list':
        plans = manager.list_plans()
        if plans:
            print(f'\n{"Task":<40} {"Status":<15} {"Progress":<15} {"Priority":<10}')
            print('-' * 80)
            for plan in plans:
                print(f'{plan["task"]:<40} {plan["status"]:<15} {plan["progress"]:<15} {plan["priority"]:<10}')
        else:
            print('No plans found')
    
    elif args.command == 'status':
        plan_path = Path(args.plan)
        status = manager.get_plan_status(plan_path)
        if status:
            print(f'\nPlan: {status["task"]}')
            print(f'Status: {status["status"]}')
            print(f'Priority: {status["priority"]}')
            print(f'Progress: {status["progress"]} ({status["completed_steps"]}/{status["total_steps"]} steps)')
        else:
            print(f'Plan not found: {plan_path}')
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
