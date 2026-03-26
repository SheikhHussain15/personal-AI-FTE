#!/usr/bin/env python3
"""
Ralph Wiggum Persistence Loop

Keeps AI agent iterating until tasks are complete.
Implements Stop hook pattern for autonomous multi-step execution.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class RalphWiggumLoop:
    """Ralph Wiggum persistence loop controller."""
    
    def __init__(
        self,
        vault_path: str,
        task: str,
        max_iterations: int = 10,
        completion_promise: Optional[str] = None,
        completion_file_movement: bool = False,
        source_folder: str = 'Needs_Action',
        target_folder: str = 'Done',
        timeout_minutes: int = 60,
        output_log: Optional[str] = None,
    ):
        """
        Initialize Ralph Wiggum Loop.
        
        Args:
            vault_path: Path to Obsidian vault
            task: Task description for AI
            max_iterations: Maximum loop iterations
            completion_promise: Promise string to detect completion
            completion_file_movement: Use file movement for completion detection
            source_folder: Source folder for file movement
            target_folder: Target folder for file movement
            timeout_minutes: Timeout in minutes
            output_log: Log file path
        """
        load_dotenv()
        
        self.vault_path = Path(vault_path).resolve()
        self.task = task
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise
        self.completion_file_movement = completion_file_movement
        self.source_folder = self.vault_path / source_folder
        self.target_folder = self.vault_path / target_folder
        self.timeout = timedelta(minutes=timeout_minutes)
        self.output_log = Path(output_log) if output_log else None
        
        # State
        self.state_file = self.vault_path / 'Scripts' / 'ralph_state.json'
        self.iteration = 0
        self.start_time = datetime.now()
        self.previous_outputs: List[str] = []
        
        # Ensure folders exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load previous state if exists
        self._load_state()
    
    def _load_state(self):
        """Load previous state if exists."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.iteration = state.get('iteration', 0)
                    self.previous_outputs = state.get('previous_outputs', [])
                    logger.info(f'Loaded state: iteration {self.iteration}')
            except Exception as e:
                logger.warning(f'Failed to load state: {e}')
    
    def _save_state(self):
        """Save current state."""
        state = {
            'task': self.task,
            'iteration': self.iteration,
            'max_iterations': self.max_iterations,
            'start_time': self.start_time.isoformat(),
            'previous_outputs': self.previous_outputs[-5:],  # Keep last 5
            'status': 'in_progress',
            'updated': datetime.now().isoformat(),
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _log(self, message: str):
        """Log message to console and file."""
        logger.info(message)
        
        if self.output_log:
            with open(self.output_log, 'a') as f:
                f.write(f'[{datetime.now().isoformat()}] {message}\n')
    
    def _is_task_complete(self, ai_output: str) -> Tuple[bool, str]:
        """
        Check if task is complete.
        
        Args:
            ai_output: AI's output text
            
        Returns:
            (is_complete, reason)
        """
        # Check completion promise
        if self.completion_promise and self.completion_promise in ai_output:
            return True, f'Completion promise detected: {self.completion_promise}'
        
        # Check file movement
        if self.completion_file_movement:
            if self.source_folder.exists():
                files = list(self.source_folder.glob('*.md'))
                if len(files) == 0:
                    return True, 'All files moved from source folder'
        
        # Check for explicit completion markers in output
        completion_markers = [
            'task is complete',
            'all done',
            'finished processing',
            'no more files',
            'nothing left to process',
        ]
        
        output_lower = ai_output.lower()
        for marker in completion_markers:
            if marker in output_lower:
                return True, f'Completion marker detected: {marker}'
        
        return False, 'Task still in progress'
    
    def _run_ai_agent(self, prompt: str) -> str:
        """
        Run AI agent with prompt.
        
        Args:
            prompt: Prompt for AI
            
        Returns:
            AI output
        """
        # For Qwen Code, we would use subprocess or API
        # This is a simplified implementation
        
        self._log(f'Running AI agent with prompt: {prompt[:100]}...')
        
        # In a real implementation, this would:
        # 1. Call Qwen Code API or subprocess
        # 2. Capture output
        # 3. Return output
        
        # For now, simulate with a placeholder
        # In production, replace with actual Qwen Code integration
        
        try:
            # Example: Call Qwen Code via subprocess
            # result = subprocess.run(
            #     ['qwen', '--prompt', prompt],
            #     capture_output=True,
            #     text=True,
            #     timeout=300,
            # )
            # return result.stdout
            
            # Placeholder for demonstration
            self._log('AI agent processing... (placeholder - integrate with Qwen Code)')
            time.sleep(2)  # Simulate processing
            
            return f'Processed iteration {self.iteration}. Task in progress...'
            
        except subprocess.TimeoutExpired:
            self._log('AI agent timed out')
            return 'Error: AI agent timed out'
        except Exception as e:
            self._log(f'AI agent error: {e}')
            return f'Error: {e}'
    
    def run(self) -> bool:
        """
        Run the Ralph Wiggum loop.
        
        Returns:
            True if task completed successfully
        """
        self._log(f'\n🔄 Starting Ralph Wiggum Persistence Loop')
        self._log(f'   Task: {self.task}')
        self._log(f'   Max iterations: {self.max_iterations}')
        self._log(f'   Vault: {self.vault_path}')
        self._log(f'   Timeout: {self.timeout}')
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            
            # Check timeout
            elapsed = datetime.now() - self.start_time
            if elapsed > self.timeout:
                self._log(f'❌ Timeout after {elapsed}')
                self._save_state()
                return False
            
            self._log(f'\n--- Iteration {self.iteration}/{self.max_iterations} ---')
            
            # Build prompt
            prompt = self._build_prompt()
            
            # Run AI agent
            output = self._run_ai_agent(prompt)
            self.previous_outputs.append(output)
            
            # Check completion
            is_complete, reason = self._is_task_complete(output)
            
            if is_complete:
                self._log(f'✅ Task complete: {reason}')
                self._log(f'\n🎉 Ralph Wiggum Loop finished successfully!')
                self._log(f'   Total iterations: {self.iteration}')
                self._log(f'   Total time: {datetime.now() - self.start_time}')
                
                # Clean up state file
                if self.state_file.exists():
                    self.state_file.unlink()
                
                return True
            
            self._log(f'   Continuing: {reason}')
            self._save_state()
            
            # Small delay between iterations
            time.sleep(1)
        
        self._log(f'\n❌ Max iterations ({self.max_iterations}) reached')
        self._log(f'   Task may not be complete')
        self._save_state()
        
        return False
    
    def _build_prompt(self) -> str:
        """Build prompt for AI agent."""
        prompt = f'''Task: {self.task}

This is iteration {self.iteration} of {self.max_iterations}.

Instructions:
1. Work on the task systematically
2. When complete, include "{self.completion_promise or 'TASK_COMPLETE'}" in your output
3. If processing files, move them to /Done/ folder when complete
4. Report progress clearly

Previous iterations: {len(self.previous_outputs)}
'''
        
        if self.previous_outputs:
            prompt += f'\nLast output summary: {self.previous_outputs[-1][:200]}...\n'
        
        return prompt


def parse_args():
    parser = argparse.ArgumentParser(description='Ralph Wiggum Persistence Loop')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--max-iterations', type=int, default=10, help='Max iterations')
    parser.add_argument('--completion-promise', help='Completion promise string')
    parser.add_argument('--completion-file-movement', action='store_true',
                       help='Use file movement for completion detection')
    parser.add_argument('--source-folder', default='Needs_Action', help='Source folder')
    parser.add_argument('--target-folder', default='Done', help='Target folder')
    parser.add_argument('--timeout-minutes', type=int, default=60, help='Timeout in minutes')
    parser.add_argument('--output-log', help='Output log file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen')
    return parser.parse_args()


def main():
    args = parse_args()
    
    if args.dry_run:
        print('Ralph Wiggum Loop - Dry Run')
        print('=' * 50)
        print(f'Vault: {args.vault}')
        print(f'Task: {args.task}')
        print(f'Max iterations: {args.max_iterations}')
        print(f'Completion detection:')
        if args.completion_promise:
            print(f'  - Promise string: {args.completion_promise}')
        if args.completion_file_movement:
            print(f'  - File movement: {args.source_folder} → {args.target_folder}')
        print(f'Timeout: {args.timeout_minutes} minutes')
        return 0
    
    loop = RalphWiggumLoop(
        vault_path=args.vault,
        task=args.task,
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise,
        completion_file_movement=args.completion_file_movement,
        source_folder=args.source_folder,
        target_folder=args.target_folder,
        timeout_minutes=args.timeout_minutes,
        output_log=args.output_log,
    )
    
    success = loop.run()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
