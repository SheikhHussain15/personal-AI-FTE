#!/usr/bin/env python3
"""
Gold Tier Verification Script

Verifies all Gold Tier components are properly installed and configured.
"""

import json
import os
import sys
import io
from pathlib import Path
from typing import List, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def check_file(path: Path, description: str) -> Tuple[bool, str]:
    """Check if file exists."""
    if path.exists():
        return True, f'✅ {description}'
    return False, f'❌ {description} - NOT FOUND'


def check_folder(path: Path, description: str) -> Tuple[bool, str]:
    """Check if folder exists."""
    if path.exists() and path.is_dir():
        return True, f'✅ {description}'
    return False, f'❌ {description} - NOT FOUND'


def check_env_var(name: str, description: str) -> Tuple[bool, str]:
    """Check if environment variable is set."""
    if os.getenv(name):
        return True, f'✅ {description}'
    return False, f'❌ {description} - NOT SET'


def main():
    print('=' * 60)
    print('  GOLD TIER VERIFICATION')
    print('  AI Employee Hackathon 2026')
    print('=' * 60)
    
    # Get paths
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    gold_tier = project_root / 'gold-tier'
    vault = project_root / 'AI_Employee_Vault'
    
    checks = []
    passed = 0
    failed = 0
    
    print('\n📁 FOLDER STRUCTURE')
    print('-' * 40)
    
    # Check Gold Tier folders
    folders = [
        (gold_tier, 'Gold Tier root'),
        (gold_tier / 'docker', 'Docker config'),
        (gold_tier / 'odoo-mcp', 'Odoo MCP'),
        (gold_tier / 'odoo-mcp' / 'scripts', 'Odoo MCP scripts'),
        (gold_tier / 'facebook-integration', 'Facebook Integration'),
        (gold_tier / 'facebook-integration' / 'scripts', 'Facebook scripts'),
        (gold_tier / 'twitter-integration', 'Twitter Integration'),
        (gold_tier / 'twitter-integration' / 'scripts', 'Twitter scripts'),
        (gold_tier / 'ceo-briefing', 'CEO Briefing'),
        (gold_tier / 'ceo-briefing' / 'scripts', 'CEO Briefing scripts'),
        (gold_tier / 'audit-logger', 'Audit Logger'),
        (gold_tier / 'audit-logger' / 'scripts', 'Audit Logger scripts'),
        (gold_tier / 'error-recovery', 'Error Recovery'),
        (gold_tier / 'error-recovery' / 'scripts', 'Error Recovery scripts'),
        (gold_tier / 'ralph-wiggum', 'Ralph Wiggum'),
        (gold_tier / 'ralph-wiggum' / 'scripts', 'Ralph Wiggum scripts'),
    ]
    
    for path, desc in folders:
        ok, msg = check_folder(path, desc)
        print(msg)
        if ok:
            passed += 1
        else:
            failed += 1
    
    print('\n📄 KEY FILES')
    print('-' * 40)
    
    # Check key files
    files = [
        (gold_tier / 'README.md', 'Gold Tier README'),
        (gold_tier / 'docker' / 'docker-compose.yml', 'Docker Compose'),
        (gold_tier / 'odoo-mcp' / 'SKILL.md', 'Odoo MCP Skill'),
        (gold_tier / 'odoo-mcp' / 'scripts' / 'odoo_client.py', 'Odoo Client'),
        (gold_tier / 'odoo-mcp' / 'scripts' / 'odoo_mcp_server.py', 'Odoo MCP Server'),
        (gold_tier / 'odoo-mcp' / 'scripts' / 'odoo_config.py', 'Odoo Config'),
        (gold_tier / 'facebook-integration' / 'SKILL.md', 'Facebook Skill'),
        (gold_tier / 'facebook-integration' / 'scripts' / 'facebook_client.py', 'Facebook Client'),
        (gold_tier / 'facebook-integration' / 'scripts' / 'facebook_watcher.py', 'Facebook Watcher'),
        (gold_tier / 'facebook-integration' / 'scripts' / 'facebook_poster.py', 'Facebook Poster'),
        (gold_tier / 'facebook-integration' / 'scripts' / 'instagram_poster.py', 'Instagram Poster'),
        (gold_tier / 'twitter-integration' / 'SKILL.md', 'Twitter Skill'),
        (gold_tier / 'twitter-integration' / 'scripts' / 'twitter_client.py', 'Twitter Client'),
        (gold_tier / 'twitter-integration' / 'scripts' / 'twitter_watcher.py', 'Twitter Watcher'),
        (gold_tier / 'twitter-integration' / 'scripts' / 'twitter_poster.py', 'Twitter Poster'),
        (gold_tier / 'ceo-briefing' / 'SKILL.md', 'CEO Briefing Skill'),
        (gold_tier / 'ceo-briefing' / 'scripts' / 'generate_briefing.py', 'CEO Briefing Generator'),
        (gold_tier / 'audit-logger' / 'SKILL.md', 'Audit Logger Skill'),
        (gold_tier / 'audit-logger' / 'scripts' / 'audit_logger.py', 'Audit Logger'),
        (gold_tier / 'error-recovery' / 'SKILL.md', 'Error Recovery Skill'),
        (gold_tier / 'error-recovery' / 'scripts' / 'error_recovery.py', 'Error Recovery'),
        (gold_tier / 'ralph-wiggum' / 'SKILL.md', 'Ralph Wiggum Skill'),
        (gold_tier / 'ralph-wiggum' / 'scripts' / 'ralph_loop.py', 'Ralph Loop'),
        (gold_tier / 'orchestrator.py', 'Gold Tier Orchestrator'),
    ]
    
    for path, desc in files:
        ok, msg = check_file(path, desc)
        print(msg)
        if ok:
            passed += 1
        else:
            failed += 1
    
    print('\n🔧 VAULT STRUCTURE')
    print('-' * 40)
    
    # Check vault folders
    vault_folders = [
        (vault, 'AI Employee Vault'),
        (vault / 'Briefings', 'Briefings'),
        (vault / 'Logs', 'Logs'),
        (vault / 'Accounting', 'Accounting'),
        (vault / 'Scripts', 'Scripts'),
    ]
    
    for path, desc in vault_folders:
        ok, msg = check_folder(path, desc)
        print(msg)
        if ok:
            passed += 1
        else:
            failed += 1
    
    print('\n🔑 CONFIGURATION')
    print('-' * 40)
    
    # Check environment files
    env_files = [
        (project_root / '.env.odoo', 'Odoo Config (.env.odoo)'),
        (project_root / '.env.facebook', 'Facebook Config (.env.facebook)'),
        (project_root / '.env.twitter', 'Twitter Config (.env.twitter)'),
    ]
    
    for path, desc in env_files:
        ok, msg = check_file(path, desc)
        print(msg)
        if ok:
            passed += 1
        else:
            failed += 1
    
    print('\n📊 VERIFICATION SUMMARY')
    print('=' * 60)
    print(f'  Passed: {passed}')
    print(f'  Failed: {failed}')
    print(f'  Total:  {passed + failed}')
    print('=' * 60)
    
    if failed == 0:
        print('\n✅ ALL CHECKS PASSED!')
        print('\nNext steps:')
        print('1. Configure credentials for each integration')
        print('2. Start Odoo: cd gold-tier/docker && docker-compose up -d')
        print('3. Run orchestrator: python gold-tier/orchestrator.py --vault AI_Employee_Vault')
        return 0
    else:
        print(f'\n⚠️  {failed} checks failed. Please review missing components.')
        print('\nRequired setup:')
        print('1. Ensure all Gold Tier files are created')
        print('2. Configure credentials (.env files)')
        print('3. Install dependencies: pip install -r gold-tier/requirements.txt')
        return 1


if __name__ == '__main__':
    sys.exit(main())
