#!/usr/bin/env python3
"""
GitHub Issues 全自動作成スクリプト v4.1 (SMART)
すべてのIssueを1つのスクリプトで動的に処理
依存関係：標準ライブラリのみ使用
"""

import os
import requests
import csv
import time
import sys
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import math

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

# 動的設定
PARALLEL_WORKERS = 6     # 並列数を少し下げて安定性向上
REQUEST_DELAY = 0.2      # 少し長めにしてRate Limit回避
BATCH_SIZE = 50          # バッチサイズ
BURST_LIMIT = 15         # バーストリミット

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

def load_all_csv_data() -> Tuple[List[Dict], List[Dict]]:
    """全てのCSVデータを読み込み"""
    print("📊 Loading all CSV data...")
    
    # タスクIssues
    task_issues = []
    task_csv_path = 'data/tasks_for_issues.csv'
    if os.path.exists(task_csv_path):
        with open(task_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            task_issues = [row for row in reader if row.get('title', '').strip()]
    
    # テストIssues
    test_issues = []
    test_csv_path = 'data/tests_for_issues.csv'
    if os.path.exists(test_csv_path):
        with open(test_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            test_issues = [row for row in reader if row.get('title', '').strip()]
    
    print(f"📋 Loaded: {len(task_issues)} task issues, {len(test_issues)} test issues")
    print(f"📊 Total: {len(task_issues) + len(test_issues)} issues to create")
    
    return task_issues, test_issues

def calculate_batches(total_count: int, batch_size: int) -> int:
    """必要なバッチ数を計算"""
    return math.ceil(total_count / batch_size)

def create_single_issue(issue_data: Dict, index: int, total: int, issue_type: str) -> Optional[Dict]:
    """単一のIssueを作成"""
    session = get_session()
    
    try:
        if index > 0:
            time.sleep(REQUEST_DELAY)
        
        response = session.post(
            f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
            json=issue_data,
            timeout=30
        )
        
        if response.status_code == 201:
            issue = response.json()
            print(f"  ✅ {issue_type} ({index + 1}/{total}): {issue_data['title'][:50]}...")
            return issue
        elif response.status_code == 403:
            print(f"  ⏳ Rate limit hit, retrying ({index + 1}/{total})...")
            time.sleep(3)
            response = session.post(
                f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
                json=issue_data,
                timeout=30
            )
            if response.status_code == 201:
                issue = response.json()
                print(f"  ✅ {issue_type} retry ({index + 1}/{total}): {issue_data['title'][:50]}...")
                return issue
        
        print(f"  ❌ {issue_type} failed ({index + 1}/{total}): {response.status_code}")
        return None
        
    except Exception as e:
        print(f"  ❌ {issue_type} exception ({index + 1}/{total}): {str(e)}")
        return None

def create_issues_batch(issues_data: List[Tuple], batch_num: int, total_batches: int) -> List[Dict]:
    """1つのバッチでIssueを作成"""
    created_issues = []
    
    if not issues_data:
        return created_issues
    
    print(f"🚀 Processing batch {batch_num}/{total_batches} ({len(issues_data)} issues)")
    
    # 並列実行
    with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
        futures = []
        for i, (issue_data, issue_type) in enumerate(issues_data):
            future = executor.submit(create_single_issue, issue_data, i, len(issues_data), issue_type)
            futures.append(future)
            
            # バーストリミット
            if i > 0 and i % BURST_LIMIT == 0:
                time.sleep(0.5)
        
        # 結果収集
        for future in as_completed(futures):
            try:
                issue = future.result(timeout=60)
                if issue:
                    created_issues.append(issue)
            except Exception as e:
                print(f"  ❌ Future exception: {str(e)}")
    
    print(f"📊 Batch {batch_num} result: {len(created_issues)}/{len(issues_data)} issues created")
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

def link_issues_to_projects(task_issues: List[Dict], test_issues: List[Dict], project_ids: Dict[str, str]):
    """IssueをProjectsにリンク"""
    print("\n🔗 Linking issues to projects...")
    
    def link_batch(issues: List[Dict], project_id: str, project_name: str, issue_type: str):
        if not issues or not project_id:
            return 0
        
        print(f"  📌 Linking {len(issues)} {issue_type} issues to {project_name}")
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            futures = []
            for issue in issues:
                future = executor.submit(add_issue_to_project_fast, project_id, issue)
                futures.append(future)
            
            for i, future in enumerate(as_completed(futures)):
                try:
                    if future.result(timeout=30):
                        success_count += 1
                    if (i + 1) % 20 == 0:
                        print(f"    ✅ Linked {i + 1}/{len(issues)} to {project_name}")
                except Exception as e:
                    print(f"    ❌ Link exception: {str(e)}")
        
        print(f"  📊 {project_name}: {success_count}/{len(issues)} issues linked")
        return success_count
    
    # プロジェクトにリンク
    task_linked = link_batch(
        task_issues, 
        project_ids.get('イマココSNS（タスク）'), 
        'イマココSNS（タスク）',
        'task'
    )
    
    test_linked = link_batch(
        test_issues,
        project_ids.get('イマココSNS（テスト）'),
        'イマココSNS（テスト）',
        'test'
    )
    
    return task_linked, test_linked

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

def prepare_issue_data(issues: List[Dict], labels: List[str]) -> List[Tuple[Dict, str]]:
    """Issue作成用のデータを準備"""
    issue_requests = []
    for row in issues:
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:
            continue
            
        existing_labels = [label.strip() for label in row.get('labels', '').split(',') if label.strip()]
        all_labels = list(set(existing_labels + labels))
        
        issue_data = {
            'title': title,
            'body': body,
            'labels': all_labels
        }
        
        issue_type = 'task' if 'task' in labels else 'test'
        issue_requests.append((issue_data, issue_type))
    
    return issue_requests

def main():
    """メイン処理"""
    print("=" * 60)
    print("🧠 SMART ALL-IN-ONE ISSUE CREATOR v4.1")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: create_all_issues_smart.py v4.1")
    print(f"⚙️ Configuration:")
    print(f"  • Parallel Workers: {PARALLEL_WORKERS}")
    print(f"  • Request Delay: {REQUEST_DELAY}s")
    print(f"  • Batch Size: {BATCH_SIZE}")
    print(f"  • Dependencies: Standard library only")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # データ読み込み
        task_data, test_data = load_all_csv_data()
        total_issues = len(task_data) + len(test_data)
        
        if total_issues == 0:
            print("⚠️ No issues found in CSV files")
            return 1
        
        # バッチ計算
        total_batches = calculate_batches(total_issues, BATCH_SIZE)
        print(f"\n📊 Processing plan:")
        print(f"  • Total issues: {total_issues}")
        print(f"  • Batch size: {BATCH_SIZE}")
        print(f"  • Total batches: {total_batches}")
        
        # プロジェクトIDを読み込み
        project_ids = load_project_ids()
        
        # Issue作成用データ準備
        task_requests = prepare_issue_data(task_data, ['task', 'development'])
        test_requests = prepare_issue_data(test_data, ['test', 'qa'])
        all_requests = task_requests + test_requests
        
        print(f"\n📋 Prepared requests: {len(all_requests)} issues")
        
        # バッチ処理
        all_created_issues = []
        task_created = []
        test_created = []
        
        for batch_num in range(total_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(all_requests))
            batch_requests = all_requests[start_idx:end_idx]
            
            print(f"\n🔄 Batch {batch_num + 1}/{total_batches}: Processing issues {start_idx + 1}-{end_idx}")
            
            batch_created = create_issues_batch(batch_requests, batch_num + 1, total_batches)
            all_created_issues.extend(batch_created)
            
            # タスク/テスト別に分類
            for issue in batch_created:
                issue_labels = [label['name'] for label in issue.get('labels', [])]
                if 'task' in issue_labels:
                    task_created.append(issue)
                else:
                    test_created.append(issue)
            
            # バッチ間の休憩
            if batch_num < total_batches - 1:
                print(f"  ⏳ Batch pause...")
                time.sleep(2)
        
        # プロジェクトリンク
        task_linked, test_linked = link_issues_to_projects(task_created, test_created, project_ids)
        
        # 結果サマリー
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n" + "=" * 60)
        print("🎉 SMART PROCESSING COMPLETED!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"  • Task issues created: {len(task_created)}")
        print(f"  • Test issues created: {len(test_created)}")
        print(f"  • Total issues created: {len(all_created_issues)}")
        print(f"  • Task issues linked: {task_linked}")
        print(f"  • Test issues linked: {test_linked}")
        print(f"  • Success rate: {(len(all_created_issues)/total_issues*100):.1f}%")
        print(f"⏱️ Performance:")
        print(f"  • Execution time: {execution_time:.1f} seconds")
        print(f"  • Average per issue: {(execution_time/len(all_created_issues)):.2f}s")
        
        # 結果保存
        with open('smart_issue_creation_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Smart Issue Creation Results\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Task issues: {len(task_created)}\n")
            f.write(f"Test issues: {len(test_created)}\n")
            f.write(f"Total: {len(all_created_issues)}\n")
            f.write(f"Execution time: {execution_time:.1f}s\n")
            f.write(f"Success rate: {(len(all_created_issues)/total_issues*100):.1f}%\n")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    exit(main())