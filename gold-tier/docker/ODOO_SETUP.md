# Odoo Docker Setup Guide

## Current Status

**Docker images are downloading.** This may take 10-30 minutes depending on your internet speed.

- Odoo image: ~400MB
- PostgreSQL image: ~70MB

---

## Manual Setup Instructions

### Step 1: Start Odoo Containers

Open Command Prompt and run:

```bash
cd C:\Users\hr773\Documents\GitHub\personal-AI-FTE\gold-tier\docker
docker-compose up -d
```

### Step 2: Wait for Odoo to Start

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f odoo
```

Wait until you see: `Odoo is running`

### Step 3: Access Odoo

Open your browser and go to:
**http://localhost:8069**

### Step 4: Configure Odoo Database

1. **Master Password**: `admin`
2. **Database Name**: `odoo`
3. **Email**: `admin@example.com`
4. **Password**: `admin`

Click **Create Database**

### Step 5: Configure Odoo MCP

```bash
cd C:\Users\hr773\Documents\GitHub\personal-AI-FTE\gold-tier\odoo-mcp\scripts
python odoo_config.py --url http://localhost:8069 --db odoo --username admin --password admin
```

### Step 6: Test Odoo Connection

```bash
python odoo_client.py
```

Expected output:
```
✅ Connected to Odoo
   User ID: 2
   URL: http://localhost:8069
   Database: odoo
```

---

## Quick Commands

```bash
# Start Odoo
cd C:\Users\hr773\Documents\GitHub\personal-AI-FTE\gold-tier\docker
docker-compose up -d

# Stop Odoo
docker-compose down

# View logs
docker-compose logs -f

# Restart Odoo
docker-compose restart

# Check status
docker-compose ps
```

---

## Troubleshooting

### Port 8069 Already in Use

```bash
# Find what's using port 8069
netstat -ano | findstr :8069

# Kill the process
taskkill /PID <PID> /F
```

### Container Won't Start

```bash
# View logs
docker-compose logs odoo

# Recreate containers
docker-compose down
docker-compose up -d --force-recreate
```

### Database Connection Error

```bash
# Check database container
docker-compose logs db

# Restart database
docker-compose restart db
```

---

## Odoo MCP Integration

Once Odoo is running, you can:

### Create Invoice
```bash
python odoo_mcp_server.py --port 8810
```

Then use MCP tools:
- `odoo_create_invoice`
- `odoo_register_payment`
- `odoo_get_financial_report`

### Test with Qwen Code
```bash
qwen "Create an invoice for $1500 for Client A using Odoo MCP"
```

---

## Gold Tier Verification Status

| Component | Status |
|-----------|--------|
| Facebook Integration | ✅ Complete & Tested |
| Twitter Integration | ✅ Code Complete |
| Odoo Integration | ⏳ Docker Setup In Progress |
| CEO Briefing | ✅ Code Complete |
| Audit Logger | ✅ Complete |
| Error Recovery | ✅ Complete |
| Ralph Wiggum Loop | ✅ Code Complete |

---

*Odoo Docker Setup Guide | AI Employee Gold Tier*
