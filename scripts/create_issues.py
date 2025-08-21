#!/usr/bin/env python3
"""
GitHub Issues作成とプロジェクト紐付けスクリプト
CSVからIssuesを作成し、対応するプロジェクトに紐付ける
"""

import os
import requests
import csv
import time
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

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
    """REST API リクエスト実行"""
    response = requests.request(method, url, headers=REST_HEADERS, **kwargs)
    if response.status_code == 403 and 'rate limit' in response.text.lower():
        print("⏳ Rate limit reached. Waiting 60 seconds...")
        time.sleep(60)
        return make_rest_request(method, url, **kwargs)
    return response

def graphql_request(query: str, variables: Dict = None) -> Dict:
    """GraphQL APIリクエスト実行"""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    response = requests.post(GRAPHQL_URL, json=payload, headers=GRAPHQL_HEADERS)
    if response.status_code != 200:
        print(f"❌ GraphQL Error: {response.status_code} - {response.text}")
        return {}
    
    data = response.json()
    if 'errors' in data:
        print(f"❌ GraphQL Errors: {data['errors']}")
        return {}
    
    return data.get('data', {})

def load_project_ids() -> Dict[str, str]:
    """保存されたプロジェクトIDを読み込み"""
    project_ids = {}
    try:
        with open('project_ids.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    title, project_id = line.strip().split(':', 1)
                    project_ids[title] = project_id
    except FileNotFoundError:
        print("⚠️ project_ids.txt not found. Issues will be created but not linked to projects.")
    
    return project_ids

def create_issues_from_csv(csv_path: str, issue_type: str, labels: List[str]) -> List[Dict]:
    """CSVファイルからIssuesを作成"""
    if not os.path.exists(csv_path):
        print(f"⚠️ CSV file not found: {csv_path}")
        return []
    
    created_issues = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                if i > 50:  # 制限を少し緩和
                    print(f"⚠️ Limiting to first 50 {issue_type} issues to avoid rate limits")
                    break
                
                title = row.get('title', '')
                body = row.get('body', '')
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
                    print(f"  ✅ Created: {title[:50]}... [Labels: {', '.join(all_labels)}]")
                else:
                    print(f"  ❌ Failed: {title[:50]}... - {response.text}")
                
                # Rate limit対策
                time.sleep(1)
                
    except Exception as e:
        print(f"❌ Error reading CSV {csv_path}: {str(e)}")
    
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
    for i, issue in enumerate(issues):
        if i >= 30:  # プロジェクトへの追加は30件まで
            print(f"    ⚠️ Limiting to first 30 issues for project addition")
            break
            
        variables = {
            'projectId': project_id,
            'contentId': issue['node_id']
        }
        
        result = graphql_request(query, variables)
        if result and 'addProjectV2ItemById' in result:
            success_count += 1
            print(f"    ✅ Added: {issue['title'][:40]}...")
        else:
            print(f"    ❌ Failed to add: {issue['title'][:40]}...")
        
        time.sleep(0.5)
    
    print(f"📊 Successfully added {success_count}/{len(issues[:30])} issues to {project_name}")

def main():
    """メイン処理"""
    print("🎯 Creating Issues and linking to Projects...")
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    
    # プロジェクトIDを読み込み
    project_ids = load_project_ids()
    
    # タスクIssuesを作成
    print("\n📝 Creating task issues from data/tasks_for_issues.csv...")
    task_issues = create_issues_from_csv(
        'data/tasks_for_issues.csv',
        'task',
        ['task', 'development']
    )
    
    # テストIssuesを作成
    print("\n🧪 Creating test issues from data/tests_for_issues.csv...")
    test_issues = create_issues_from_csv(
        'data/tests_for_issues.csv', 
        'test',
        ['test', 'qa']
    )
    
    # プロジェクトに紐付け
    if project_ids:
        print("\n📌 Linking issues to projects...")
        
        # タスクプロジェクトに紐付け
        task_project_id = project_ids.get('イマココSNS（タスク）')
        if task_project_id and task_issues:
            add_issues_to_project(task_project_id, task_issues, 'イマココSNS（タスク）')
        
        # テストプロジェクトに紐付け
        test_project_id = project_ids.get('イマココSNS（テスト）')
        if test_project_id and test_issues:
            add_issues_to_project(test_project_id, test_issues, 'イマココSNS（テスト）')
    
    print(f"\n✨ Issue creation completed!")
    print(f"📌 Created issues:")
    print(f"  • {len(task_issues)} task issues")
    print(f"  • {len(test_issues)} test issues")
    
    print(f"\n🔗 Access your issues:")
    print(f"  https://github.com/{GITHUB_REPOSITORY}/issues")
    
    return 0

if __name__ == '__main__':
    exit(main())