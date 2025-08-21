#!/usr/bin/env python3
"""
GitHub Projects V2作成スクリプト
3つの独立したプロジェクトを作成する
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

REPO_OWNER, REPO_NAME = GITHUB_REPOSITORY.split('/')

# GitHub GraphQL API設定
# API Reference: https://docs.github.com/en/graphql/reference/mutations#createprojectv2
GRAPHQL_URL = 'https://api.github.com/graphql'
HEADERS = {
    'Authorization': f'Bearer {TEAM_SETUP_TOKEN}',
    'Content-Type': 'application/json'
}

def graphql_request(query: str, variables: Dict = None) -> Dict:
    """GraphQL APIリクエスト実行"""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    response = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ GraphQL Error: {response.status_code} - {response.text}")
        return {}
    
    data = response.json()
    if 'errors' in data:
        print(f"❌ GraphQL Errors: {data['errors']}")
        return {}
    
    return data.get('data', {})

def get_repository_info() -> Optional[Dict]:
    """リポジトリ情報を取得"""
    # API Reference: https://docs.github.com/en/graphql/reference/queries#repository
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
            owner {
                id
                __typename
            }
        }
    }
    """
    
    variables = {
        'owner': REPO_OWNER,
        'name': REPO_NAME
    }
    
    result = graphql_request(query, variables)
    if result and 'repository' in result:
        return {
            'repository_id': result['repository']['id'],
            'owner_id': result['repository']['owner']['id']
        }
    return None

def create_project(title: str, repo_info: Dict) -> Optional[str]:
    """プロジェクトを作成"""
    # API Reference: https://docs.github.com/en/graphql/reference/mutations#createprojectv2
    query = """
    mutation($ownerId: ID!, $repositoryId: ID!, $title: String!) {
        createProjectV2(input: {ownerId: $ownerId, repositoryId: $repositoryId, title: $title}) {
            projectV2 {
                id
                number
                title
                url
            }
        }
    }
    """
    
    variables = {
        'ownerId': repo_info['owner_id'],
        'repositoryId': repo_info['repository_id'],
        'title': title
    }
    
    result = graphql_request(query, variables)
    if result and 'createProjectV2' in result:
        project = result['createProjectV2']['projectV2']
        print(f"✅ Created project: {project['title']} (#{project['number']})")
        print(f"🔗 Project URL: {project['url']}")
        return project['id']
    else:
        print(f"❌ Failed to create project: {title}")
        return None

def main():
    """メイン処理"""
    print("📊 Creating GitHub Projects V2...")
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    
    # リポジトリ情報取得
    repo_info = get_repository_info()
    if not repo_info:
        print("❌ Failed to get repository information")
        return 1
    
    # 3つのプロジェクトを作成
    projects = [
        "イマココSNS（タスク）",
        "イマココSNS（テスト）", 
        "イマココSNS（KPTA）"
    ]
    
    created_projects = {}
    
    for project_title in projects:
        project_id = create_project(project_title, repo_info)
        if project_id:
            created_projects[project_title] = project_id
        
        # Rate limit対策
        time.sleep(2)
    
    # 結果をファイルに保存（他のスクリプトで使用）
    if created_projects:
        project_info = []
        for title, project_id in created_projects.items():
            project_info.append(f"{title}:{project_id}")
        
        with open('project_ids.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(project_info))
    
    print(f"\n✨ Project creation completed!")
    print(f"📌 Created {len(created_projects)} projects:")
    for title in created_projects:
        print(f"  • {title}")
    
    print(f"\n🔗 Access your projects:")
    print(f"  https://github.com/{GITHUB_REPOSITORY}/projects")
    
    return 0

if __name__ == '__main__':
    exit(main())