# 🏢 Odoo MCP - ERP Integration Skill

**Type**: MCP Server  
**Purpose**: Connect AI Employee to Odoo ERP for accounting, invoices, payments, and business management  
**Status**: 🚧 Development  

---

## Overview

This skill provides a Model Context Protocol (MCP) server that enables Qwen Code to interact with Odoo ERP via JSON-RPC APIs. It supports:

- **Accounting**: Create invoices, record payments, manage accounts
- **CRM**: Manage customers, leads, opportunities
- **Inventory**: Track products, stock levels
- **Projects**: Manage tasks, timesheets
- **Reports**: Generate financial reports

---

## Architecture

```
┌─────────────────┐      JSON-RPC      ┌─────────────────┐
│   Qwen Code     │ ◄────────────────► │   Odoo MCP      │
│   (Reasoning)   │    MCP Protocol    │   Server        │
└─────────────────┘                    └────────┬────────┘
                                                │
                                                │ XML-RPC
                                                ▼
                                       ┌─────────────────┐
                                       │   Odoo ERP      │
                                       │   (Community)   │
                                       └─────────────────┘
```

---

## Installation

### 1. Start Odoo (Docker)

```bash
cd gold-tier/docker
docker-compose up -d
```

### 2. Install Python Dependencies

```bash
pip install requests python-dotenv
```

### 3. Configure Connection

```bash
python scripts/odoo_config.py \
  --url http://localhost:8069 \
  --db odoo \
  --username admin \
  --password admin
```

---

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `odoo_create_invoice` | Create customer invoice | customer_id, amount, description, due_date |
| `odoo_get_invoice` | Get invoice details | invoice_id |
| `odoo_list_invoices` | List invoices with filters | status, customer_id, date_range |
| `odoo_post_invoice` | Validate/post draft invoice | invoice_id |
| `odoo_register_payment` | Record payment against invoice | invoice_id, amount, payment_method |
| `odoo_create_customer` | Create new customer | name, email, phone, address |
| `odoo_get_customer` | Get customer details | customer_id |
| `odoo_list_customers` | List all customers | limit, offset |
| `odoo_create_product` | Create new product | name, price, category |
| `odoo_get_financial_report` | Get financial summary | period, type |

---

## Usage Examples

### Create Invoice

```python
# MCP Call
python scripts/mcp_client.py call -u http://localhost:8810 \
  -t odoo_create_invoice \
  -p '{"customer_id": 1, "amount": 1500.00, "description": "January 2026 Services", "due_date": "2026-04-01"}'
```

### Register Payment

```python
# MCP Call
python scripts/mcp_client.py call -u http://localhost:8810 \
  -t odoo_register_payment \
  -p '{"invoice_id": "INV/2026/0001", "amount": 1500.00, "payment_method": "bank_transfer"}'
```

### Get Financial Report

```python
# MCP Call
python scripts/mcp_client.py call -u http://localhost:8810 \
  -t odoo_get_financial_report \
  -p '{"period": "last_month", "type": "profit_loss"}'
```

---

## Configuration File

```json
{
  "odoo_url": "http://localhost:8069",
  "database": "odoo",
  "username": "admin",
  "password": "secure_password",
  "timeout": 30,
  "retry_attempts": 3
}
```

---

## Error Handling

| Error | Code | Recovery |
|-------|------|----------|
| Connection refused | ODOO_001 | Check Docker container |
| Authentication failed | ODOO_002 | Verify credentials |
| Database not found | ODOO_003 | Create database |
| Record not found | ODOO_004 | Check ID/parameters |
| Permission denied | ODOO_005 | Update user permissions |

---

## Security

- Never store credentials in code
- Use environment variables or encrypted config
- Enable HTTPS for production
- Rotate API passwords regularly
- Limit user permissions to minimum required

---

## References

- [Odoo 19 External API Docs](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Odoo JSON-RPC Examples](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [mcp-odoo-adv](https://github.com/AlanOgic/mcp-odoo-adv)

---

*Odoo MCP Skill v0.1 | AI Employee Hackathon 2026*
