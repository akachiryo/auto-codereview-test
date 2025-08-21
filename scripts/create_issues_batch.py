#!/usr/bin/env python3
"""
GitHub Issues バッチ作成スクリプト
Rate Limit対策でバッチ処理によりIssueを作成
"""

import os
import requests
import csv
import time
import sys
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')
BATCH_NUMBER = int(os.environ.get('BATCH_NUMBER', '1'))
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '50'))

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

REPO_OWNER, REPO_NAME = GITHUB_REPOSITORY.split('/')

# GitHub API設定
# API Reference: https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28
API_BASE = 'https://api.github.com'
REST_HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

# GraphQL API設定
# API Reference: https://docs.github.com/en/graphql/reference/mutations#addprojectv2itembyid
GRAPHQL_URL = 'https://api.github.com/graphql'
GRAPHQL_HEADERS = {
    'Authorization': f'Bearer {TEAM_SETUP_TOKEN}',
    'Content-Type': 'application/json'
}

def make_rest_request(method: str, url: str, **kwargs) -> requests.Response:
    """REST API リクエスト実行（エラーハンドリング強化）"""
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.request(method, url, headers=REST_HEADERS, **kwargs)
        
        if response.status_code == 403:
            if 'rate limit' in response.text.lower():
                wait_time = 60 * (attempt + 1)  # 1分、2分、3分と段階的に増加
                print(f"⏳ Rate limit reached (attempt {attempt + 1}). Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"❌ Forbidden error: {response.text}")
                break
        elif response.status_code == 422:
            print(f"⚠️ Validation error: {response.text}")
            break
        else:
            return response
    
    return response

def graphql_request(query: str, variables: Dict = None) -> Dict:
    """GraphQL APIリクエスト実行"""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.post(GRAPHQL_URL, json=payload, headers=GRAPHQL_HEADERS)
        
        if response.status_code == 403:
            wait_time = 60 * (attempt + 1)
            print(f"⏳ GraphQL rate limit. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            continue
            
        if response.status_code != 200:
            print(f"❌ GraphQL Error: {response.status_code} - {response.text}")
            return {}
        
        data = response.json()
        if 'errors' in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
            return {}
        
        return data.get('data', {})
    
    return {}

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

def create_issues_from_batch(batch_data: List[Dict], issue_type: str, labels: List[str]) -> List[Dict]:
    """バッチデータからIssuesを作成"""
    created_issues = []
    
    print(f"🎯 Creating {len(batch_data)} {issue_type} issues...")
    
    for i, row in enumerate(batch_data, 1):
        title = row.get('title', '').strip()
        body = row.get('body', '').strip()
        
        if not title:  # タイトルが空の場合はスキップ
            print(f"  ⚠️ Skipping row {i}: empty title")
            continue
            
        existing_labels = [label.strip() for label in row.get('labels', '').split(',') if label.strip()]
        
        # 新しいラベルを追加
        all_labels = list(set(existing_labels + labels))
        
        # Issue作成
        issue_data = {
            'title': title,
            'body': body,
            'labels': all_labels
        }
        
        response = make_rest_request(
            'POST',
            f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
            json=issue_data
        )
        
        if response.status_code == 201:
            issue = response.json()
            created_issues.append(issue)
            print(f"  ✅ Created ({i}/{len(batch_data)}): {title[:50]}...")
        else:
            print(f"  ❌ Failed ({i}/{len(batch_data)}): {title[:50]}...")
            print(f"     Error: {response.status_code} - {response.text[:100]}")
        
        # バッチ内でもRate limit対策
        time.sleep(2)
        
        # 10件ごとに少し長めの休憩
        if i % 10 == 0:
            print(f"  ⏳ Processed {i} issues, brief pause...")
            time.sleep(5)
    
    return created_issues

def add_issues_to_project(project_id: str, issues: List[Dict], project_name: str):
    """IssuesをProjectsに追加"""
    if not issues or not project_id:
        return
    
    print(f"📌 Adding {len(issues)} issues to project: {project_name}")
    
    # API Reference: https://docs.github.com/en/graphql/reference/mutations#addprojectv2itembyid
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item {
                id
            }
        }
    }
    """
    
    success_count = 0
    for i, issue in enumerate(issues, 1):
        variables = {
            'projectId': project_id,
            'contentId': issue['node_id']
        }
        
        result = graphql_request(query, variables)
        if result and 'addProjectV2ItemById' in result:
            success_count += 1
            print(f"    ✅ Added ({i}/{len(issues)}): {issue['title'][:40]}...")
        else:
            print(f"    ❌ Failed ({i}/{len(issues)}): {issue['title'][:40]}...")
        
        # プロジェクト追加でもRate limit対策
        time.sleep(1.5)
        
        # 10件ごとに休憩
        if i % 10 == 0:
            print(f"    ⏳ Added {i} issues to project, brief pause...")
            time.sleep(5)
    
    print(f"📊 Successfully added {success_count}/{len(issues)} issues to {project_name}")

def main():
    """メイン処理"""
    print(f"🎯 Creating Issues - Batch {BATCH_NUMBER} (Size: {BATCH_SIZE})")
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    
    # プロジェクトIDを読み込み
    project_ids = load_project_ids()
    
    # タスクIssuesのバッチ処理
    print(f"\n📝 Processing task issues batch {BATCH_NUMBER}...")
    task_batch = get_csv_batch('data/tasks_for_issues.csv', BATCH_NUMBER, BATCH_SIZE)
    task_issues = []
    
    if task_batch:
        task_issues = create_issues_from_batch(
            task_batch,
            'task',
            ['task', 'development']
        )
        
        # タスクプロジェクトに紐付け
        task_project_id = project_ids.get('イマココSNS（タスク）')
        if task_project_id and task_issues:
            add_issues_to_project(task_project_id, task_issues, 'イマココSNS（タスク）')
    
    # テストIssuesのバッチ処理
    print(f"\n🧪 Processing test issues batch {BATCH_NUMBER}...")
    test_batch = get_csv_batch('data/tests_for_issues.csv', BATCH_NUMBER, BATCH_SIZE)
    test_issues = []
    
    if test_batch:
        test_issues = create_issues_from_batch(
            test_batch, 
            'test',
            ['test', 'qa']
        )
        
        # テストプロジェクトに紐付け
        test_project_id = project_ids.get('イマココSNS（テスト）')
        if test_project_id and test_issues:
            add_issues_to_project(test_project_id, test_issues, 'イマココSNS（テスト）')
    
    print(f"\n✨ Batch {BATCH_NUMBER} completed!")
    print(f"📌 Created issues:")
    print(f"  • {len(task_issues)} task issues")
    print(f"  • {len(test_issues)} test issues")
    
    # バッチ完了状況をファイルに保存
    with open(f'batch_{BATCH_NUMBER}_completed.txt', 'w', encoding='utf-8') as f:
        f.write(f"Batch {BATCH_NUMBER} completed\n")
        f.write(f"Task issues: {len(task_issues)}\n")
        f.write(f"Test issues: {len(test_issues)}\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return 0

if __name__ == '__main__':
    exit(main())