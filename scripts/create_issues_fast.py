#!/usr/bin/env python3
"""
GitHub Issues 高速バッチ作成スクリプト v4.0
並列処理によりIssue作成を大幅に高速化
"""

import os
import requests
import csv
import time
import sys
import asyncio
import aiohttp
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')
BATCH_NUMBER = int(os.environ.get('BATCH_NUMBER', '1'))
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '50'))

# 高速化設定
PARALLEL_WORKERS = 8  # 同時並列リクエスト数
REQUEST_DELAY = 0.1   # リクエスト間隔（秒）- 大幅短縮
BURST_LIMIT = 20      # 一度に送信するリクエスト数

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

REPO_OWNER, REPO_NAME = GITHUB_REPOSITORY.split('/')

# GitHub API設定
API_BASE = 'https://api.github.com'
REST_HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

# GraphQL API設定
GRAPHQL_URL = 'https://api.github.com/graphql'
GRAPHQL_HEADERS = {
    'Authorization': f'Bearer {TEAM_SETUP_TOKEN}',
    'Content-Type': 'application/json'
}

# スレッドローカルセッション
thread_local = threading.local()

def get_session():
    """スレッドローカルセッションを取得"""
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
        thread_local.session.headers.update(REST_HEADERS)
    return thread_local.session

def create_single_issue(issue_data: Dict, index: int, total: int) -> Optional[Dict]:
    """単一のIssueを作成（並列処理用）"""
    session = get_session()
    
    try:
        # 短い待機でRate limit回避
        if index > 0:
            time.sleep(REQUEST_DELAY)
        
        response = session.post(
            f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
            json=issue_data,
            timeout=30
        )
        
        if response.status_code == 201:
            issue = response.json()
            print(f"  ✅ Created ({index + 1}/{total}): {issue_data['title'][:50]}...")
            return issue
        elif response.status_code == 403:
            print(f"  ⏳ Rate limit hit, retrying ({index + 1}/{total})...")
            time.sleep(2)
            # リトライ
            response = session.post(
                f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
                json=issue_data,
                timeout=30
            )
            if response.status_code == 201:
                issue = response.json()
                print(f"  ✅ Retry success ({index + 1}/{total}): {issue_data['title'][:50]}...")
                return issue
        
        print(f"  ❌ Failed ({index + 1}/{total}): {response.status_code} - {response.text[:100]}")
        return None
        
    except Exception as e:
        print(f"  ❌ Exception ({index + 1}/{total}): {str(e)}")
        return None

def create_issues_parallel(batch_data: List[Dict], issue_type: str, labels: List[str]) -> List[Dict]:
    """並列処理でIssuesを作成"""
    created_issues = []
    
    print(f"🚀 Creating {len(batch_data)} {issue_type} issues with {PARALLEL_WORKERS} parallel workers...")
    
    # Issue作成データを準備
    issue_requests = []
    for i, row in enumerate(batch_data):
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:  # タイトルが空の場合はスキップ
            print(f"  ⚠️ Skipping row {i + 1}: empty title")
            continue
            
        existing_labels = [label.strip() for label in row.get('labels', '').split(',') if label.strip()]
        all_labels = list(set(existing_labels + labels))
        
        issue_data = {
            'title': title,
            'body': body,
            'labels': all_labels
        }
        issue_requests.append((issue_data, i, len(batch_data)))
    
    if not issue_requests:
        print("  ⚠️ No valid issues to create")
        return []
    
    # 並列実行
    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        # バーストを避けるため、一定間隔でタスクを投入
        futures = []
        for i, (issue_data, index, total) in enumerate(issue_requests):
            future = executor.submit(create_single_issue, issue_data, index, total)
            futures.append(future)
            
            # バーストリミット適用
            if i > 0 and i % BURST_LIMIT == 0:
                print(f"  🔄 Burst limit reached, brief pause at {i}/{len(issue_requests)}...")
                time.sleep(1)
        
        # 結果を収集
        for future in as_completed(futures):
            try:
                issue = future.result(timeout=60)
                if issue:
                    created_issues.append(issue)
            except Exception as e:
                print(f"  ❌ Future exception: {str(e)}")
    
    print(f"🎯 Parallel creation completed: {len(created_issues)}/{len(issue_requests)} issues created")
    return created_issues

