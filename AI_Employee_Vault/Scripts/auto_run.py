"""
AI Employee - Silver Tier Auto-Runner

Fully automated runner for Silver Tier.
Automatically:
- Creates LinkedIn posts
- Moves files through workflow
- Posts to LinkedIn
- Logs all actions

Usage:
    python auto_run.py --content "Your post content"
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import threading


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'auto_run_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger('AutoRun')


class AIEmployeeAutoRunner:
    """Fully automated AI Employee runner for Silver Tier."""
    
    def __init__(self, vault_path: str):
        """
        Initialize Auto Runner.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path).resolve()
        self.scripts_path = self.vault_path / 'Scripts'
        self.linkedin_poster = self.vault_path.parent / '.qwen' / 'skills' / 'linkedin-poster' / 'scripts' / 'linkedin_poster.py'
        
        logger.info(f'Vault: {self.vault_path}')
        logger.info('AI Employee Auto Runner initialized')
    
    def create_linkedin_post(self, content: str, category: str = 'business_update'):
        """
        Create LinkedIn post directly in Approved folder.
        
        Args:
            content: Post content
            category: Post category
        """
        logger.info(f'Creating LinkedIn post: {category}')
        
        cmd = [
            sys.executable,
            str(self.linkedin_poster),
            '--vault', str(self.vault_path),
            '--content', content
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            logger.info(f'Post created: {result.stdout}')
            if result.stderr:
                logger.warning(f'Stderr: {result.stderr}')
        except Exception as e:
            logger.error(f'Error creating post: {e}')
    
    def start_linkedin_watcher(self):
        """Start LinkedIn Watcher in background."""
        logger.info('Starting LinkedIn Watcher...')
        
        cmd = [
            sys.executable,
            str(self.scripts_path / 'linkedin_watcher.py'),
            '--vault', str(self.vault_path),
            '--interval', '30'
        ]
        
        # Start as background process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        logger.info(f'LinkedIn Watcher started (PID: {process.pid})')
        return process
    
    def start_all_watchers(self):
        """Start all Silver Tier watchers."""
        logger.info('Starting all Silver Tier watchers...')
        
        watchers = {
            'Filesystem': ['filesystem_watcher.py', '--interval', '30'],
            'Gmail': ['gmail_watcher.py', '--interval', '120'],
            'LinkedIn': ['linkedin_watcher.py', '--interval', '30'],
            'Orchestrator': ['orchestrator.py', '--watch', '--interval', '60']
        }
        
        processes = {}
        
        for name, args in watchers.items():
            cmd = [sys.executable] + args + ['--vault', '..']
            
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(self.scripts_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                processes[name] = proc
                logger.info(f'{name} Watcher started (PID: {proc.pid})')
            except Exception as e:
                logger.error(f'Failed to start {name}: {e}')
        
        return processes
    
    def run_automation(self, content: str, category: str = 'business_update'):
        """
        Run full automation: create post, start watcher, auto-post.
        
        Args:
            content: LinkedIn post content
            category: Post category
        """
        logger.info('=' * 60)
        logger.info('AI Employee Silver Tier - Full Automation')
        logger.info('=' * 60)
        
        # Step 1: Create post (goes directly to Approved/)
        logger.info('Step 1: Creating LinkedIn post...')
        self.create_linkedin_post(content, category)
        
        # Step 2: Start LinkedIn Watcher
        logger.info('Step 2: Starting LinkedIn Watcher...')
        watcher_proc = self.start_linkedin_watcher()
        
        # Step 3: Wait for posting to complete
        logger.info('Step 3: Waiting for auto-post (max 5 minutes)...')
        start_time = time.time()
        max_wait = 300  # 5 minutes
        
        while time.time() - start_time < max_wait:
            time.sleep(10)
            
            # Check if post was moved to Done
            done_folder = self.vault_path / 'Done' / 'LinkedIn'
            if done_folder.exists() and list(done_folder.glob('LINKEDIN_POST_*.md')):
                logger.info('✓ Post published successfully!')
                break
        
        # Cleanup
        logger.info('Stopping watcher...')
        watcher_proc.terminate()
        
        logger.info('=' * 60)
        logger.info('Automation complete!')
        logger.info('=' * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Auto Runner')
    parser.add_argument('--vault', '-v', type=str, default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--content', '-c', type=str, required=True,
                       help='LinkedIn post content')
    parser.add_argument('--category', type=str, default='business_update',
                       help='Post category')
    parser.add_argument('--watchers', action='store_true',
                       help='Start all watchers (not just LinkedIn)')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    runner = AIEmployeeAutoRunner(str(vault_path))
    
    if args.watchers:
        # Start all watchers
        processes = runner.start_all_watchers()
        logger.info('All watchers running. Press Ctrl+C to stop.')
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info('Stopping all watchers...')
            for name, proc in processes.items():
                proc.terminate()
            logger.info('All watchers stopped.')
    else:
        # Run automation
        runner.run_automation(args.content, args.category)


if __name__ == '__main__':
    main()
