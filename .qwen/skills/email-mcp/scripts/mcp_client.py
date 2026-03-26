"""
MCP Client for Email Server

Simple client to test Email MCP Server tools.
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Dict, Any


def call_mcp_tool(server_url: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call MCP server tool.
    
    Args:
        server_url: MCP server URL (e.g., http://localhost:8809)
        tool_name: Tool name (email_send, email_draft, email_search)
        params: Tool parameters as dict
        
    Returns:
        Server response as dict
    """
    request_data = {
        'tool': tool_name,
        'params': params
    }
    
    try:
        # Send POST request
        req = urllib.request.Request(
            server_url,
            data=json.dumps(request_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
            
    except urllib.error.URLError as e:
        return {
            'success': False,
            'error': f'Connection failed: {e.reason}',
            'hint': 'Make sure Email MCP Server is running on the specified port'
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Invalid response: {e}',
            'hint': 'Server returned non-JSON response'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {e}'
        }


def main():
    """Run MCP client."""
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Client for Email Server')
    parser.add_argument(
        '--url', '-u',
        type=str,
        default='http://localhost:8809',
        help='MCP server URL (default: http://localhost:8809)'
    )
    parser.add_argument(
        '--tool', '-t',
        type=str,
        required=True,
        choices=['email_send', 'email_draft', 'email_search'],
        help='Tool to call'
    )
    parser.add_argument(
        '--params', '-p',
        type=str,
        required=True,
        help='JSON parameters (e.g., \'{"to": "test@example.com", "subject": "Test"}\')'
    )
    
    args = parser.parse_args()
    
    # Parse params
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in params: {e}")
        sys.exit(1)
    
    # Call tool
    print(f"Calling {args.tool} on {args.url}...")
    result = call_mcp_tool(args.url, args.tool, params)
    
    # Print result
    print()
    print("Response:")
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print()
        print("Success!")
        sys.exit(0)
    else:
        print()
        print("Failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
