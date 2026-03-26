#!/usr/bin/env python3
"""
Odoo MCP Server

Model Context Protocol server for Odoo ERP integration.
Exposes accounting, CRM, and business management tools.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from odoo_client import OdooClient, get_client


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class OdooMCPServer:
    """MCP Server for Odoo ERP."""
    
    def __init__(self, port: int = 8810):
        self.port = port
        self.client: Optional[OdooClient] = None
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available MCP tools."""
        return [
            {
                'name': 'odoo_create_invoice',
                'description': 'Create a new customer invoice in Odoo',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'customer_id': {'type': 'integer', 'description': 'Customer ID'},
                        'amount': {'type': 'number', 'description': 'Invoice amount'},
                        'description': {'type': 'string', 'description': 'Invoice description'},
                        'due_date': {'type': 'string', 'description': 'Due date (YYYY-MM-DD)'},
                        'invoice_date': {'type': 'string', 'description': 'Invoice date (YYYY-MM-DD)'},
                    },
                    'required': ['customer_id', 'amount', 'description'],
                },
            },
            {
                'name': 'odoo_get_invoice',
                'description': 'Get invoice details by ID or name',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'invoice_id': {'type': 'integer', 'description': 'Invoice ID'},
                        'invoice_name': {'type': 'string', 'description': 'Invoice name (e.g., INV/2026/0001)'},
                    },
                },
            },
            {
                'name': 'odoo_list_invoices',
                'description': 'List invoices with optional filters',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'description': 'Invoice status (draft, posted, paid, cancel)'},
                        'customer_id': {'type': 'integer', 'description': 'Filter by customer'},
                        'date_from': {'type': 'string', 'description': 'From date (YYYY-MM-DD)'},
                        'date_to': {'type': 'string', 'description': 'To date (YYYY-MM-DD)'},
                        'limit': {'type': 'integer', 'description': 'Max results', 'default': 10},
                    },
                },
            },
            {
                'name': 'odoo_post_invoice',
                'description': 'Validate/post a draft invoice',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'invoice_id': {'type': 'integer', 'description': 'Invoice ID'},
                    },
                    'required': ['invoice_id'],
                },
            },
            {
                'name': 'odoo_register_payment',
                'description': 'Register payment against an invoice',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'invoice_id': {'type': 'integer', 'description': 'Invoice ID'},
                        'amount': {'type': 'number', 'description': 'Payment amount'},
                        'payment_method': {'type': 'string', 'description': 'Payment method (bank_transfer, cash, check)'},
                        'payment_date': {'type': 'string', 'description': 'Payment date (YYYY-MM-DD)'},
                        'reference': {'type': 'string', 'description': 'Payment reference'},
                    },
                    'required': ['invoice_id', 'amount'],
                },
            },
            {
                'name': 'odoo_create_customer',
                'description': 'Create a new customer',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Customer name'},
                        'email': {'type': 'string', 'description': 'Email address'},
                        'phone': {'type': 'string', 'description': 'Phone number'},
                        'address': {'type': 'string', 'description': 'Address'},
                        'city': {'type': 'string', 'description': 'City'},
                        'country': {'type': 'string', 'description': 'Country'},
                    },
                    'required': ['name'],
                },
            },
            {
                'name': 'odoo_get_customer',
                'description': 'Get customer details',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'customer_id': {'type': 'integer', 'description': 'Customer ID'},
                        'email': {'type': 'string', 'description': 'Search by email'},
                    },
                },
            },
            {
                'name': 'odoo_list_customers',
                'description': 'List all customers',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Max results', 'default': 80},
                    },
                },
            },
            {
                'name': 'odoo_create_product',
                'description': 'Create a new product',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Product name'},
                        'price': {'type': 'number', 'description': 'Sale price'},
                        'cost': {'type': 'number', 'description': 'Cost price'},
                        'category': {'type': 'string', 'description': 'Product category'},
                        'description': {'type': 'string', 'description': 'Product description'},
                    },
                    'required': ['name'],
                },
            },
            {
                'name': 'odoo_get_financial_report',
                'description': 'Get financial summary report',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'period': {'type': 'string', 'description': 'Period (this_month, last_month, this_quarter, this_year)'},
                        'type': {'type': 'string', 'description': 'Report type (profit_loss, balance_sheet, cash_flow)'},
                    },
                },
            },
        ]
    
    def _get_client(self) -> OdooClient:
        """Get or create Odoo client."""
        if self.client is None:
            self.client = get_client()
        return self.client
    
    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return result."""
        try:
            client = self._get_client()
            
            if name == 'odoo_create_invoice':
                return self._create_invoice(client, arguments)
            elif name == 'odoo_get_invoice':
                return self._get_invoice(client, arguments)
            elif name == 'odoo_list_invoices':
                return self._list_invoices(client, arguments)
            elif name == 'odoo_post_invoice':
                return self._post_invoice(client, arguments)
            elif name == 'odoo_register_payment':
                return self._register_payment(client, arguments)
            elif name == 'odoo_create_customer':
                return self._create_customer(client, arguments)
            elif name == 'odoo_get_customer':
                return self._get_customer(client, arguments)
            elif name == 'odoo_list_customers':
                return self._list_customers(client, arguments)
            elif name == 'odoo_create_product':
                return self._create_product(client, arguments)
            elif name == 'odoo_get_financial_report':
                return self._get_financial_report(client, arguments)
            else:
                return {'error': f'Unknown tool: {name}'}
                
        except Exception as e:
            logger.error(f'Tool execution error: {e}')
            return {'error': str(e)}
    
    def _create_invoice(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer invoice."""
        # In Odoo 19, invoices are account.move with move_type='out_invoice'
        invoice_data = {
            'move_type': 'out_invoice',
            'partner_id': args['customer_id'],
            'invoice_date': args.get('invoice_date', datetime.now().strftime('%Y-%m-%d')),
            'invoice_date_due': args.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
            'narration': args['description'],
        }
        
        # Create invoice
        invoice_id = client.create('account.move', invoice_data)
        
        # Create invoice line (required for valid invoice)
        amount = args['amount']
        client.create('account.move.line', {
            'move_id': invoice_id,
            'name': args['description'],
            'quantity': 1,
            'price_unit': amount,
        })
        
        # Get invoice name
        invoice = client.read('account.move', [invoice_id], ['name'])[0]
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'invoice_name': invoice.get('name', f'INV/{invoice_id}'),
            'amount': amount,
            'status': 'draft',
        }
    
    def _get_invoice(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get invoice details."""
        if 'invoice_id' in args:
            invoice_id = args['invoice_id']
        elif 'invoice_name' in args:
            # Search by name
            ids = client.search('account.move', [
                ['name', '=', args['invoice_name']]
            ])
            if not ids:
                return {'error': f'Invoice not found: {args["invoice_name"]}'}
            invoice_id = ids[0]
        else:
            return {'error': 'Provide invoice_id or invoice_name'}
        
        fields = ['name', 'partner_id', 'amount_total', 'amount_residual', 
                  'state', 'invoice_date', 'invoice_date_due', 'narration']
        invoice = client.read('account.move', [invoice_id], fields)[0]
        
        # Get customer name
        if 'partner_id' in invoice and isinstance(invoice['partner_id'], list):
            invoice['customer_name'] = invoice['partner_id'][1]
            invoice['partner_id'] = invoice['partner_id'][0]
        
        return {'success': True, 'invoice': invoice}
    
    def _list_invoices(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """List invoices with filters."""
        domain = []
        
        if 'status' in args:
            domain.append(['state', '=', args['status']])
        if 'customer_id' in args:
            domain.append(['partner_id', '=', args['customer_id']])
        if 'date_from' in args:
            domain.append(['invoice_date', '>=', args['date_from']])
        if 'date_to' in args:
            domain.append(['invoice_date', '<=', args['date_to']])
        
        ids = client.search('account.move', domain=domain, limit=args.get('limit', 10))
        
        if not ids:
            return {'success': True, 'invoices': [], 'count': 0}
        
        fields = ['name', 'partner_id', 'amount_total', 'amount_residual', 'state', 'invoice_date']
        invoices = client.read('account.move', ids, fields)
        
        # Format partner_id
        for inv in invoices:
            if 'partner_id' in inv and isinstance(inv['partner_id'], list):
                inv['customer_name'] = inv['partner_id'][1]
                inv['partner_id'] = inv['partner_id'][0]
        
        return {'success': True, 'invoices': invoices, 'count': len(invoices)}
    
    def _post_invoice(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Post/validate draft invoice."""
        invoice_id = args['invoice_id']
        
        # Check state first
        invoice = client.read('account.move', [invoice_id], ['state'])[0]
        if invoice.get('state') != 'draft':
            return {'error': f'Invoice is not in draft state: {invoice.get("state")}'}
        
        # Post the invoice
        client.execute('account.move', 'action_post', args=[[invoice_id]])
        
        return {'success': True, 'invoice_id': invoice_id, 'status': 'posted'}
    
    def _register_payment(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Register payment against invoice."""
        invoice_id = args['invoice_id']
        amount = args['amount']
        
        # Create payment wizard
        payment_data = {
            'amount': amount,
            'payment_date': args.get('payment_date', datetime.now().strftime('%Y-%m-%d')),
            'payment_method_line_id': 1,  # Default payment method
            'payment_type': 'inbound',  # Receive payment
        }
        
        # Simplified: directly create account.payment
        payment_id = client.create('account.payment', {
            'amount': amount,
            'date': payment_data['payment_date'],
            'payment_type': 'inbound',
            'partner_id': client.read('account.move', [invoice_id], ['partner_id'])[0]['partner_id'][0],
        })
        
        # Reconcile with invoice
        client.execute('account.payment', 'action_post', args=[[payment_id]])
        
        return {
            'success': True,
            'payment_id': payment_id,
            'invoice_id': invoice_id,
            'amount': amount,
        }
    
    def _create_customer(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create new customer."""
        customer_data = {
            'name': args['name'],
            'email': args.get('email', ''),
            'phone': args.get('phone', ''),
            'street': args.get('address', ''),
            'city': args.get('city', ''),
            'country_id': args.get('country', ''),
        }
        
        customer_id = client.create('res.partner', customer_data)
        
        return {
            'success': True,
            'customer_id': customer_id,
            'name': args['name'],
        }
    
    def _get_customer(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer details."""
        if 'customer_id' in args:
            customer_id = args['customer_id']
        elif 'email' in args:
            ids = client.search('res.partner', [['email', '=', args['email']]])
            if not ids:
                return {'error': f'Customer not found: {args["email"]}'}
            customer_id = ids[0]
        else:
            return {'error': 'Provide customer_id or email'}
        
        fields = ['name', 'email', 'phone', 'street', 'city', 'country_id']
        customer = client.read('res.partner', [customer_id], fields)[0]
        
        return {'success': True, 'customer': customer}
    
    def _list_customers(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all customers."""
        ids = client.search('res.partner', domain=[['customer', '=', True]], limit=args.get('limit', 80))
        
        if not ids:
            return {'success': True, 'customers': [], 'count': 0}
        
        fields = ['name', 'email', 'phone']
        customers = client.read('res.partner', ids, fields)
        
        return {'success': True, 'customers': customers, 'count': len(customers)}
    
    def _create_product(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create new product."""
        product_data = {
            'name': args['name'],
            'list_price': args.get('price', 0),
            'standard_price': args.get('cost', 0),
            'categ_id': args.get('category', 'All / Saleable'),
            'description_sale': args.get('description', ''),
            'type': 'product',
        }
        
        product_id = client.create('product.template', product_data)
        
        return {
            'success': True,
            'product_id': product_id,
            'name': args['name'],
        }
    
    def _get_financial_report(self, client: OdooClient, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial summary."""
        period = args.get('period', 'this_month')
        
        # Calculate date range
        now = datetime.now()
        if period == 'this_month':
            date_from = now.replace(day=1).strftime('%Y-%m-%d')
            date_to = now.strftime('%Y-%m-%d')
        elif period == 'last_month':
            first_day = now.replace(day=1) - timedelta(days=1)
            date_from = first_day.replace(day=1).strftime('%Y-%m-%d')
            date_to = first_day.strftime('%Y-%m-%d')
        elif period == 'this_quarter':
            quarter = (now.month - 1) // 3 + 1
            date_from = datetime(now.year, (quarter - 1) * 3 + 1, 1).strftime('%Y-%m-%d')
            date_to = now.strftime('%Y-%m-%d')
        elif period == 'this_year':
            date_from = datetime(now.year, 1, 1).strftime('%Y-%m-%d')
            date_to = now.strftime('%Y-%m-%d')
        else:
            date_from = now.replace(day=1).strftime('%Y-%m-%d')
            date_to = now.strftime('%Y-%m-%d')
        
        # Get invoices in period
        invoice_ids = client.search('account.move', [
            ['move_type', '=', 'out_invoice'],
            ['invoice_date', '>=', date_from],
            ['invoice_date', '<=', date_to],
        ])
        
        revenue = 0
        if invoice_ids:
            invoices = client.read('account.move', invoice_ids, ['amount_total', 'state'])
            for inv in invoices:
                if inv.get('state') == 'posted':
                    revenue += inv.get('amount_total', 0)
        
        # Get bills (expenses)
        bill_ids = client.search('account.move', [
            ['move_type', 'in', ['in_invoice', 'in_refund']],
            ['invoice_date', '>=', date_from],
            ['invoice_date', '<=', date_to],
        ])
        
        expenses = 0
        if bill_ids:
            bills = client.read('account.move', bill_ids, ['amount_total', 'state'])
            for bill in bills:
                if bill.get('state') == 'posted':
                    expenses += bill.get('amount_total', 0)
        
        return {
            'success': True,
            'period': period,
            'date_from': date_from,
            'date_to': date_to,
            'revenue': revenue,
            'expenses': expenses,
            'profit': revenue - expenses,
        }
    
    def run(self):
        """Run MCP server (stdio mode)."""
        logger.info(f'Starting Odoo MCP Server on port {self.port}')
        
        # Initialize client
        try:
            self._get_client()
            logger.info('Connected to Odoo')
        except Exception as e:
            logger.error(f'Failed to connect to Odoo: {e}')
            return 1
        
        # Simple stdio loop for MCP
        print(json.dumps({
            'jsonrpc': '2.0',
            'method': 'initialized',
            'params': {'tools': self.tools},
        }), flush=True)
        
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                method = request.get('method')
                params = request.get('params', {})
                
                if method == 'tools/call':
                    tool_name = params.get('name')
                    arguments = params.get('arguments', {})
                    result = self.execute_tool(tool_name, arguments)
                    
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {
                            'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}],
                        },
                    }
                else:
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'error': {'code': -32601, 'message': f'Method not found: {method}'},
                    }
                
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f'JSON decode error: {e}')
            except Exception as e:
                logger.error(f'Error processing request: {e}')
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id', 0),
                    'error': {'code': -32603, 'message': str(e)},
                }
                print(json.dumps(response), flush=True)
        
        return 0


def main():
    parser = argparse.ArgumentParser(description='Odoo MCP Server')
    parser.add_argument('--port', type=int, default=8810, help='Server port')
    args = parser.parse_args()
    
    server = OdooMCPServer(port=args.port)
    return server.run()


if __name__ == '__main__':
    sys.exit(main())
