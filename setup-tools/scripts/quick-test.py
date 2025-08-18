#!/usr/bin/env python3
"""
Quick test script to verify the team setup works correctly
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_csv_parsing():
    """Test CSV to Issues conversion"""
    print("🧪 Testing CSV parsing...")
    
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / 'data' / 'sample-tasks.csv'
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    # Test dry run
    result = subprocess.run([
        'python3', script_dir / 'csv-to-issues.py',
        '--csv', str(csv_path.relative_to(script_dir.parent)),
        '--repo', 'test/repo', 
        '--token', 'fake_token',
        '--dry-run'
    ], cwd=script_dir.parent, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ CSV parsing test passed")
        return True
    else:
        print(f"❌ CSV parsing test failed: {result.stderr}")
        return False

def test_wiki_templates():
    """Test Wiki template generation"""
    print("🧪 Testing Wiki templates...")
    
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / 'templates' / 'wiki'
    
    if not template_dir.exists():
        print(f"❌ Wiki templates not found: {template_dir}")
        return False
    
    # Check template files exist
    required_files = ['table-design.md']
    for file_name in required_files:
        file_path = template_dir / file_name
        if not file_path.exists():
            print(f"❌ Template file missing: {file_name}")
            return False
    
    print("✅ Wiki templates test passed")
    return True

def test_discussions_templates():
    """Test Discussions template generation"""
    print("🧪 Testing Discussions templates...")
    
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / 'templates' / 'discussions'
    
    if not template_dir.exists():
        print(f"❌ Discussions templates not found: {template_dir}")
        return False
    
    # Check template files exist
    required_files = ['meeting-template.md']
    for file_name in required_files:
        file_path = template_dir / file_name
        if not file_path.exists():
            print(f"❌ Template file missing: {file_name}")
            return False
    
    print("✅ Discussions templates test passed")
    return True

def test_script_permissions():
    """Test script permissions"""
    print("🧪 Testing script permissions...")
    
    script_dir = Path(__file__).parent
    setup_script = script_dir / 'setup.sh'
    
    if not setup_script.exists():
        print(f"❌ Setup script not found: {setup_script}")
        return False
    
    # Check if script is executable
    if not os.access(setup_script, os.X_OK):
        print(f"❌ Setup script is not executable: {setup_script}")
        print("   Run: chmod +x setup-tools/scripts/setup.sh")
        return False
    
    print("✅ Script permissions test passed")
    return True

def test_requirements():
    """Test Python requirements"""
    print("🧪 Testing Python requirements...")
    
    script_dir = Path(__file__).parent
    req_file = script_dir.parent / 'requirements.txt'
    
    if not req_file.exists():
        print(f"❌ Requirements file not found: {req_file}")
        return False
    
    # Test requirements parsing
    try:
        with open(req_file, 'r') as f:
            requirements = f.read()
        
        required_packages = ['requests', 'pandas', 'PyGithub', 'python-dotenv', 'pyyaml']
        for package in required_packages:
            if package not in requirements:
                print(f"❌ Missing required package: {package}")
                return False
        
        print("✅ Requirements test passed")
        return True
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def test_github_workflow():
    """Test GitHub Actions workflow"""
    print("🧪 Testing GitHub Actions workflow...")
    
    script_dir = Path(__file__).parent
    workflow_file = script_dir.parent.parent / '.github' / 'workflows' / 'team-setup.yml'
    
    if not workflow_file.exists():
        print(f"❌ Workflow file not found: {workflow_file}")
        return False
    
    # Basic YAML parsing test
    try:
        import yaml
        with open(workflow_file, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        if 'name' not in workflow_data:
            print("❌ Workflow missing 'name' field")
            return False
        
        if 'on' not in workflow_data:
            print("❌ Workflow missing 'on' field")
            return False
        
        if 'jobs' not in workflow_data:
            print("❌ Workflow missing 'jobs' field")
            return False
        
        print("✅ GitHub Actions workflow test passed")
        return True
    except ImportError:
        print("⚠️  YAML library not available, skipping workflow validation")
        return True
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Running Team Setup Tests...\n")
    
    tests = [
        test_requirements,
        test_script_permissions,
        test_csv_parsing,
        test_wiki_templates,
        test_discussions_templates,
        test_github_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The setup system is ready to use.")
        print("\n📋 Next steps:")
        print("1. Set TEAM_SETUP_TOKEN and GITHUB_REPO environment variables")
        print("2. Run: ./setup-tools/scripts/setup.sh --dry-run")
        print("3. If dry run looks good, run: ./setup-tools/scripts/setup.sh")
        print("4. Or use the GitHub Actions workflow for one-click setup")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)