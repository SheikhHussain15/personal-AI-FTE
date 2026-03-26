#!/usr/bin/env python3
"""
Gold Tier Orchestrator

Master orchestration script for AI Employee Gold Tier.
Manages all watchers, MCP servers, and automation tasks.
"""

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class GoldTierOrchestrator:
    """Orchestrator for Gold Tier AI Employee."""
    
    def __init__(self, vault_path: str):
        """
        Initialize Orchestrator.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        load_dotenv()
        
        self.vault_path = Path(vault_path).resolve()
        self.gold_tier_path = self.vault_path.parent / 'gold-tier'
        
        # Process management
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = False
        
        # Configuration
        self.config = self._load_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration."""
        config_file = self.vault_path / 'Scripts' / 'orchestrator_config.json'
        
        default_config = {
            'watchers': {
                'gmail': {'enabled': True, 'interval': 120},
                'whatsapp': {'enabled': True, 'interval': 30},
                'facebook': {'enabled': False, 'interval': 60},
                'twitter': {'enabled': False, 'interval': 30},
            },
            'mcp_servers': {
                'email': {'enabled': True, 'port': 8809},
                'odoo': {'enabled': False, 'port': 8810},
            },
            'scheduled_tasks': {
                'ceo_briefing': {'enabled': True, 'schedule': 'monday_7am'},
                'audit_archive': {'enabled': True, 'schedule': 'daily_midnight'},
            },
            'logging': {
                'level': 'INFO',
                'audit_enabled': True,
            },
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in loaded:
                            default_config[key].update(loaded[key])
            except Exception as e:
                logger.warning(f'Failed to load config: {e}')
        
        return default_config
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f'Received signal {signum}, shutting down...')
        self.running = False
        self.stop_all()
        sys.exit(0)
    
    def start_watcher(self, name: str, script: str, interval: int) -> bool:
        """
        Start a watcher process.
        
        Args:
            name: Watcher name
            script: Script path
            interval: Check interval in seconds
            
        Returns:
            True if started successfully
        """
        try:
            cmd = [
                sys.executable,
                script,
                '--vault', str(self.vault_path),
                '--interval', str(interval),
            ]
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            self.processes[name] = proc
            logger.info(f'Started watcher: {name} (PID: {proc.pid})')
            
            return True
            
        except Exception as e:
            logger.error(f'Failed to start watcher {name}: {e}')
            return False
    
    def start_mcp_server(self, name: str, script: str, port: int) -> bool:
        """
        Start an MCP server.
        
        Args:
            name: Server name
            script: Script path
            port: Server port
            
        Returns:
            True if started successfully
        """
        try:
            cmd = [
                sys.executable,
                script,
                '--port', str(port),
            ]
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            self.processes[name] = proc
            logger.info(f'Started MCP server: {name} (PID: {proc.pid}, Port: {port})')
            
            return True
            
        except Exception as e:
            logger.error(f'Failed to start MCP server {name}: {e}')
            return False
    
    def stop_process(self, name: str):
        """Stop a process by name."""
        if name in self.processes:
            proc = self.processes[name]
            proc.terminate()
            
            try:
                proc.wait(timeout=5)
                logger.info(f'Stopped process: {name}')
            except subprocess.TimeoutExpired:
                proc.kill()
                logger.warning(f'Killed process: {name}')
            
            del self.processes[name]
    
    def stop_all(self):
        """Stop all processes."""
        logger.info('Stopping all processes...')
        
        for name in list(self.processes.keys()):
            self.stop_process(name)
        
        logger.info('All processes stopped')
    
    def check_health(self) -> Dict[str, bool]:
        """Check health of all processes."""
        health = {}
        
        for name, proc in self.processes.items():
            if proc.poll() is None:
                health[name] = True
            else:
                health[name] = False
                logger.warning(f'Process {name} has exited unexpectedly')
        
        return health
    
    def restart_unhealthy(self):
        """Restart unhealthy processes."""
        health = self.check_health()
        
        for name, healthy in health.items():
            if not healthy:
                logger.info(f'Restarting unhealthy process: {name}')
                
                if name.endswith('_watcher'):
                    watcher_type = name.replace('_watcher', '')
                    config = self.config['watchers'].get(watcher_type, {})
                    if config.get('enabled'):
                        script = self.gold_tier_path / watcher_type / 'scripts' / f'{watcher_type}_watcher.py'
                        if script.exists():
                            self.start_watcher(name, str(script), config.get('interval', 60))
                elif name.endswith('_mcp'):
                    server_type = name.replace('_mcp', '')
                    config = self.config['mcp_servers'].get(server_type, {})
                    if config.get('enabled'):
                        script = self.gold_tier_path / f'{server_type}-mcp' / 'scripts' / f'{server_type}_mcp_server.py'
                        if script.exists():
                            self.start_mcp_server(name, str(script), config.get('port', 8800))
    
    def run_scheduled_tasks(self):
        """Run scheduled tasks based on current time."""
        now = datetime.now()
        
        # CEO Briefing - Monday 7 AM
        briefing_config = self.config['scheduled_tasks'].get('ceo_briefing', {})
        if briefing_config.get('enabled'):
            if now.weekday() == 0 and now.hour == 7 and now.minute == 0:
                logger.info('Running scheduled CEO Briefing')
                script = self.gold_tier_path / 'ceo-briefing' / 'scripts' / 'generate_briefing.py'
                if script.exists():
                    subprocess.run([
                        sys.executable, str(script),
                        '--vault', str(self.vault_path),
                        '--period', 'last_week',
                    ])
        
        # Audit Archive - Daily midnight
        archive_config = self.config['scheduled_tasks'].get('audit_archive', {})
        if archive_config.get('enabled'):
            if now.hour == 0 and now.minute == 0:
                logger.info('Running scheduled Audit Archive')
                script = self.gold_tier_path / 'audit-logger' / 'scripts' / 'audit_logger.py'
                if script.exists():
                    subprocess.run([
                        sys.executable, str(script),
                        '--vault', str(self.vault_path),
                        '--archive',
                    ])
    
    def start_all(self):
        """Start all configured services."""
        logger.info('Starting Gold Tier Orchestrator')
        logger.info(f'Vault: {self.vault_path}')
        logger.info(f'Gold Tier Path: {self.gold_tier_path}')
        
        # Start watchers
        for watcher_type, config in self.config['watchers'].items():
            if config.get('enabled'):
                script = self.gold_tier_path / f'{watcher_type}-integration' / 'scripts' / f'{watcher_type}_watcher.py'
                if not script.exists():
                    script = self.gold_tier_path.parent / '.qwen' / 'skills' / f'{watcher_type}-watcher' / 'scripts' / f'{watcher_type}_watcher.py'
                
                if script.exists():
                    self.start_watcher(
                        f'{watcher_type}_watcher',
                        str(script),
                        config.get('interval', 60),
                    )
                else:
                    logger.warning(f'Watcher script not found: {watcher_type}')
        
        # Start MCP servers
        for server_type, config in self.config['mcp_servers'].items():
            if config.get('enabled'):
                if server_type == 'odoo':
                    script = self.gold_tier_path / f'{server_type}-mcp' / 'scripts' / f'{server_type}_mcp_server.py'
                else:
                    script = self.gold_tier_path.parent / '.qwen' / 'skills' / f'{server_type}-mcp' / 'scripts' / f'{server_type}_mcp_server.py'
                
                if script.exists():
                    self.start_mcp_server(
                        f'{server_type}_mcp',
                        str(script),
                        config.get('port', 8800),
                    )
                else:
                    logger.warning(f'MCP server script not found: {server_type}')
        
        self.running = True
        logger.info('All services started')
    
    def run(self):
        """Run the orchestrator main loop."""
        self.start_all()
        
        last_health_check = time.time()
        last_scheduled_check = time.time()
        
        try:
            while self.running:
                time.sleep(1)
                
                # Health check every 30 seconds
                if time.time() - last_health_check > 30:
                    self.restart_unhealthy()
                    last_health_check = time.time()
                
                # Scheduled tasks check every minute
                if time.time() - last_scheduled_check > 60:
                    self.run_scheduled_tasks()
                    last_scheduled_check = time.time()
                    
        except KeyboardInterrupt:
            logger.info('Interrupted by user')
        finally:
            self.stop_all()


def parse_args():
    parser = argparse.ArgumentParser(description='Gold Tier Orchestrator')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--start', choices=['all', 'watchers', 'mcp'], default='all',
                       help='What to start')
    parser.add_argument('--status', action='store_true', help='Show status')
    return parser.parse_args()


def main():
    args = parse_args()
    
    orchestrator = GoldTierOrchestrator(vault_path=args.vault)
    
    if args.status:
        print('Gold Tier Orchestrator Status')
        print('=' * 50)
        print(f'Vault: {orchestrator.vault_path}')
        print(f'Config: {json.dumps(orchestrator.config, indent=2)}')
        return 0
    
    orchestrator.run()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
