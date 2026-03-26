#!/usr/bin/env python3
"""
Odoo MCP Configuration Script

Configures connection to Odoo ERP instance.
Creates .env file with credentials (never commit this file).
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key


def parse_args():
    parser = argparse.ArgumentParser(description='Configure Odoo MCP connection')
    parser.add_argument('--url', required=True, help='Odoo URL (e.g., http://localhost:8069)')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--username', required=True, help='Odoo username')
    parser.add_argument('--password', required=True, help='Odoo password')
    parser.add_argument('--vault', default='../AI_Employee_Vault', help='Vault path')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    return parser.parse_args()


def test_connection(url: str, db: str, username: str, password: str) -> bool:
    """Test connection to Odoo instance."""
    import requests
    
    try:
        # Test common authentication endpoint
        response = requests.post(
            f'{url}/web/session/authenticate',
            json={
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'db': db,
                    'login': username,
                    'password': password,
                },
                'id': 1,
            },
            headers={'Content-Type': 'application/json'},
            timeout=10,
        )
        
        result = response.json()
        if result.get('result', {}).get('uid'):
            print(f'✅ Connection successful!')
            print(f'   User ID: {result["result"]["uid"]}')
            print(f'   Username: {username}')
            print(f'   Database: {db}')
            return True
        else:
            print(f'❌ Authentication failed')
            print(f'   Error: {result.get("error", {}).get("data", "Unknown error")}')
            return False
            
    except requests.exceptions.ConnectionError:
        print(f'❌ Connection refused')
        print(f'   Is Odoo running at {url}?')
        print(f'   Try: docker-compose up -d')
        return False
    except requests.exceptions.Timeout:
        print(f'❌ Connection timeout')
        print(f'   Odoo server is not responding')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False


def save_config(url: str, db: str, username: str, password: str, vault: str, timeout: int):
    """Save configuration to .env file."""
    vault_path = Path(vault).resolve()
    config_dir = vault_path / 'Scripts' / 'Config'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    env_file = config_dir / '.env.odoo'
    
    # Save to .env file
    set_key(str(env_file), 'ODOO_URL', url)
    set_key(str(env_file), 'ODOO_DB', db)
    set_key(str(env_file), 'ODOO_USERNAME', username)
    set_key(str(env_file), 'ODOO_PASSWORD', password)
    set_key(str(env_file), 'ODOO_TIMEOUT', str(timeout))
    
    print(f'\n✅ Configuration saved to: {env_file}')
    print(f'   ⚠️  NEVER commit this file to version control!')
    
    # Also save to project root .env
    project_root = Path(__file__).parent.parent.parent.parent
    root_env = project_root / '.env.odoo'
    set_key(str(root_env), 'ODOO_URL', url)
    set_key(str(root_env), 'ODOO_DB', db)
    set_key(str(root_env), 'ODOO_USERNAME', username)
    set_key(str(root_env), 'ODOO_PASSWORD', password)
    set_key(str(root_env), 'ODOO_TIMEOUT', str(timeout))
    
    print(f'   Also saved to: {root_env}')


def main():
    args = parse_args()
    
    print('🔧 Odoo MCP Configuration')
    print('=' * 50)
    print(f'\nTesting connection to: {args.url}')
    print(f'Database: {args.db}')
    print(f'Username: {args.username}')
    print()
    
    if test_connection(args.url, args.db, args.username, args.password):
        save_config(
            args.url, 
            args.db, 
            args.username, 
            args.password,
            args.vault,
            args.timeout
        )
        print('\n✅ Configuration complete!')
        print('\nNext steps:')
        print('1. Start Odoo MCP server:')
        print('   python scripts/odoo_mcp_server.py --port 8810')
        return 0
    else:
        print('\n❌ Configuration failed')
        print('\nTroubleshooting:')
        print('1. Ensure Odoo is running: docker-compose ps')
        print('2. Check Odoo logs: docker-compose logs odoo')
        print('3. Verify credentials in Odoo admin panel')
        return 1


if __name__ == '__main__':
    sys.exit(main())
