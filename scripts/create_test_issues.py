#!/usr/bin/env python3
"""
テストIssue作成スクリプト（順序保持・並列実行最適化版）
"""

import os
import requests
import csv
import time
import math
import random
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

# 最適化されたRate Limit設定（テストは大量のため少し保守的）
REQUEST_DELAY = 0.8      # 0.8秒間隔
BATCH_SIZE = 15          # バッチサイズ増加
BATCH_PAUSE = 8.0        # バッチ間休憩短縮
MAX_RETRIES = 10

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

# GitHub API設定
API_BASE = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

def load_test_data() -> List[Dict]:
    """テストCSVデータを読み込み"""
    print("📊 Loading test data...")
    
    test_issues = []
    csv_path = 'data/tests_for_issues.csv'
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            test_issues = [row for row in reader if row.get('title', '').strip()]
    
    print(f"📋 Loaded: {len(test_issues)} test issues")
    return test_issues

def create_single_issue(issue_data: Dict, index: int, total: int) -> Optional[Dict]:
    """単一のテストIssueを作成（順序保持）"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    if index > 0:
        time.sleep(REQUEST_DELAY)
    
    for attempt in range(MAX_RETRIES):
        try:
            response = session.post(
                f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
                json=issue_data,
                timeout=30
            )
            
            if response.status_code == 201:
                issue = response.json()
                print(f"  ✅ Test ({index + 1}/{total}): {issue_data['title'][:50]}...")
                return issue
            
            elif response.status_code == 403:
                retry_after = response.headers.get('retry-after')
                wait_time = int(retry_after) if retry_after else (30 * (attempt + 1))
                print(f"  ⏳ Rate limit, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"  ❌ Test failed ({index + 1}/{total}): {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ❌ Exception ({index + 1}/{total}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(30 * (attempt + 1))
                continue
    
    return None

def prepare_test_data(tests: List[Dict]) -> List[Dict]:
    """テストIssue作成用データを準備"""
    test_requests = []
    
    for index, row in enumerate(tests, 1):
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:
            continue
        
        # タイトル番号の整理
        if title.startswith('テスト'):
            import re
            match = re.match(r'テスト[\d\s:.]*(.+)', title)
            if match:
                clean_title = match.group(1).strip()
            else:
                clean_title = title
            numbered_title = f"テスト{index:03d}: {clean_title}"
        else:
            numbered_title = f"テスト{index:03d}: {title}"
        
        # ラベル処理
        labels_str = row.get('labels', '').strip()
        if labels_str.startswith('"') and labels_str.endswith('"'):
            labels_str = labels_str[1:-1]
        labels = [label.strip() for label in labels_str.split(',') if label.strip()]
        
        if 'test' not in labels:
            labels.append('test')
        
        issue_data = {
            'title': numbered_title,
            'body': body,
            'labels': labels
        }
        
        test_requests.append(issue_data)
    
    return test_requests

def create_test_issues_batch(issues_data: List[Dict], batch_num: int, total_batches: int) -> List[Dict]:
    """テストIssuesをバッチ作成（順序保持）"""
    created_issues = []
    
    print(f"🚀 Processing test batch {batch_num}/{total_batches} ({len(issues_data)} issues)")
    
    # 順序保持のため順次実行
    for i, issue_data in enumerate(issues_data):
        issue = create_single_issue(issue_data, i, len(issues_data))
        if issue:
            created_issues.append(issue)
    
    print(f"📊 Test batch {batch_num} result: {len(created_issues)}/{len(issues_data)} issues created")
    return created_issues

def main():
    """メイン処理"""
    print("=" * 60)
    print("🧪 TEST ISSUE CREATOR (Sequential Order Preserved)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⚙️ Settings: delay={REQUEST_DELAY}s, batch_size={BATCH_SIZE}")
    print(f"🔄 Order preservation: Sequential execution within batches")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # プロジェクトステータスチェック
        if os.path.exists('project_status.txt'):
            with open('project_status.txt', 'r') as f:
                status = f.read().strip()
            if status == 'ALL_SKIPPED':
                print("\n✅ All projects already exist. Skipping test issue creation.")
                print("💡 Projects were reused from previous setup.")
                # 空の結果ファイルを作成（後続処理のため）
                with open('test_issues_result.txt', 'w', encoding='utf-8') as f:
                    f.write("Test Issues: SKIPPED (projects already exist)\n")
                return 0
        
        # データ読み込み
        test_data = load_test_data()
        
        if not test_data:
            print("⚠️ No test issues found")
            return 0
        
        # データ準備
        test_requests = prepare_test_data(test_data)
        total_batches = math.ceil(len(test_requests) / BATCH_SIZE)
        
        print(f"📋 Processing {len(test_requests)} test issues in {total_batches} batches")
        
        # 完了予想時刻
        estimated_time = (len(test_requests) * REQUEST_DELAY + (total_batches - 1) * BATCH_PAUSE) / 60
        print(f"⏱️ Estimated completion: {estimated_time:.1f} minutes")
        
        # バッチ処理
        all_created = []
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(test_requests))
            batch_requests = test_requests[start_idx:end_idx]
            
            batch_created = create_test_issues_batch(batch_requests, batch_num + 1, total_batches)
            all_created.extend(batch_created)
            
            # 進捗表示
            progress = (len(all_created) / len(test_requests)) * 100
            print(f"📊 Overall progress: {len(all_created)}/{len(test_requests)} ({progress:.1f}%)")
            
            # バッチ間休憩
            if batch_num < total_batches - 1:
                print(f"  ⏳ Batch pause ({BATCH_PAUSE}s)...")
                time.sleep(BATCH_PAUSE)
        
        # 結果保存
        with open('test_issues_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Test Issues Created: {len(all_created)}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution time: {time.time() - start_time:.1f}s\n")
            
            for issue in all_created:
                f.write(f"{issue['number']}: {issue['title']}\n")
        
        print(f"\n✅ Test issues completed: {len(all_created)}/{len(test_requests)}")
        print(f"⏱️ Execution time: {(time.time() - start_time)/60:.1f} minutes")
        
        return 0
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())