#!/usr/bin/env python3
"""
Environment Verification Script v3.0
Checks all environment variables, files, and data integrity before setup
"""

import os
import csv
import time
from typing import Dict, List, Optional

def check_environment_variables():
    """環境変数をチェック"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'TEAM_SETUP_TOKEN',
        'GITHUB_REPOSITORY'
    ]
    
    optional_vars = [
        'BATCH_NUMBER',
        'BATCH_SIZE'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
            print(f"  ❌ {var}: Not set")
        else:
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked_value}")
    
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ℹ️ {var}: Not set (optional)")
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_csv_files():
    """CSVファイルの存在と内容をチェック"""
    print("\n📊 Checking CSV files...")
    
    csv_files = {
        'data/imakoko_sns_tables.csv': 'Database table design',
        'data/tasks_for_issues.csv': 'Task issues',
        'data/tests_for_issues.csv': 'Test issues'
    }
    
    all_files_ok = True
    total_records = 0
    
    for file_path, description in csv_files.items():
        print(f"  📄 Checking {description}: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"    ❌ File not found")
            all_files_ok = False
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                row_count = len(rows)
                total_records += row_count
                
                print(f"    ✅ Found {row_count} records")
                
                # ヘッダーチェック
                if rows:
                    headers = list(rows[0].keys())
                    print(f"    📋 Headers: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
                    
                    # サンプルレコードチェック
                    if 'title' in headers:
                        non_empty_titles = sum(1 for row in rows if row.get('title', '').strip())
                        print(f"    📝 Records with titles: {non_empty_titles}/{row_count}")
                        
                        if non_empty_titles < row_count * 0.8:  # 80%未満の場合警告
                            print(f"    ⚠️ Warning: Many records have empty titles")
                
        except Exception as e:
            print(f"    ❌ Error reading file: {str(e)}")
            all_files_ok = False
    
    print(f"\n📊 Total records across all CSV files: {total_records}")
    
    if all_files_ok:
        print("✅ All CSV files are accessible and contain data")
    else:
        print("❌ Some CSV files have issues")
    
    return all_files_ok

def check_directory_structure():
    """ディレクトリ構造をチェック"""
    print("\n📁 Checking directory structure...")
    
    required_dirs = ['scripts', 'data']
    optional_dirs = ['wiki', '.github/workflows']
    
    all_dirs_ok = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            print(f"  ✅ {dir_path}: Exists ({file_count} files)")
        else:
            print(f"  ❌ {dir_path}: Not found")
            all_dirs_ok = False
    
    for dir_path in optional_dirs:
        if os.path.exists(dir_path):
            file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            print(f"  ✅ {dir_path}: Exists ({file_count} files)")
        else:
            print(f"  ℹ️ {dir_path}: Not found (optional)")
    
    return all_dirs_ok

def check_workflow_files():
    """ワークフローファイルをチェック"""
    print("\n⚙️ Checking workflow files...")
    
    workflow_dir = '.github/workflows'
    if not os.path.exists(workflow_dir):
        print(f"  ❌ Workflow directory not found: {workflow_dir}")
        return False
    
    workflow_files = [f for f in os.listdir(workflow_dir) if f.endswith('.yml') or f.endswith('.yaml')]
    
    if not workflow_files:
        print(f"  ❌ No workflow files found in {workflow_dir}")
        return False
    
    print(f"  📋 Found {len(workflow_files)} workflow files:")
    for file in sorted(workflow_files):
        file_path = os.path.join(workflow_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"    • {file} ({file_size} bytes)")
    
    # Check for the main workflow
    main_workflow = 'team-setup.yml'
    if main_workflow in workflow_files:
        print(f"  ✅ Main workflow found: {main_workflow}")
    else:
        print(f"  ⚠️ Main workflow not found: {main_workflow}")
        print(f"    Available workflows: {', '.join(workflow_files)}")
    
    return True

def estimate_processing_requirements():
    """処理要件を見積もり"""
    print("\n📈 Estimating processing requirements...")
    
    try:
        # タスクIssues数を確認
        task_count = 0
        if os.path.exists('data/tasks_for_issues.csv'):
            with open('data/tasks_for_issues.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                task_rows = [row for row in reader if row.get('title', '').strip()]
                task_count = len(task_rows)
        
        # テストIssues数を確認
        test_count = 0
        if os.path.exists('data/tests_for_issues.csv'):
            with open('data/tests_for_issues.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                test_rows = [row for row in reader if row.get('title', '').strip()]
                test_count = len(test_rows)
        
        total_issues = task_count + test_count
        
        print(f"  📝 Task issues to create: {task_count}")
        print(f"  🧪 Test issues to create: {test_count}")
        print(f"  📊 Total issues to create: {total_issues}")
        
        # バッチ数を計算
        batch_size = int(os.environ.get('BATCH_SIZE', '50'))
        required_batches = (total_issues + batch_size - 1) // batch_size  # 切り上げ
        
        print(f"  📦 Batch size: {batch_size}")
        print(f"  🔄 Required batches: {required_batches}")
        
        # 推定実行時間
        estimated_time_per_issue = 3  # 秒（Rate limit考慮）
        estimated_total_time = total_issues * estimated_time_per_issue
        estimated_minutes = estimated_total_time // 60
        
        print(f"  ⏱️ Estimated processing time: {estimated_minutes} minutes ({estimated_total_time} seconds)")
        
        if total_issues > 200:
            print(f"  ⚠️ Warning: Large number of issues may hit GitHub rate limits")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error estimating requirements: {str(e)}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("🔍 ENVIRONMENT VERIFICATION v3.0")
    print("=" * 60)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🔧 Script: verify_environment.py v3.0")
    print("=" * 60)
    
    # All verification checks
    checks = [
        ("Environment Variables", check_environment_variables),
        ("CSV Files", check_csv_files),
        ("Directory Structure", check_directory_structure),
        ("Workflow Files", check_workflow_files),
        ("Processing Requirements", estimate_processing_requirements)
    ]
    
    all_passed = True
    results = {}
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"\n❌ Error during {check_name} check: {str(e)}")
            results[check_name] = False
            all_passed = False
    
    print("\n" + "=" * 60)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {check_name}")
    
    if all_passed:
        print("\n🎉 All verification checks passed!")
        print("✅ Environment is ready for team setup")
        return 0
    else:
        print("\n⚠️ Some verification checks failed!")
        print("❌ Please fix the issues before running team setup")
        return 1

if __name__ == '__main__':
    exit(main())