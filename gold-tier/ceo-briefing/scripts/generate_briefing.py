#!/usr/bin/env python3
"""
CEO Briefing Generator

Generates comprehensive weekly business audit reports.
Analyzes finances, tasks, social media, and communications.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class CEOBriefingGenerator:
    """Generate CEO briefings from business data."""
    
    def __init__(self, vault_path: str):
        """
        Initialize Briefing Generator.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        load_dotenv()
        
        self.vault_path = Path(vault_path).resolve()
        self.briefings_folder = self.vault_path / 'Briefings'
        self.done_folder = self.vault_path / 'Done'
        self.accounting_folder = self.vault_path / 'Accounting'
        self.plans_folder = self.vault_path / 'Plans'
        
        # Ensure folders exist
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
        
        # Load business goals
        self.business_goals = self._load_business_goals()
        
        # Try to initialize Odoo client
        self.odoo_client = self._try_init_odoo()
    
    def _load_business_goals(self) -> Dict[str, Any]:
        """Load business goals from vault."""
        goals_file = self.vault_path / 'Business_Goals.md'
        
        if not goals_file.exists():
            logger.warning('Business_Goals.md not found')
            return {}
        
        content = goals_file.read_text(encoding='utf-8')
        
        # Parse frontmatter
        goals = {}
        in_frontmatter = False
        
        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                goals[key.strip()] = value.strip()
        
        # Parse revenue targets from content
        if 'Monthly Goal' in content:
            import re
            match = re.search(r'Monthly Goal:?\s*\$?([\d,]+)', content)
            if match:
                goals['monthly_revenue_target'] = float(match.group(1).replace(',', ''))
        
        return goals
    
    def _try_init_odoo(self):
        """Try to initialize Odoo client."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'odoo-mcp' / 'scripts'))
            from odoo_client import OdooClient
            
            client = OdooClient()
            if client.authenticate():
                logger.info('Odoo connection established')
                return client
            else:
                logger.warning('Odoo authentication failed')
                return None
        except Exception as e:
            logger.warning(f'Odoo not available: {e}')
            return None
    
    def _get_date_range(self, period: str) -> tuple:
        """Get date range for period."""
        now = datetime.now()
        
        if period == 'this_week':
            # Monday to today
            start = now - timedelta(days=now.weekday())
            end = now
        elif period == 'last_week':
            # Previous Monday to Sunday
            start = now - timedelta(days=now.weekday() + 7)
            end = start + timedelta(days=6)
        elif period == 'this_month':
            start = now.replace(day=1)
            end = now
        elif period == 'last_month':
            first_day = now.replace(day=1) - timedelta(days=1)
            start = first_day.replace(day=1)
            end = first_day
        elif period == 'this_quarter':
            quarter = (now.month - 1) // 3 + 1
            start = datetime(now.year, (quarter - 1) * 3 + 1, 1)
            end = now
        else:
            # Default: last 7 days
            start = now - timedelta(days=7)
            end = now
        
        return start.date(), end.date()
    
    def _analyze_revenue(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyze revenue for period."""
        result = {
            'total_revenue': 0,
            'invoice_count': 0,
            'paid_count': 0,
            'pending_count': 0,
            'top_invoices': [],
        }
        
        # Try Odoo first
        if self.odoo_client:
            try:
                # Search invoices in date range
                domain = [
                    ['move_type', '=', 'out_invoice'],
                    ['invoice_date', '>=', start_date],
                    ['invoice_date', '<=', end_date],
                ]
                
                invoice_ids = self.odoo_client.search('account.move', domain=domain)
                
                if invoice_ids:
                    invoices = self.odoo_client.read(
                        'account.move',
                        invoice_ids,
                        ['name', 'amount_total', 'amount_residual', 'state', 'partner_id', 'invoice_date']
                    )
                    
                    result['invoice_count'] = len(invoices)
                    
                    for inv in invoices:
                        amount = inv.get('amount_total', 0)
                        residual = inv.get('amount_residual', 0)
                        state = inv.get('state', '')
                        
                        if state == 'posted':
                            result['total_revenue'] += amount
                            
                            if residual <= 0:
                                result['paid_count'] += 1
                            else:
                                result['pending_count'] += 1
                            
                            # Get customer name
                            customer = inv.get('partner_id')
                            if isinstance(customer, list) and len(customer) > 1:
                                customer_name = customer[1]
                            else:
                                customer_name = 'Unknown'
                            
                            result['top_invoices'].append({
                                'name': inv.get('name', ''),
                                'customer': customer_name,
                                'amount': amount,
                                'paid': residual <= 0,
                            })
                
            except Exception as e:
                logger.error(f'Odoo revenue analysis error: {e}')
        
        # Fallback: Check Accounting folder for transaction files
        if result['total_revenue'] == 0 and self.accounting_folder.exists():
            # Parse markdown files for transactions
            for md_file in self.accounting_folder.glob('*.md'):
                content = md_file.read_text(encoding='utf-8')
                # Look for revenue entries
                if 'revenue' in content.lower() or 'income' in content.lower():
                    import re
                    matches = re.findall(r'\$?([\d,]+\.?\d*)', content)
                    for match in matches:
                        try:
                            result['total_revenue'] += float(match.replace(',', ''))
                        except ValueError:
                            pass
        
        return result
    
    def _analyze_expenses(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyze expenses for period."""
        result = {
            'total_expenses': 0,
            'expense_count': 0,
            'subscriptions': [],
            'alerts': [],
        }
        
        # Try Odoo
        if self.odoo_client:
            try:
                # Search bills in date range
                domain = [
                    ['move_type', 'in', ['in_invoice', 'in_refund']],
                    ['invoice_date', '>=', start_date],
                    ['invoice_date', '<=', end_date],
                ]
                
                bill_ids = self.odoo_client.search('account.move', domain=domain)
                
                if bill_ids:
                    bills = self.odoo_client.read(
                        'account.move',
                        bill_ids,
                        ['name', 'amount_total', 'partner_id', 'invoice_date']
                    )
                    
                    result['expense_count'] = len(bills)
                    
                    for bill in bills:
                        amount = bill.get('amount_total', 0)
                        result['total_expenses'] += amount
                        
                        # Check for subscriptions
                        vendor = bill.get('partner_id')
                        if isinstance(vendor, list) and len(vendor) > 1:
                            vendor_name = vendor[1].lower()
                            
                            # Common subscription patterns
                            subscription_keywords = ['software', 'saas', 'subscription', 'monthly', 'annual']
                            if any(kw in vendor_name for kw in subscription_keywords):
                                result['subscriptions'].append({
                                    'vendor': vendor[1],
                                    'amount': amount,
                                    'name': bill.get('name', ''),
                                })
                
            except Exception as e:
                logger.error(f'Odoo expense analysis error: {e}')
        
        # Check for subscription alerts
        expense_threshold = float(os.getenv('EXPENSE_ALERT_THRESHOLD', '600'))
        if result['total_expenses'] > expense_threshold:
            result['alerts'].append(f'High expenses: ${result["total_expenses"]:.2f} exceeds threshold ${expense_threshold}')
        
        return result
    
    def _analyze_completed_tasks(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyze completed tasks."""
        result = {
            'total_completed': 0,
            'by_category': {},
            'tasks': [],
        }
        
        if not self.done_folder.exists():
            return result
        
        # Count files by type
        for md_file in self.done_folder.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            
            # Extract type from frontmatter
            task_type = 'general'
            for line in content.split('\n')[:20]:
                if line.startswith('type:'):
                    task_type = line.split(':')[1].strip()
                    break
            
            result['by_category'][task_type] = result['by_category'].get(task_type, 0) + 1
            result['total_completed'] += 1
            
            # Get task name from filename
            task_name = md_file.stem.replace('_', ' ').replace('-', ' ')
            result['tasks'].append({
                'name': task_name,
                'type': task_type,
                'completed': md_file.stat().st_mtime,
            })
        
        # Sort by most recent
        result['tasks'].sort(key=lambda x: x['completed'], reverse=True)
        result['tasks'] = result['tasks'][:10]  # Top 10
        
        return result
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify bottlenecks and delays."""
        bottlenecks = []
        
        # Check Needs_Action folder for old items
        needs_action = self.vault_path / 'Needs_Action'
        if needs_action.exists():
            threshold = datetime.now() - timedelta(days=3)
            
            for md_file in needs_action.glob('*.md'):
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime < threshold:
                    days_old = (threshold - mtime).days
                    bottlenecks.append({
                        'item': md_file.name,
                        'type': 'stuck_in_needs_action',
                        'days_old': days_old,
                        'severity': 'high' if days_old > 7 else 'medium',
                    })
        
        # Check Pending_Approval for old approvals
        pending_approval = self.vault_path / 'Pending_Approval'
        if pending_approval.exists():
            threshold = datetime.now() - timedelta(days=1)
            
            for md_file in pending_approval.glob('*.md'):
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                if mtime < threshold:
                    days_old = (threshold - mtime).days
                    bottlenecks.append({
                        'item': md_file.name,
                        'type': 'pending_approval',
                        'days_old': days_old,
                        'severity': 'high',
                    })
        
        return bottlenecks
    
    def _get_social_summary(self) -> Dict[str, Any]:
        """Get social media activity summary."""
        result = {
            'facebook_posts': 0,
            'instagram_posts': 0,
            'twitter_posts': 0,
            'linkedin_posts': 0,
            'total_posts': 0,
        }
        
        if not self.done_folder.exists():
            return result
        
        # Count social media posts
        for md_file in self.done_folder.glob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            
            if 'facebook' in content.lower():
                result['facebook_posts'] += 1
            if 'instagram' in content.lower():
                result['instagram_posts'] += 1
            if 'twitter' in content.lower():
                result['twitter_posts'] += 1
            if 'linkedin' in content.lower():
                result['linkedin_posts'] += 1
        
        result['total_posts'] = (
            result['facebook_posts'] +
            result['instagram_posts'] +
            result['twitter_posts'] +
            result['linkedin_posts']
        )
        
        return result
    
    def _generate_proactive_suggestions(
        self,
        revenue: Dict,
        expenses: Dict,
        bottlenecks: List,
    ) -> List[str]:
        """Generate proactive suggestions."""
        suggestions = []
        
        # Revenue suggestions
        monthly_target = self.business_goals.get('monthly_revenue_target', 10000)
        if revenue['total_revenue'] < monthly_target * 0.5:
            suggestions.append(
                f'⚠️ Revenue is below 50% of monthly target (${monthly_target}). '
                'Consider launching a promotion or reaching out to prospects.'
            )
        
        # Expense suggestions
        if expenses['subscriptions']:
            suggestions.append(
                f'📋 Review {len(expenses["subscriptions"])} subscription(s) for potential cost savings. '
                'Cancel unused services.'
            )
        
        # Bottleneck suggestions
        if bottlenecks:
            high_severity = [b for b in bottlenecks if b.get('severity') == 'high']
            if high_severity:
                suggestions.append(
                    f'🚨 {len(high_severity)} high-priority bottleneck(s) need attention. '
                    'Review items in Needs_Action and Pending_Approval.'
                )
        
        # Task completion suggestions
        if self.business_goals:
            suggestions.append(
                '📅 Schedule weekly review meeting to assess progress on business goals.'
            )
        
        return suggestions
    
    def generate_briefing(self, period: str = 'last_week') -> Path:
        """
        Generate CEO briefing.
        
        Args:
            period: Time period (this_week, last_week, this_month, last_month)
            
        Returns:
            Path to generated briefing file
        """
        logger.info(f'Generating CEO briefing for period: {period}')
        
        # Get date range
        start_date, end_date = self._get_date_range(period)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Analyze data
        revenue = self._analyze_revenue(start_str, end_str)
        expenses = self._analyze_expenses(start_str, end_str)
        tasks = self._analyze_completed_tasks(start_str, end_str)
        bottlenecks = self._identify_bottlenecks()
        social = self._get_social_summary()
        suggestions = self._generate_proactive_suggestions(revenue, expenses, bottlenecks)
        
        # Calculate profit
        profit = revenue['total_revenue'] - expenses['total_expenses']
        
        # Generate briefing content
        timestamp = datetime.now().strftime('%Y-%m-%d')
        period_label = period.replace('_', ' ').title()
        
        content = f'''---
type: ceo_briefing
generated: {datetime.now().isoformat()}
period: {period}
date_from: {start_str}
date_to: {end_str}
---

# 📊 CEO Briefing: {period_label}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Period**: {start_str} to {end_str}

---

## 📈 Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| Revenue | ${revenue['total_revenue']:,.2f} | {"✅" if revenue['total_revenue'] > 0 else "⚠️"} |
| Expenses | ${expenses['total_expenses']:,.2f} | {"⚠️" if expenses['total_expenses'] > 0 else "✅"} |
| Profit | ${profit:,.2f} | {"✅" if profit > 0 else "⚠️"} |
| Tasks Completed | {tasks['total_completed']} | {"✅" if tasks['total_completed'] > 0 else "⚠️"} |
| Social Posts | {social['total_posts']} | {"✅" if social['total_posts'] > 0 else "⚠️"} |

---

## 💰 Revenue

**Total Revenue**: ${revenue['total_revenue']:,.2f}  
**Invoices**: {revenue['invoice_count']} ({revenue['paid_count']} paid, {revenue['pending_count']} pending)

### Top Invoices
'''
        
        # Add invoice table
        if revenue['top_invoices']:
            content += '\n| Invoice | Customer | Amount | Status |\n'
            content += '|---------|----------|--------|--------|\n'
            for inv in revenue['top_invoices'][:5]:
                status = '✅ Paid' if inv['paid'] else '⏳ Pending'
                content += f'| {inv["name"]} | {inv["customer"]} | ${inv["amount"]:,.2f} | {status} |\n'
        else:
            content += '\n*No invoices recorded this period.*\n'
        
        content += f'''
---

## 💸 Expenses

**Total Expenses**: ${expenses['total_expenses']:,.2f}  
**Expense Entries**: {expenses['expense_count']}

### Subscriptions
'''
        
        if expenses['subscriptions']:
            content += '\n| Vendor | Amount | Reference |\n'
            content += '|--------|--------|----------|\n'
            for sub in expenses['subscriptions']:
                content += f'| {sub["vendor"]} | ${sub["amount"]:,.2f} | {sub["name"]} |\n'
        else:
            content += '\n*No subscriptions detected.*\n'
        
        if expenses['alerts']:
            content += '\n### ⚠️ Alerts\n'
            for alert in expenses['alerts']:
                content += f'- {alert}\n'
        
        content += f'''
---

## ✅ Completed Tasks

**Total Completed**: {tasks['total_completed']}

### By Category
'''
        
        if tasks['by_category']:
            for category, count in sorted(tasks['by_category'].items(), key=lambda x: x[1], reverse=True):
                content += f'- **{category}**: {count}\n'
        else:
            content += '*No tasks completed this period.*\n'
        
        content += f'''
### Recent Tasks
'''
        
        if tasks['tasks']:
            for task in tasks['tasks'][:5]:
                content += f'- {task["name"]} ({task["type"]})\n'
        else:
            content += '*No recent tasks.*\n'
        
        content += f'''
---

## 🚧 Bottlenecks

'''
        
        if bottlenecks:
            content += '| Item | Type | Days Old | Severity |\n'
            content += '|------|------|----------|----------|\n'
            for b in bottlenecks[:10]:
                severity_icon = '🔴' if b['severity'] == 'high' else '🟡'
                content += f'| {b["item"]} | {b["type"]} | {b["days_old"]} | {severity_icon} |\n'
        else:
            content += '*No bottlenecks detected.*\n'
        
        content += f'''
---

## 📱 Social Media

| Platform | Posts |
|----------|-------|
| Facebook | {social['facebook_posts']} |
| Instagram | {social['instagram_posts']} |
| Twitter | {social['twitter_posts']} |
| LinkedIn | {social['linkedin_posts']} |
| **Total** | **{social['total_posts']}** |

---

## 💡 Proactive Suggestions

'''
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                content += f'{i}. {suggestion}\n\n'
        else:
            content += '*No suggestions at this time.*\n'
        
        content += f'''
---

## 📅 Upcoming Focus

> *Set your priorities for the upcoming week*

- [ ] 
- [ ] 
- [ ] 

---

*Briefing generated by AI Employee v0.3 (Gold Tier)*
'''
        
        # Save briefing
        filename = f'{timestamp}_CEO_Briefing_{period}.md'
        filepath = self.briefings_folder / filename
        filepath.write_text(content, encoding='utf-8')
        
        logger.info(f'Briefing saved to: {filepath}')
        
        return filepath


def parse_args():
    parser = argparse.ArgumentParser(description='CEO Briefing Generator')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--period', default='last_week', 
                       choices=['this_week', 'last_week', 'this_month', 'last_month', 'this_quarter'],
                       help='Time period for briefing')
    parser.add_argument('--output', help='Output file path (optional)')
    return parser.parse_args()


def main():
    args = parse_args()
    
    try:
        generator = CEOBriefingGenerator(vault_path=args.vault)
        filepath = generator.generate_briefing(period=args.period)
        
        print(f'\n✅ CEO Briefing generated successfully!')
        print(f'   Saved to: {filepath}')
        print(f'\nOpen in Obsidian to review and add your notes.')
        
        return 0
        
    except Exception as e:
        logger.error(f'Briefing generation failed: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
