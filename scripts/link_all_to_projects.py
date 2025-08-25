#!/usr/bin/env python3
"""
全Issue→プロジェクトリンクスクリプト（並列実行後統合版）
"""

import os
import requests
import time
from typing import Dict, List, Optional

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
GITHUB_REPOSITORY = os.environ.get('GITHUB_REPOSITORY')

if not TEAM_SETUP_TOKEN or not GITHUB_REPOSITORY:
    raise ValueError("TEAM_SETUP_TOKEN and GITHUB_REPOSITORY environment variables are required")

# GitHub API設定
API_BASE = 'https://api.github.com'
GRAPHQL_URL = 'https://api.github.com/graphql'

REST_HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

GRAPHQL_HEADERS = {
    'Authorization': f'Bearer {TEAM_SETUP_TOKEN}',
    'Content-Type': 'application/json'
}

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
        print("⚠️ project_ids.txt not found")
    
    return project_ids

def get_all_issues_by_labels() -> Dict[str, List[Dict]]:
    """ラベル別にIssueを取得"""
    print("📋 Fetching all issues by labels...")
    
    issues_by_type = {
        'task': [],
        'test': [],
        'kpt': []
    }
    
    session = requests.Session()
    session.headers.update(REST_HEADERS)
    
    # 各ラベルでIssueを取得
    for label_type in ['task', 'test', 'kpt']:
        page = 1
        while True:
            try:
                response = session.get(
                    f"{API_BASE}/repos/{GITHUB_REPOSITORY}/issues",
                    params={
                        'labels': label_type,
                        'state': 'open',
                        'per_page': 100,
                        'page': page
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    issues = response.json()
                    if not issues:
                        break
                    
                    issues_by_type[label_type].extend(issues)
                    print(f"  📄 {label_type}: fetched page {page} ({len(issues)} issues)")
                    page += 1
                    time.sleep(0.5)  # API制限回避
                else:
                    print(f"  ❌ Failed to fetch {label_type} issues: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"  ❌ Exception fetching {label_type}: {str(e)}")
                break
    
    print(f"📊 Total issues: task={len(issues_by_type['task'])}, test={len(issues_by_type['test'])}, kpt={len(issues_by_type['kpt'])}")
    return issues_by_type

def add_issue_to_project(project_id: str, issue: Dict) -> Optional[str]:
    """IssueをProjectに追加"""
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

def link_issues_to_projects(issues_by_type: Dict[str, List[Dict]], project_ids: Dict[str, str]):
    """全IssueをProjectsにリンク"""
    print("\n🔗 Linking issues to projects...")
    
    # プロジェクトマッピング
    project_mapping = {
        'task': 'イマココSNS（タスク）',
        'test': 'イマココSNS（テスト）',
        'kpt': 'イマココSNS（KPT）'
    }
    
    linking_results = {}
    
    for issue_type, project_name in project_mapping.items():
        issues = issues_by_type.get(issue_type, [])
        project_id = project_ids.get(project_name)
        
        if not issues:
            print(f"  📝 No {issue_type} issues to link")
            linking_results[issue_type] = 0
            continue
            
        if not project_id:
            print(f"  ❌ Project ID not found for {project_name}")
            linking_results[issue_type] = 0
            continue
        
        print(f"  📌 Linking {len(issues)} {issue_type} issues to {project_name}")
        success_count = 0
        
        for i, issue in enumerate(issues):
            try:
                item_id = add_issue_to_project(project_id, issue)
                if item_id:
                    success_count += 1
                
                # 進捗表示
                if (i + 1) % 50 == 0 or i == len(issues) - 1:
                    print(f"    ✅ Progress: {i + 1}/{len(issues)} ({success_count} successful)")
                    
            except Exception as e:
                print(f"    ❌ Link exception: {str(e)}")
            
            time.sleep(0.1)  # API制限回避
        
        linking_results[issue_type] = success_count
        print(f"  📊 {project_name}: {success_count}/{len(issues)} issues linked")
    
    return linking_results

def main():
    """メイン処理"""
    print("=" * 60)
    print("🔗 PROJECT LINKER (Post-Parallel Integration)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # プロジェクトID読み込み
        project_ids = load_project_ids()
        if not project_ids:
            print("❌ No project IDs found. Cannot link issues.")
            return 1
        
        # 全Issueをラベル別に取得
        issues_by_type = get_all_issues_by_labels()
        
        total_issues = sum(len(issues) for issues in issues_by_type.values())
        if total_issues == 0:
            print("⚠️ No issues found to link")
            return 0
        
        # プロジェクトにリンク
        linking_results = link_issues_to_projects(issues_by_type, project_ids)
        
        # 結果サマリー
        total_linked = sum(linking_results.values())
        
        print(f"\n" + "=" * 60)
        print("🎉 PROJECT LINKING COMPLETED!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"  • Task issues linked: {linking_results.get('task', 0)}")
        print(f"  • Test issues linked: {linking_results.get('test', 0)}")
        print(f"  • KPT issues linked: {linking_results.get('kpt', 0)}")
        print(f"  • Total issues linked: {total_linked}/{total_issues}")
        print(f"  • Success rate: {(total_linked/total_issues*100):.1f}%")
        print(f"⏱️ Execution time: {time.time() - start_time:.1f}s")
        
        # 結果保存
        with open('project_linking_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"Project Linking Results\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Task issues linked: {linking_results.get('task', 0)}\n")
            f.write(f"Test issues linked: {linking_results.get('test', 0)}\n")
            f.write(f"KPT issues linked: {linking_results.get('kpt', 0)}\n")
            f.write(f"Total linked: {total_linked}\n")
            f.write(f"Success rate: {(total_linked/total_issues*100):.1f}%\n")
            f.write(f"Execution time: {time.time() - start_time:.1f}s\n")
        
        return 0
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())