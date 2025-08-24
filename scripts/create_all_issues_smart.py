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
# from concurrent.futures import ThreadPoolExecutor, as_completed  # 並列処理無効化
import threading
import math

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

# 動的設定
PARALLEL_WORKERS = 1     # 順番保持のためシーケンシャル処理
REQUEST_DELAY = 0.5      # レート制限回避のためのディレイ
BATCH_SIZE = 30          # バッチサイズ
BURST_LIMIT = 10         # バーストリミット
RETRY_DELAY = 2.0        # リトライ間隔
MAX_RETRIES = 3          # 最大リトライ回数

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
    
    # デバッグ: 最初の数件のdifficultyを確認
    if task_issues:
        print(f"🔍 Debug: First few task difficulties:")
        for i, task in enumerate(task_issues[:5]):
            print(f"    Task {i+1}: {task.get('title', 'No title')[:50]}... -> difficulty: '{task.get('difficulty', 'None')}'")
        
        # 各難易度の数もカウント
        difficulties = {}
        for task in task_issues:
            diff = task.get('difficulty', '')
            difficulties[diff] = difficulties.get(diff, 0) + 1
        print(f"🔍 Debug: Difficulty distribution: {difficulties}")
    
    return task_issues, test_issues

def calculate_batches(total_count: int, batch_size: int) -> int:
    """必要なバッチ数を計算"""
    return math.ceil(total_count / batch_size)

