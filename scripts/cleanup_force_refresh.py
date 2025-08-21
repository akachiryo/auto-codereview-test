#!/usr/bin/env python3
"""
Force Cleanup and Refresh Script v3.0
Cleans up any cached or temporary files and prepares for fresh execution
"""

import os
import shutil
import glob
import time
from typing import List

def remove_files(pattern_list: List[str], description: str):
    """指定されたパターンのファイルを削除"""
    print(f"🧹 Cleaning {description}...")
    removed_count = 0
    
    for pattern in pattern_list:
        matching_files = glob.glob(pattern)
        for file_path in matching_files:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"  ✅ Removed file: {file_path}")
                    removed_count += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"  ✅ Removed directory: {file_path}")
                    removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {file_path}: {str(e)}")
    
    if removed_count == 0:
        print(f"  ℹ️ No {description} found to clean")
    else:
        print(f"  🎯 Removed {removed_count} items")

def clean_temporary_files():
    """一時ファイルを削除"""
    temp_patterns = [
        "project_ids.txt",
        "batch_*_completed.txt",
        "*.tmp",
        "*.cache",
        "*.log",
        "__pycache__",
        "*.pyc",
        ".DS_Store"
    ]
    
    remove_files(temp_patterns, "temporary files")

def clean_generated_content():
    """生成されたコンテンツを削除"""
    generated_patterns = [
        "wiki",
        "wiki_repository",
        "*.wiki"
    ]
    
    remove_files(generated_patterns, "generated content")

def clean_github_caches():
    """GitHub関連のキャッシュファイルを削除"""
    cache_patterns = [
        ".github/workflows/*.cache",
        ".github/workflows/*.tmp",
        ".github/workflows/.*",
    ]
    
    # .gitignoreなどの重要なファイルは除外
    important_files = [".gitignore", ".gitattributes"]
    
    print("🧹 Cleaning GitHub caches...")
    removed_count = 0
    
    for pattern in cache_patterns:
        matching_files = glob.glob(pattern)
        for file_path in matching_files:
            file_name = os.path.basename(file_path)
            if file_name not in important_files:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"  ✅ Removed cache: {file_path}")
                        removed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to remove {file_path}: {str(e)}")
    
    if removed_count == 0:
        print("  ℹ️ No GitHub caches found to clean")
    else:
        print(f"  🎯 Removed {removed_count} cache items")

def verify_essential_files():
    """必須ファイルの存在確認"""
    print("🔍 Verifying essential files...")
    
    essential_files = {
        ".github/workflows/team-setup.yml": "Main workflow file",
        "scripts/create_projects.py": "Projects creation script",
        "scripts/setup_discussions.py": "Discussions setup script", 
        "scripts/setup_wiki.py": "Wiki setup script",
        "scripts/create_issues_batch.py": "Issues batch creation script",
        "scripts/verify_environment.py": "Environment verification script",
        "data/imakoko_sns_tables.csv": "Database tables CSV",
        "data/tasks_for_issues.csv": "Task issues CSV",
        "data/tests_for_issues.csv": "Test issues CSV"
    }
    
    missing_files = []
    for file_path, description in essential_files.items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {description}: {file_path} ({file_size} bytes)")
        else:
            print(f"  ❌ {description}: {file_path} (MISSING)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ WARNING: {len(missing_files)} essential files are missing!")
        for missing in missing_files:
            print(f"  • {missing}")
        return False
    else:
        print("\n✅ All essential files are present")
        return True

def create_fresh_start_marker():
    """新しい実行のマーカーファイルを作成"""
    print("🆕 Creating fresh start marker...")
    
    marker_content = f"""# Fresh Start Marker v3.0
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Version: v3.0 (CONSOLIDATED)
Action: Force cleanup completed

This marker indicates that force cleanup was run and the environment
is ready for fresh execution of team-setup.yml v3.0.

All temporary files, caches, and generated content have been removed.
"""
    
    try:
        with open('FRESH_START_MARKER.txt', 'w', encoding='utf-8') as f:
            f.write(marker_content)
        print(f"  ✅ Created: FRESH_START_MARKER.txt")
    except Exception as e:
        print(f"  ❌ Failed to create marker: {str(e)}")

def display_cleanup_summary():
    """クリーンアップ結果のサマリーを表示"""
    print("\n" + "=" * 60)
    print("📋 CLEANUP SUMMARY")
    print("=" * 60)
    
    print("✅ Completed cleanup tasks:")
    print("  • Temporary files removed")
    print("  • Generated content cleaned")
    print("  • GitHub caches cleared")
    print("  • Fresh start marker created")
    
    print("\n🎯 Next steps:")
    print("  1. Run the team-setup.yml workflow manually")
    print("  2. Monitor the logs for v3.0 version confirmation")
    print("  3. Verify all issues are created without limits")
    
    print("\n💡 If you still see old error messages:")
    print("  • Check that you're running from the correct branch")
    print("  • Verify the workflow file is team-setup.yml (not old ones)")
    print("  • Look for 'v3.0 (CONSOLIDATED)' in the workflow logs")

def main():
    """メイン処理"""
    print("=" * 60)
    print("🧹 FORCE CLEANUP & REFRESH v3.0")
    print("=" * 60)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🔧 Script: cleanup_force_refresh.py v3.0")
    print("=" * 60)
    print("\n🎯 This script will:")
    print("  • Remove all temporary and cache files")
    print("  • Clean generated content")
    print("  • Verify essential files are present")
    print("  • Create fresh start marker")
    print("=" * 60)
    
    try:
        # Step 1: Clean temporary files
        clean_temporary_files()
        print()
        
        # Step 2: Clean generated content
        clean_generated_content()
        print()
        
        # Step 3: Clean GitHub caches
        clean_github_caches()
        print()
        
        # Step 4: Verify essential files
        files_ok = verify_essential_files()
        print()
        
        # Step 5: Create fresh start marker
        if files_ok:
            create_fresh_start_marker()
        else:
            print("⚠️ Skipping marker creation due to missing essential files")
        
        # Step 6: Display summary
        display_cleanup_summary()
        
        if files_ok:
            print("\n🎉 Force cleanup completed successfully!")
            print("✅ Environment is ready for fresh team setup execution")
            return 0
        else:
            print("\n⚠️ Cleanup completed with warnings!")
            print("❌ Some essential files are missing - please restore them")
            return 1
            
    except Exception as e:
        print(f"\n💥 Unexpected error during cleanup: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    exit(main())