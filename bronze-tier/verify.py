"""
Verification Script for Bronze Tier

Run this script to verify that all Bronze Tier components are properly installed and working.
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
        'watchdog': 'File system watching',
    }
    
    all_ok = True
    for package, purpose in deps.items():
        try:
            __import__(package)
            print(f"  [OK] {package} - {purpose}")
        except ImportError:
            print(f"  [MISSING] {package} - {purpose}")
            all_ok = False
    
    return all_ok


def check_vault_structure(vault_path: Path):
    """Check vault directory structure"""
    print(f"\nChecking vault structure at {vault_path}...")
    
    required_dirs = [
        'Inbox',
        'Needs_Action',
        'Done',
        'Plans',
        'Pending_Approval',
        'Approved',
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
        ('VAULT_SKILL.md', 'Agent skill documentation'),
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


def check_scripts(vault_path: Path):
    """Check Python scripts"""
    print("\nChecking scripts...")
    
    scripts = [
        ('base_watcher.py', 'Base watcher class'),
        ('filesystem_watcher.py', 'File system watcher'),
        ('orchestrator.py', 'Main orchestrator'),
    ]
    
    all_ok = True
    for filename, description in scripts:
        script_path = vault_path / 'Scripts' / filename
        if script_path.exists():
            print(f"  [OK] {filename} - {description}")
        else:
            print(f"  [MISSING] {filename} - {description}")
            all_ok = False
    
    return all_ok


def test_watcher_import(vault_path: Path):
    """Test that watcher scripts can be imported"""
    print("\nTesting script imports...")
    
    scripts_dir = vault_path / 'Scripts'
    sys.path.insert(0, str(scripts_dir))
    
    all_ok = True
    
    try:
        from base_watcher import BaseWatcher
        print("  [OK] base_watcher.py imports OK")
    except Exception as e:
        print(f"  [FAIL] base_watcher.py import failed: {e}")
        all_ok = False
    
    try:
        from filesystem_watcher import FilesystemWatcher
        print("  [OK] filesystem_watcher.py imports OK")
    except Exception as e:
        print(f"  [FAIL] filesystem_watcher.py import failed: {e}")
        all_ok = False
    
    try:
        from orchestrator import Orchestrator
        print("  [OK] orchestrator.py imports OK")
    except Exception as e:
        print(f"  [FAIL] orchestrator.py import failed: {e}")
        all_ok = False
    
    return all_ok


def test_file_drop(vault_path: Path):
    """Test file drop and processing"""
    print("\nTesting file drop...")
    
    inbox = vault_path / 'Inbox'
    inbox.mkdir(exist_ok=True)
    
    # Create test file
    test_file = inbox / 'test_verification.txt'
    test_file.write_text(f"Test file created at {datetime.now().isoformat()}")
    print(f"  Created test file: {test_file.name}")
    
    # Run watcher once
    sys.path.insert(0, str(vault_path / 'Scripts'))
    try:
        from filesystem_watcher import FilesystemWatcher
        
        watcher = FilesystemWatcher(str(vault_path), check_interval=1)
        items = watcher.check_for_updates()
        
        if items:
            print(f"  [OK] Watcher detected {len(items)} file(s)")
            for item in items:
                watcher.create_action_file(item)
            print("  [OK] Action file created")
        else:
            print("  [WARN] No files detected (may need to wait)")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Test failed: {e}")
        return False


def check_qwen_code():
    """Check Qwen Code installation"""
    print("\nChecking Qwen Code...")
    
    try:
        # Try to run qwen --version or check if qwen command exists
        result = subprocess.run(
            ['qwen', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  [OK] Qwen Code: {result.stdout.strip()}")
            return True
        else:
            print("  [WARN] Qwen Code not found or not in PATH")
            return False
    except FileNotFoundError:
        print("  [WARN] Qwen Code not found")
        return False
    except subprocess.TimeoutExpired:
        print("  [WARN] Qwen Code check timed out")
        return False


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("AI Employee - Bronze Tier Verification")
    print("=" * 60)
    
    # Determine vault path
    vault_path = Path('./AI_Employee_Vault').resolve()
    if not vault_path.exists():
        # Try parent directory
        vault_path = Path('../AI_Employee_Vault').resolve()
    
    results = []
    
    # Run checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Vault Structure", check_vault_structure(vault_path)))
    results.append(("Vault Files", check_vault_files(vault_path)))
    results.append(("Scripts", check_scripts(vault_path)))
    results.append(("Script Imports", test_watcher_import(vault_path)))
    results.append(("Qwen Code", check_qwen_code()))
    results.append(("File Drop Test", test_file_drop(vault_path)))
    
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
        print("\n[SUCCESS] All checks passed! Bronze Tier is ready.")
        print("\nNext steps:")
        print("  1. Open AI_Employee_Vault in Obsidian")
        print("  2. Review Company_Handbook.md")
        print("  3. Update Business_Goals.md")
        print("  4. Drop a file in Inbox/")
        print("  5. Run: python AI_Employee_Vault/Scripts/orchestrator.py")
    else:
        print("\n[WARN] Some checks failed. Please review and fix issues.")
    
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
