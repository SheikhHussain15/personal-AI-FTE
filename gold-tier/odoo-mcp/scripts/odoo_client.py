#!/usr/bin/env python3
"""
Odoo JSON-RPC Client

Low-level client for communicating with Odoo ERP via JSON-RPC.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

import requests
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class OdooClient:
    """Client for Odoo JSON-RPC API."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Odoo client.
        
        Args:
            url: Odoo instance URL (e.g., http://localhost:8069)
            database: Database name
            username: Odoo username
            password: Odoo password
            timeout: Request timeout in seconds
        """
        # Load from environment if not provided
        load_dotenv()
        
        self.url = url or os.getenv('ODOO_URL', 'http://localhost:8069')
        self.database = database or os.getenv('ODOO_DB', 'odoo')
        self.username = username or os.getenv('ODOO_USERNAME', 'admin')
        self.password = password or os.getenv('ODOO_PASSWORD', 'admin')
        self.timeout = timeout or int(os.getenv('ODOO_TIMEOUT', '30'))
        
        self.uid: Optional[int] = None
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo instance.
        
        Returns:
            True if authentication successful
        """
        try:
            response = self.session.post(
                f'{self.url}/web/session/authenticate',
                json={
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': {
                        'db': self.database,
                        'login': self.username,
                        'password': self.password,
                    },
                    'id': 1,
                },
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout,
            )
            
            result = response.json()
            
            if 'result' in result and result['result'].get('uid'):
                self.uid = result['result']['uid']
                logger.info(f'Authenticated as user {self.uid}')
                return True
            else:
                logger.error(f'Authentication failed: {result.get("error", "Unknown error")}')
                return False
                
        except Exception as e:
            logger.error(f'Authentication error: {e}')
            return False
    
    def execute(
        self,
        model: str,
        method: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute a method on an Odoo model.
        
        Args:
            model: Odoo model name (e.g., 'account.move')
            method: Method to call (e.g., 'create', 'read', 'search')
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Method result
        """
        if self.uid is None:
            if not self.authenticate():
                raise Exception('Not authenticated')
        
        try:
            response = self.session.post(
                f'{self.url}/web/dataset/call_kw',
                json={
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': {
                        'model': model,
                        'method': method,
                        'args': args or [],
                        'kwargs': kwargs or {},
                    },
                    'id': 2,
                },
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout,
            )
            
            result = response.json()
            
            if 'error' in result:
                error = result['error']
                logger.error(f'Odoo error: {error.get("data", {}).get("message", error)}')
                raise Exception(f'Odoo error: {error}')
            
            return result.get('result', {})
            
        except Exception as e:
            logger.error(f'Execute error: {e}')
            raise
    
    def search(
        self,
        model: str,
        domain: Optional[List[Any]] = None,
        limit: int = 80,
        offset: int = 0,
        order: Optional[str] = None,
    ) -> List[int]:
        """
        Search for records in a model.
        
        Args:
            model: Odoo model name
            domain: Search domain (e.g., [['state', '=', 'draft']])
            limit: Maximum number of records
            offset: Offset for pagination
            order: Order by field
            
        Returns:
            List of record IDs
        """
        return self.execute(
            model,
            'search',
            kwargs={
                'domain': domain or [],
                'limit': limit,
                'offset': offset,
                'order': order,
            }
        )
    
    def read(
        self,
        model: str,
        ids: List[int],
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read fields from records.
        
        Args:
            model: Odoo model name
            ids: Record IDs
            fields: Fields to read
            
        Returns:
            List of record dictionaries
        """
        return self.execute(
            model,
            'read',
            args=[ids],
            kwargs={'fields': fields} if fields else {},
        )
    
    def create(
        self,
        model: str,
        values: Dict[str, Any],
    ) -> int:
        """
        Create a new record.
        
        Args:
            model: Odoo model name
            values: Field values
            
        Returns:
            New record ID
        """
        return self.execute(
            model,
            'create',
            args=[values],
        )
    
    def write(
        self,
        model: str,
        ids: List[int],
        values: Dict[str, Any],
    ) -> bool:
        """
        Update records.
        
        Args:
            model: Odoo model name
            ids: Record IDs
            values: Field values to update
            
        Returns:
            True if successful
        """
        return self.execute(
            model,
            'write',
            args=[ids, values],
        )
    
    def unlink(
        self,
        model: str,
        ids: List[int],
    ) -> bool:
        """
        Delete records.
        
        Args:
            model: Odoo model name
            ids: Record IDs
            
        Returns:
            True if successful
        """
        return self.execute(
            model,
            'unlink',
            args=[ids],
        )


# Convenience functions for MCP tools

def get_client() -> OdooClient:
    """Get authenticated Odoo client."""
    client = OdooClient()
    if not client.authenticate():
        raise Exception('Failed to authenticate with Odoo')
    return client


if __name__ == '__main__':
    # Test connection
    client = get_client()
    print(f'✅ Connected to Odoo')
    print(f'   User ID: {client.uid}')
    print(f'   URL: {client.url}')
    print(f'   Database: {client.database}')
