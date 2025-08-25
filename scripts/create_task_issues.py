#!/usr/bin/env python3
"""
タスクIssue作成スクリプト（並列実行最適化版）
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

# Rate Limit設定（保守的）
REQUEST_DELAY = 1.5      # 1.5秒間隔（Rate制限回避）
BATCH_SIZE = 10          # 小さめのバッチ
BATCH_PAUSE = 15.0       # 長めの休憩
MAX_RETRIES = 5          # リトライ回数削減

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

# GitHub API設定
API_BASE = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

def load_task_data() -> List[Dict]:
    """タスクCSVデータを読み込み"""
    print("📊 Loading task data...")
    
    task_issues = []
    csv_path = 'data/tasks_for_issues.csv'
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            task_issues = [row for row in reader if row.get('title', '').strip()]
    
    print(f"📋 Loaded: {len(task_issues)} task issues")
    return task_issues

def create_single_issue(issue_data: Dict, index: int, total: int) -> Optional[Dict]:
    """単一のタスクIssueを作成"""
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
                print(f"  ✅ Task ({index + 1}/{total}): {issue_data['title'][:50]}...")
                return issue
            
            elif response.status_code == 403:
                retry_after = response.headers.get('retry-after')
                if retry_after:
                    wait_time = int(retry_after) + 10  # 余裕を持たせる
                else:
                    wait_time = 60  # デフォルト60秒待機
                remaining = response.headers.get('x-ratelimit-remaining', 'unknown')
                print(f"  ⏳ Rate limit hit (remaining: {remaining}), waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"  ❌ Task failed ({index + 1}/{total}): {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ❌ Exception ({index + 1}/{total}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(30 * (attempt + 1))
                continue
    
    return None

def prepare_task_data(tasks: List[Dict]) -> List[Dict]:
    """タスクIssue作成用データを準備"""
    task_requests = []
    
    for index, row in enumerate(tasks, 1):
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:
            continue
        
        # タイトル番号の整理
        if title.startswith('タスク'):
            import re
            match = re.match(r'タスク[\d\s:.]*(.+)', title)
            if match:
                clean_title = match.group(1).strip()
            else:
                clean_title = title
            numbered_title = f"タスク{index:03d}: {clean_title}"
        else:
            numbered_title = f"タスク{index:03d}: {title}"
        
        # ラベル処理
        labels_str = row.get('labels', '').strip()
        if labels_str.startswith('"') and labels_str.endswith('"'):
            labels_str = labels_str[1:-1]
        labels = [label.strip() for label in labels_str.split(',') if label.strip()]
        
        if 'task' not in labels:
            labels.append('task')
        
        issue_data = {
            'title': numbered_title,
            'body': body,
            'labels': labels
        }
        
        task_requests.append(issue_data)
    
    return task_requests

def create_task_issues_batch(issues_data: List[Dict], batch_num: int, total_batches: int, start_time: float) -> List[Dict]:
    """タスクIssuesをバッチ作成"""
    created_issues = []
    
    print(f"🚀 Processing task batch {batch_num}/{total_batches} ({len(issues_data)} issues)")
    
    for i, issue_data in enumerate(issues_data):
        issue = create_single_issue(issue_data, i, len(issues_data))
        if issue:
            created_issues.append(issue)
        
        # 進捗表示（タイムアウト防止）
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start_time
            print(f"  📊 Progress: {i + 1}/{len(issues_data)} in batch {batch_num} - Elapsed: {elapsed:.1f}s")
    
    print(f"📊 Task batch {batch_num} result: {len(created_issues)}/{len(issues_data)} issues created")
    return created_issues

def main():
    """メイン処理"""
    print("=" * 60)
    print("📋 TASK ISSUE CREATOR (Parallel Optimized)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⚙️ Settings: delay={REQUEST_DELAY}s, batch_size={BATCH_SIZE}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # プロジェクトステータスチェック
        if os.path.exists('project_status.txt'):
            with open('project_status.txt', 'r') as f:
                status = f.read().strip()
            if status == 'ALL_SKIPPED':
                print("\n✅ All projects already exist. Skipping task issue creation.")
                print("💡 Projects were reused from previous setup.")
                # 空の結果ファイルを作成（後続処理のため）
                with open('task_issues_result.txt', 'w', encoding='utf-8') as f:
                    f.write("Task Issues: SKIPPED (projects already exist)\n")
                return 0
        
        # データ読み込み
        task_data = load_task_data()
        
        if not task_data:
            print("⚠️ No task issues found")
            return 0
        
        # データ準備
        task_requests = prepare_task_data(task_data)
        total_batches = math.ceil(len(task_requests) / BATCH_SIZE)
        
        print(f"📋 Processing {len(task_requests)} task issues in {total_batches} batches")
        
        # バッチ処理
        all_created = []
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(task_requests))
            batch_requests = task_requests[start_idx:end_idx]
            
            batch_created = create_task_issues_batch(batch_requests, batch_num + 1, total_batches, start_time)
            all_created.extend(batch_created)
            
            # バッチ間休憩
            if batch_num < total_batches - 1:
                print(f"  ⏳ Batch pause ({BATCH_PAUSE}s)...")
                time.sleep(BATCH_PAUSE)
        
        # 結果保存
        with open('task_issues_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Task Issues Created: {len(all_created)}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution time: {time.time() - start_time:.1f}s\n")
            
            for issue in all_created:
                f.write(f"{issue['number']}: {issue['title']}\n")
        
        print(f"\n✅ Task issues completed: {len(all_created)}/{len(task_requests)}")
        print(f"⏱️ Execution time: {time.time() - start_time:.1f}s")
        
        return 0
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())