def create_single_issue(issue_data: Dict, index: int, total: int, issue_type: str) -> Optional[Dict]:
    """単一のIssueを作成（リトライ機能付き）"""
    session = get_session()
    
    # レート制限回避のためのディレイ
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
                if attempt > 0:
                    print(f"  ✅ {issue_type} ({index + 1}/{total}) [retry {attempt}]: {issue_data['title'][:50]}...")
                else:
                    print(f"  ✅ {issue_type} ({index + 1}/{total}): {issue_data['title'][:50]}...")
                return issue
            
            elif response.status_code == 403:
                print(f"  ⏳ Rate limit hit ({index + 1}/{total}) [attempt {attempt + 1}]...")
                time.sleep(RETRY_DELAY * (attempt + 1))  # 指数バックオフ
                continue
                
            elif response.status_code >= 500:
                print(f"  🔄 Server error ({response.status_code}) ({index + 1}/{total}) [attempt {attempt + 1}]...")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            
            else:
                print(f"  ❌ {issue_type} failed ({index + 1}/{total}): {response.status_code} - {response.text[:100]}")
                break
                
        except Exception as e:
            print(f"  ❌ {issue_type} exception ({index + 1}/{total}) [attempt {attempt + 1}]: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
    
    return None

def create_issues_batch(issues_data: List[Tuple], batch_num: int, total_batches: int) -> Tuple[List[Dict], List[Tuple]]:
    """1つのバッチでIssueを作成（失敗したものを返す）"""
    created_issues = []
    failed_issues = []
    
    if not issues_data:
        return created_issues, failed_issues
    
    print(f"🚀 Processing batch {batch_num}/{total_batches} ({len(issues_data)} issues)")
    
    # シーケンシャル実行（順番保持のため）
    for i, (issue_data, issue_type) in enumerate(issues_data):
        try:
            issue = create_single_issue(issue_data, i, len(issues_data), issue_type)
            if issue:
                created_issues.append(issue)
            else:
                failed_issues.append((issue_data, issue_type))
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            failed_issues.append((issue_data, issue_type))
    
    print(f"📊 Batch {batch_num} result: {len(created_issues)}/{len(issues_data)} issues created, {len(failed_issues)} failed")
    return created_issues, failed_issues

def set_project_field_value_by_name(project_id: str, item_id: str, field_name: str, option_name: str) -> bool:
    """プロジェクトアイテムのカスタムフィールド値をフィールド名で設定"""
    print(f"    🔧 Setting field '{field_name}' to '{option_name}'")
    
    # フィールド情報とオプションIDを取得
    get_field_query = """
    query($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
                fields(first: 20) {
                    nodes {
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                            options {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    variables = {'projectId': project_id}
    
    try:
        payload = {'query': get_field_query, 'variables': variables}
        response = requests.post(GRAPHQL_URL, json=payload, headers=GRAPHQL_HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"    ❌ Failed to get field info: HTTP {response.status_code}")
            return False
            
        data = response.json()
        if 'errors' in data:
            print(f"    ❌ GraphQL errors: {data['errors']}")
            return False
            
        if 'data' not in data or not data['data'] or not data['data']['node']:
            print(f"    ❌ No data returned")
            return False
            
        # 対象フィールドとオプションを探す
        field_id = None
        option_id = None
        
        for field in data['data']['node']['fields']['nodes']:
            if field.get('name') == field_name:
                field_id = field['id']
                print(f"    ✅ Found field '{field_name}' with ID: {field_id}")
                print(f"    🔍 Available options: {[opt['name'] for opt in field.get('options', [])]}")
                
                for option in field.get('options', []):
                    if option['name'] == option_name:
                        option_id = option['id']
                        print(f"    ✅ Found option '{option_name}' with ID: {option_id}")
                        break
                break
        
        if not field_id:
            print(f"    ❌ Field '{field_name}' not found")
            return False
            
        if not option_id:
            print(f"    ❌ Option '{option_name}' not found in field '{field_name}'")
            return False
        
        # フィールド値を設定
        update_query = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
            updateProjectV2ItemFieldValue(input: {
                projectId: $projectId,
                itemId: $itemId,
                fieldId: $fieldId,
                value: $value
            }) {
                projectV2Item { 
                    id 
                }
            }
        }
        """
        
        update_variables = {
            'projectId': project_id,
            'itemId': item_id,
            'fieldId': field_id,
            'value': {
                'singleSelectOptionId': option_id
            }
        }
        
        update_payload = {'query': update_query, 'variables': update_variables}
        update_response = requests.post(GRAPHQL_URL, json=update_payload, headers=GRAPHQL_HEADERS, timeout=30)
        
        if update_response.status_code == 200:
            update_data = update_response.json()
            if 'errors' not in update_data and 'data' in update_data:
                print(f"    ✅ Successfully set field value")
                return True
            else:
                print(f"    ❌ Update failed: {update_data.get('errors', 'Unknown error')}")
        else:
            print(f"    ❌ Update request failed: HTTP {update_response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"    ❌ Exception setting field value: {str(e)}")
        return False

def set_project_field_value(project_id: str, item_id: str, field_id: str, option_name: str) -> bool:
    """プロジェクトアイテムのカスタムフィールド値を設定"""
    print(f"    🔧 Attempting to set field value: {option_name}")
    # まずフィールドのオプションIDを取得
    get_field_query = """
    query($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
                fields(first: 20) {
                    nodes {
                        ... on ProjectV2SingleSelectField {
                            id
                            name
                            options {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    variables = {'projectId': project_id}
    
    try:
        payload = {'query': get_field_query, 'variables': variables}
        response = requests.post(GRAPHQL_URL, json=payload, headers=GRAPHQL_HEADERS, timeout=30)
        
        if response.status_code != 200:
            return False
            
        data = response.json()
        if 'errors' in data or 'data' not in data:
            return False
            
        # 難易度フィールドと対象オプションを探す
        option_id = None
        difficulty_field_found = False
        
        for field in data['data']['node']['fields']['nodes']:
            if field.get('name') == 'Difficulty':
                difficulty_field_found = True
                print(f"    🔍 Found Difficulty field with options: {[opt['name'] for opt in field.get('options', [])]}")
                for option in field.get('options', []):
                    if option['name'] == option_name:
                        option_id = option['id']
                        print(f"    ✅ Found matching option: {option_name} -> {option_id}")
                        break
                break
        
        if not difficulty_field_found:
            print(f"    ❌ Difficulty field not found in project")
            return False
            
        if not option_id:
            print(f"    ❌ Option '{option_name}' not found in Difficulty field")
            return False
        
        # フィールド値を設定
        update_query = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
            updateProjectV2ItemFieldValue(input: {
                projectId: $projectId,
                itemId: $itemId,
                fieldId: $fieldId,
                value: $value
            }) {
                projectV2Item { id }
            }
        }
        """
        
        update_variables = {
            'projectId': project_id,
            'itemId': item_id,
            'fieldId': field_id,
            'value': {
                'singleSelectOptionId': option_id
            }
        }
        
        update_payload = {'query': update_query, 'variables': update_variables}
        update_response = requests.post(GRAPHQL_URL, json=update_payload, headers=GRAPHQL_HEADERS, timeout=30)
        
        if update_response.status_code == 200:
            update_data = update_response.json()
            return 'errors' not in update_data and 'data' in update_data
        return False
        
    except Exception as e:
        print(f"    ⚠️ Field update error: {str(e)}")
        return False

def load_difficulty_field_info() -> Optional[Tuple[str, str, str]]:
    """難易度フィールド情報を読み込み"""
    try:
        with open('difficulty_field.txt', 'r', encoding='utf-8') as f:
            line = f.read().strip()
            print(f"    🔍 Read difficulty_field.txt: {line}")
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    result = parts[0], parts[1], parts[2]  # title, project_id, field_id
                    print(f"    🔍 Parsed difficulty info: {result}")
                    return result
        print(f"    ⚠️ difficulty_field.txt exists but format is invalid")
        return None
    except FileNotFoundError:
        print(f"    ⚠️ difficulty_field.txt not found")
        return None

def add_issue_to_project_fast(project_id: str, issue: Dict) -> Optional[str]:
    """高速でIssueをProjectに追加し、アイテムIDを返す"""
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
                return data['data']['addProjectV2ItemById']['item']['id']
        return None
    except:
        return None

def link_issues_to_projects(task_issues: List[Dict], test_issues: List[Dict], project_ids: Dict[str, str]):
    """IssueをProjectsにリンク"""
    print("\n🔗 Linking issues to projects...")
    
    def link_batch(issues: List[Dict], project_id: str, project_name: str, issue_type: str):
        if not issues or not project_id:
            return 0
        
        print(f"  📌 Linking {len(issues)} {issue_type} issues to {project_name}")
        success_count = 0
        
        # 難易度フィールド情報を読み込み
        difficulty_info = load_difficulty_field_info()
        field_set_count = 0
        
        if issue_type == 'task':
            print(f"    🔍 Debug: difficulty_info = {difficulty_info}")
            print(f"    🔍 Debug: project_name = {project_name}")
            print(f"    🔍 Debug: project_id = {project_id}")
        
        for i, issue in enumerate(issues):
            try:
                item_id = add_issue_to_project_fast(project_id, issue)
                if item_id:
                    success_count += 1
                    
                    # タスクの場合、難易度フィールドを設定
                    if issue_type == 'task':
                        print(f"    🔍 Debug: issue difficulty = {issue.get('difficulty')}")
                        
                        if (difficulty_info and 'タスク' in project_name and issue.get('difficulty')):
                            _, task_project_id, stored_field_id = difficulty_info
                            print(f"    🔍 Debug: Attempting to set field. project_id match: {project_id == task_project_id}")
                            
                            if project_id == task_project_id:
                                # フィールドIDは使わず、フィールド名でダイナミックに検索
                                if set_project_field_value_by_name(project_id, item_id, 'Difficulty', issue['difficulty']):
                                    field_set_count += 1
                                    print(f"    ✅ Set difficulty '{issue['difficulty']}' for issue {issue.get('title', 'Unknown')}")
                                else:
                                    print(f"    ❌ Failed to set difficulty for issue {issue.get('title', 'Unknown')}")
                        else:
                            print(f"    ⚠️ Skipping difficulty set: difficulty_info={bool(difficulty_info)}, has_タスク={'タスク' in project_name}, has_difficulty={bool(issue.get('difficulty'))}")
                
                if (i + 1) % 20 == 0:
                    print(f"    ✅ Linked {i + 1}/{len(issues)} to {project_name}")
            except Exception as e:
                print(f"    ❌ Link exception: {str(e)}")
            time.sleep(0.1)  # プロジェクトリンクも少し間隔を空ける
        
        print(f"  📊 {project_name}: {success_count}/{len(issues)} issues linked")
        if issue_type == 'task' and field_set_count > 0:
            print(f"  🏷️ {project_name}: {field_set_count}/{success_count} difficulty fields set")
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
    """Issue作成用のデータを準備（番号付きタイトル）"""
    issue_requests = []
    issue_type = 'task' if 'task' in labels else 'test'
    
    for index, row in enumerate(issues, 1):
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:
            continue
        
        # タイトルに番号を追加（既に番号がある場合は置き換え）
        if issue_type == 'task':
            # 「タスク」で始まる場合は、番号を置き換え
            if title.startswith('タスク'):
                # 「タスク」の後の数字やコロンを削除し、本文を抽出
                import re
                match = re.match(r'タスク[\d\s:.]*(.+)', title)
                if match:
                    clean_title = match.group(1).strip()
                else:
                    clean_title = title
                numbered_title = f"タスク{index:03d}: {clean_title}"
            else:
                numbered_title = f"タスク{index:03d}: {title}"
        else:
            # 「テスト」で始まる場合は、番号を置き換え
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
            
        existing_labels = [label.strip() for label in row.get('labels', '').split(',') if label.strip()]
        all_labels = list(set(existing_labels + labels))
        
        # 難易度情報を取得（タスクのみ）
        difficulty = row.get('difficulty', '').strip() if issue_type == 'task' else None
        
        issue_data = {
            'title': numbered_title,
            'body': body,
            'labels': all_labels,
            'difficulty': difficulty
        }
        
        issue_requests.append((issue_data, issue_type))
    
    return issue_requests

def retry_failed_issues(failed_issues: List[Tuple], max_retry_rounds: int = 2) -> List[Dict]:
    """失敗したissueをリトライする"""
    if not failed_issues:
        return []
    
    print(f"\n🔄 Retrying {len(failed_issues)} failed issues...")
    
    retry_created = []
    remaining_failed = failed_issues.copy()
    
    for round_num in range(max_retry_rounds):
        if not remaining_failed:
            break
            
        print(f"  🔁 Retry round {round_num + 1}/{max_retry_rounds}: {len(remaining_failed)} issues")
        
        # リトライ前に長めの休憩
        time.sleep(3.0)
        
        current_round_created, current_round_failed = create_issues_batch(
            remaining_failed, round_num + 1, max_retry_rounds
        )
        
        retry_created.extend(current_round_created)
        remaining_failed = current_round_failed
        
        # 次のラウンドまでの休憩
        if remaining_failed and round_num < max_retry_rounds - 1:
            print(f"    ⏳ Waiting before next retry round...")
            time.sleep(5.0)
    
    if remaining_failed:
        print(f"  ⚠️ {len(remaining_failed)} issues could not be created after all retries")
        print("  Failed issues:")
        for issue_data, issue_type in remaining_failed[:5]:  # 最初の5個だけ表示
            print(f"    - {issue_type}: {issue_data['title'][:50]}...")
        if len(remaining_failed) > 5:
            print(f"    ... and {len(remaining_failed) - 5} more")
    
    print(f"  ✅ Retry success: {len(retry_created)} issues created")
    return retry_created

def main():
    """メイン処理"""
    print("=" * 60)
    print("🧠 SMART ALL-IN-ONE ISSUE CREATOR v4.3 (sequential + numbered)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: create_all_issues_smart.py v4.3")
    print(f"⚙️ Configuration:")
    print(f"  • Parallel Workers: {PARALLEL_WORKERS}")
    print(f"  • Request Delay: {REQUEST_DELAY}s")
    print(f"  • Retry Delay: {RETRY_DELAY}s")
    print(f"  • Max Retries: {MAX_RETRIES}")
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
            
            batch_created, batch_failed = create_issues_batch(batch_requests, batch_num + 1, total_batches)
            all_created_issues.extend(batch_created)
            
            # 失敗したものを集約
            if batch_failed:
                print(f"  📝 {len(batch_failed)} issues failed in this batch, will retry later...")
                if 'all_failed_issues' not in locals():
                    all_failed_issues = []
                all_failed_issues.extend(batch_failed)
            
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
        
        # 失敗したもののリトライ
        retry_created = []
        if 'all_failed_issues' in locals() and all_failed_issues:
            retry_created = retry_failed_issues(all_failed_issues)
            all_created_issues.extend(retry_created)
            
            # リトライで作成されたものも分類
            for issue in retry_created:
                issue_labels = [label['name'] for label in issue.get('labels', [])]
                if 'task' in issue_labels:
                    task_created.append(issue)
                else:
                    test_created.append(issue)
        
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
        if retry_created:
            print(f"  • Retry issues created: {len(retry_created)}")
        print(f"  • Task issues linked: {task_linked}")
        print(f"  • Test issues linked: {test_linked}")
        final_failed = len(all_failed_issues) - len(retry_created) if 'all_failed_issues' in locals() else 0
        if final_failed > 0:
            print(f"  • Final failed issues: {final_failed}")
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
            if retry_created:
                f.write(f"Retry issues: {len(retry_created)}\n")
            final_failed = len(all_failed_issues) - len(retry_created) if 'all_failed_issues' in locals() else 0
            if final_failed > 0:
                f.write(f"Final failed issues: {final_failed}\n")
            f.write(f"Execution time: {execution_time:.1f}s\n")
            f.write(f"Success rate: {(len(all_created_issues)/total_issues*100):.1f}%\n")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")
        return 1

if __name__ == '__main__':
    exit(main())