def add_issue_to_project_fast(project_id: str, issue: Dict) -> bool:
    """高速でIssueをProjectに追加"""
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
        }
    }
    """
    
    variables = {
        'projectId': project_id,
        'contentId': issue['node_id']
    }
    
    payload = {'query': query, 'variables': variables}
    
    try:
        response = requests.post(
            GRAPHQL_URL, 
            json=payload, 
            headers=GRAPHQL_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' not in data and 'data' in data:
                return True
        
        return False
    except:
        return False

def add_issues_to_project_parallel(project_id: str, issues: List[Dict], project_name: str):
    """並列処理でIssuesをProjectsに追加"""
    if not issues or not project_id:
        return
    
    print(f"🔗 Adding {len(issues)} issues to project: {project_name} (parallel)")
    
    success_count = 0
    
    def add_single_issue(issue, index, total):
        nonlocal success_count
        try:
            if add_issue_to_project_fast(project_id, issue):
                success_count += 1
                if index % 10 == 0:  # 10件ごとに進捗表示
                    print(f"    ✅ Progress: {index + 1}/{total} linked to project")
                return True
            else:
                print(f"    ❌ Failed to link: {issue['title'][:40]}...")
                return False
        except Exception as e:
            print(f"    ❌ Exception linking: {str(e)}")
            return False
    
    # 並列実行でプロジェクト追加
    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        futures = []
        for i, issue in enumerate(issues):
            if i > 0 and i % BURST_LIMIT == 0:
                time.sleep(0.5)  # GraphQL rate limit対策
            
            future = executor.submit(add_single_issue, issue, i, len(issues))
            futures.append(future)
        
        # 完了を待つ
        for future in as_completed(futures):
            try:
                future.result(timeout=30)
            except Exception as e:
                print(f"    ❌ Project linking exception: {str(e)}")
    
    print(f"🔗 Project linking completed: {success_count}/{len(issues)} issues linked to {project_name}")

def load_project_ids() -> Dict[str, str]:
    """保存されたプロジェクトIDを読み込み"""
    project_ids = {}
    try:
        with open('project_ids.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    title, project_id = line.strip().split(':', 1)
                    project_ids[title] = project_id
        print(f"📂 Loaded {len(project_ids)} project IDs")
    except FileNotFoundError:
        print("⚠️ project_ids.txt not found. Issues will be created but not linked to projects.")
    
    return project_ids

def get_csv_batch(csv_path: str, batch_number: int, batch_size: int) -> List[Dict]:
    """CSVファイルから指定バッチのデータを取得"""
    if not os.path.exists(csv_path):
        print(f"⚠️ CSV file not found: {csv_path}")
        return []
    
    start_index = (batch_number - 1) * batch_size
    end_index = start_index + batch_size
    
    print(f"📊 Reading batch {batch_number}: rows {start_index + 1} to {end_index}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
            batch_rows = all_rows[start_index:end_index]
            
            print(f"📋 Total rows in CSV: {len(all_rows)}")
            print(f"📋 Batch {batch_number} rows: {len(batch_rows)}")
            
            return batch_rows
            
    except Exception as e:
        print(f"❌ Error reading CSV {csv_path}: {str(e)}")
        return []

def main():
    """メイン処理"""
    print("=" * 60)
    print(f"🚀 FAST PARALLEL ISSUE CREATION v4.0")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: create_issues_fast.py v4.0")
    print(f"📊 Performance Configuration:")
    print(f"  • Parallel Workers: {PARALLEL_WORKERS}")
    print(f"  • Request Delay: {REQUEST_DELAY}s (vs old: 2s)")
    print(f"  • Burst Limit: {BURST_LIMIT}")
    print(f"  • Batch Number: {BATCH_NUMBER}")
    print(f"  • Batch Size: {BATCH_SIZE}")
    print("=" * 60)
    
    start_time = time.time()
    
    # プロジェクトIDを読み込み
    project_ids = load_project_ids()
    
    # タスクIssuesのバッチ処理
    print(f"\n📝 Processing task issues batch {BATCH_NUMBER} (PARALLEL)...")
    task_batch = get_csv_batch('data/tasks_for_issues.csv', BATCH_NUMBER, BATCH_SIZE)
    task_issues = []
    
    if task_batch:
        task_issues = create_issues_parallel(
            task_batch,
            'task',
            ['task', 'development']
        )
        
        # タスクプロジェクトに紐付け（並列）
        task_project_id = project_ids.get('イマココSNS（タスク）')
        if task_project_id and task_issues:
            add_issues_to_project_parallel(task_project_id, task_issues, 'イマココSNS（タスク）')
    
    # テストIssuesのバッチ処理
    print(f"\n🧪 Processing test issues batch {BATCH_NUMBER} (PARALLEL)...")
    test_batch = get_csv_batch('data/tests_for_issues.csv', BATCH_NUMBER, BATCH_SIZE)
    test_issues = []
    
    if test_batch:
        test_issues = create_issues_parallel(
            test_batch, 
            'test',
            ['test', 'qa']
        )
        
        # テストプロジェクトに紐付け（並列）
        test_project_id = project_ids.get('イマココSNS（テスト）')
        if test_project_id and test_issues:
            add_issues_to_project_parallel(test_project_id, test_issues, 'イマココSNS（テスト）')
    
    # 実行時間計算
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n⚡ FAST BATCH {BATCH_NUMBER} COMPLETED!")
    print(f"📌 Results:")
    print(f"  • {len(task_issues)} task issues created")
    print(f"  • {len(test_issues)} test issues created")
    print(f"  • Total execution time: {execution_time:.1f} seconds")
    
    # パフォーマンス比較
    old_estimated_time = (len(task_issues) + len(test_issues)) * 2 + ((len(task_issues) + len(test_issues)) // 10) * 5
    speedup = old_estimated_time / execution_time if execution_time > 0 else 1
    print(f"  • Old method would take: ~{old_estimated_time} seconds")
    print(f"  • Speed improvement: {speedup:.1f}x faster!")
    
    # バッチ完了状況をファイルに保存
    with open(f'batch_{BATCH_NUMBER}_completed_fast.txt', 'w', encoding='utf-8') as f:
        f.write(f"Fast Batch {BATCH_NUMBER} completed\n")
        f.write(f"Task issues: {len(task_issues)}\n")
        f.write(f"Test issues: {len(test_issues)}\n")
        f.write(f"Execution time: {execution_time:.1f} seconds\n")
        f.write(f"Speed improvement: {speedup:.1f}x\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return 0

if __name__ == '__main__':
    exit(main())