"""
Silver Tier Verification Script

Verifies all Silver Tier components are properly installed and working.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def check_python_version():
    """Check Python version is 3.13+"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 13):
        print("  [WARN] Python 3.13+ recommended")
        return False
    print("  [OK] Python version OK")
    return True


def check_dependencies():
    """Check required Python packages"""
    print("\nChecking dependencies...")
    
    deps = {
        ('google.auth', 'googleapiclient'): 'Gmail API',
        'google_auth_oauthlib': 'Gmail OAuth',
        'playwright': 'Browser automation',
        'watchdog': 'File system watching',
    }
    
    all_ok = True
    for package, info in deps.items():
        if isinstance(package, tuple):
            import_names = package
            purpose = info
        else:
            import_names = (package,)
            purpose = info
        
        found = False
        for name in import_names:
            try:
                # Try different import styles
                import_name = name.replace('.', '_').replace('-', '_')
                __import__(import_name)
                found = True
                break
            except ImportError:
                try:
                    __import__(name)
                    found = True
                    break
                except ImportError:
                    continue
        
        if found:
            print(f"  [OK] {purpose}")
        else:
            print(f"  [MISSING] {purpose}")
            all_ok = False
    
    return all_ok


def check_skills():
    """Check Silver Tier skills"""
    print("\nChecking Silver Tier skills...")
    
    skills = [
        'gmail-watcher',
        'whatsapp-watcher',
        'email-mcp',
        'approval-workflow',
        'linkedin-poster',
        'plan-manager',
    ]
    
    base_path = Path('.qwen/skills')
    all_ok = True
    
    for skill in skills:
        skill_path = base_path / skill
        if skill_path.exists():
            print(f"  [OK] {skill}")
        else:
            print(f"  [MISSING] {skill}")
            all_ok = False
    
    return all_ok


def check_vault_structure(vault_path: Path):
    """Check vault directory structure"""
    print(f"\nChecking vault structure at {vault_path}...")
    
    required_dirs = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Done/LinkedIn',
        'Done/Email',
        'Plans',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Briefings',
        'Accounting',
        'Logs',
        'Scripts',
    ]
    
    all_ok = True
    for directory in required_dirs:
        dir_path = vault_path / directory
        if dir_path.exists() and dir_path.is_dir():
            print(f"  [OK] {directory}/")
        else:
            print(f"  [MISSING] {directory}/")
            all_ok = False
    
    return all_ok


def check_vault_files(vault_path: Path):
    """Check required vault files"""
    print("\nChecking vault files...")
    
    required_files = [
        ('Dashboard.md', 'Main dashboard'),
        ('Company_Handbook.md', 'Rules of engagement'),
        ('Business_Goals.md', 'Objectives and metrics'),
    ]
    
    all_ok = True
    for filename, description in required_files:
        file_path = vault_path / filename
        if file_path.exists():
            print(f"  [OK] {filename} - {description}")
        else:
            print(f"  [MISSING] {filename} - {description}")
            all_ok = False
    
    return all_ok


def check_gmail_auth(vault_path: Path):
    """Check Gmail authentication"""
    print("\nChecking Gmail authentication...")
    
    token_path = vault_path / 'Scripts' / 'token.json'
    credentials_path = Path('credentials.json')
    
    if not credentials_path.exists():
        print("  [MISSING] credentials.json")
        return False
    
    if token_path.exists():
        print(f"  [OK] Gmail token exists")
        return True
    else:
        print("  [WARN] Gmail token not found - authentication needed")
        print("         Run: python .qwen/skills/gmail-watcher/scripts/gmail_auth.py")
        return False


def check_scripts():
    """Check Silver Tier scripts"""
    print("\nChecking Silver Tier scripts...")
    
    scripts = [
        ('.qwen/skills/gmail-watcher/scripts/gmail_watcher.py', 'Gmail Watcher'),
        ('.qwen/skills/gmail-watcher/scripts/gmail_auth.py', 'Gmail Auth'),
        ('.qwen/skills/whatsapp-watcher/scripts/whatsapp_watcher.py', 'WhatsApp Watcher'),
        ('.qwen/skills/linkedin-poster/scripts/linkedin_poster.py', 'LinkedIn Poster'),
        ('.qwen/skills/plan-manager/scripts/plan_manager.py', 'Plan Manager'),
        ('.qwen/skills/approval-workflow/scripts/approval_workflow.py', 'Approval Workflow'),
    ]
    
    all_ok = True
    for script_path, description in scripts:
        if Path(script_path).exists():
            print(f"  [OK] {description}")
        else:
            print(f"  [MISSING] {description}")
            all_ok = False
    
    return all_ok


def test_gmail_watcher(vault_path: Path):
    """Test Gmail Watcher import"""
    print("\nTesting Gmail Watcher...")
    
    # Add correct paths
    sys.path.insert(0, str(Path('.qwen/skills/gmail-watcher/scripts').resolve()))
    sys.path.insert(0, str((vault_path / 'Scripts').resolve()))
    
    try:
        import gmail_watcher
        print("  [OK] Gmail Watcher imports OK")
        return True
    except Exception as e:
        print(f"  [FAIL] Gmail Watcher import failed: {e}")
        return False


def test_plan_manager(vault_path: Path):
    """Test Plan Manager"""
    print("\nTesting Plan Manager...")
    
    sys.path.insert(0, str(Path('.qwen/skills/plan-manager/scripts').resolve()))
    
    try:
        from plan_manager import PlanManager
        manager = PlanManager(str(vault_path))
        print("  [OK] Plan Manager imports OK")
        return True
    except Exception as e:
        print(f"  [FAIL] Plan Manager import failed: {e}")
        return False


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("AI Employee - Silver Tier Verification")
    print("=" * 60)
    
    # Determine vault path
    vault_path = Path('./AI_Employee_Vault').resolve()
    
    results = []
    
    # Run checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Silver Tier Skills", check_skills()))
    results.append(("Scripts", check_scripts()))
    results.append(("Vault Structure", check_vault_structure(vault_path)))
    results.append(("Vault Files", check_vault_files(vault_path)))
    results.append(("Gmail Auth", check_gmail_auth(vault_path)))
    results.append(("Gmail Watcher", test_gmail_watcher(vault_path)))
    results.append(("Plan Manager", test_plan_manager(vault_path)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] All checks passed! Silver Tier is ready.")
        print("\nNext steps:")
        print("  1. Start watchers: silver-tier\\start-watchers.bat")
        print("  2. Open AI_Employee_Vault in Obsidian")
        print("  3. Drop a file in Inbox/ or wait for Gmail")
        print("  4. Process with Qwen Code")
    else:
        print("\n[WARN] Some checks failed. Please review and fix issues.")
        if not results[6][1]:  # Gmail auth failed
            print("\nTo authenticate Gmail:")
            print("  python .qwen/skills/gmail-watcher/scripts/gmail_auth.py --vault ./AI_Employee_Vault")
    
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
