#!/usr/bin/env python3
"""
GitHub Discussions設定スクリプト
デフォルトカテゴリーを削除し、議事録カテゴリーとテンプレートを作成
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
# API Reference: https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions
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

def check_discussions_enabled() -> bool:
    """リポジトリでDiscussionsが有効化されているかチェック"""
    # API Reference: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}"
    headers = {
        'Authorization': f'token {TEAM_SETUP_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        discussions_enabled = repo_data.get('has_discussions', False)
        print(f"🔍 Discussions enabled: {discussions_enabled}")
        return discussions_enabled
    else:
        print(f"⚠️ Could not check discussions status: {response.status_code}")
        return False

def enable_discussions() -> bool:
    """リポジトリでDiscussionsを有効化"""
    # API Reference: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}"
    headers = {
        'Authorization': f'token {TEAM_SETUP_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    data = {'has_discussions': True}
    response = requests.patch(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Discussions enabled successfully")
        return True
    else:
        print(f"❌ Failed to enable discussions: {response.status_code} - {response.text}")
        return False

def get_repository_info() -> Optional[Dict]:
    """リポジトリ情報とDiscussionカテゴリーを取得"""
    # まずDiscussionsが有効かチェック
    if not check_discussions_enabled():
        print("📝 Discussions not enabled, attempting to enable...")
        if not enable_discussions():
            print("⚠️ Could not enable discussions automatically")
            print("💡 Please enable discussions manually:")
            print(f"   1. Go to https://github.com/{GITHUB_REPOSITORY}/settings")
            print("   2. Scroll down to 'Features' section")
            print("   3. Check 'Discussions' checkbox")
            return None
        else:
            # 有効化後少し待機
            print("⏳ Waiting for discussions to be fully enabled...")
            time.sleep(5)
    
    # API Reference: https://docs.github.com/en/graphql/reference/objects#repository
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
            hasDiscussionsEnabled
            discussionCategories(first: 20) {
                nodes {
                    id
                    name
                    slug
                    description
                    isAnswerable
                }
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
        repo = result['repository']
        print(f"📊 Repository discussions enabled: {repo.get('hasDiscussionsEnabled', 'Unknown')}")
        print(f"📊 Found {len(repo.get('discussionCategories', {}).get('nodes', []))} discussion categories")
        return repo
    return None

def get_existing_discussions(repository_id: str) -> List[Dict]:
    """既存のディスカッションを取得"""
    # API Reference: https://docs.github.com/en/graphql/reference/objects#discussionconnection
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            discussions(first: 100) {
                nodes {
                    id
                    title
                    body
                    category {
                        id
                        name
                    }
                }
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
        return result['repository']['discussions']['nodes']
    return []

def create_category_via_web_api(repository_id: str, name: str, description: str) -> Optional[str]:
    """Discussion カテゴリーの作成（Web API制限あり）"""
    # NOTE: GitHub GraphQL API では discussion category の作成をサポートしていません
    # API Reference: https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions
    # Discussion categories must be created via GitHub web interface
    
    print(f"  ⚠️ GitHub API limitation: Cannot create discussion categories via API")
    print(f"  📝 Category '{name}' must be created manually in GitHub web interface")
    print(f"  🔗 Go to: https://github.com/{GITHUB_REPOSITORY}/discussions/categories")
    print(f"  💡 Or enable discussions and default categories will be created automatically")
    return None

def create_discussion(repository_id: str, category_id: str, title: str, body: str) -> bool:
    """Discussionを作成"""
    # API Reference: https://docs.github.com/en/graphql/reference/mutations#creatediscussion
    query = """
    mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
        createDiscussion(input: {
            repositoryId: $repositoryId,
            categoryId: $categoryId,
            title: $title,
            body: $body
        }) {
            discussion {
                id
                title
                url
            }
        }
    }
    """
    
    variables = {
        'repositoryId': repository_id,
        'categoryId': category_id,
        'title': title,
        'body': body
    }
    
    result = graphql_request(query, variables)
    if result and 'createDiscussion' in result:
        discussion = result['createDiscussion']['discussion']
        print(f"  ✅ Created discussion: {discussion['title']}")
        print(f"  🔗 URL: {discussion['url']}")
        return True
    else:
        print(f"  ❌ Failed to create discussion: {title}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("💬 DISCUSSIONS SETUP v3.0 (CONSOLIDATED)")
    print("=" * 60)
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Script: setup_discussions.py v3.0")
    print("=" * 60)
    
    # リポジトリ情報取得
    repo_info = get_repository_info()
    if not repo_info:
        print("❌ Failed to get repository information")
        return 1
    
    repository_id = repo_info['id']
    existing_categories = repo_info['discussionCategories']['nodes']
    
    # 既存のディスカッションをチェック
    print(f"\n🔍 Checking for existing discussions...")
    existing_discussions = get_existing_discussions(repository_id)
    
    # 議事録テンプレートが既に存在するかチェック
    template_exists = False
    for discussion in existing_discussions:
        if "議事録テンプレート" in discussion.get('title', ''):
            template_exists = True
            print(f"  ✅ Meeting minutes template already exists: {discussion['title']}")
            break
    
    print(f"\n📝 Working with discussions...")
    
    # GitHub API では discussion category の作成ができないため、
    # 既存のカテゴリーを確認してそこに議事録テンプレートを作成
    
    if existing_categories and not template_exists:
        # 最初のカテゴリーを使用してテンプレートを作成
        first_category = existing_categories[0]
        category_id = first_category['id']
        category_name = first_category['name']
        
        print(f"  📝 Using existing category: {category_name}")
        print(f"  📋 Creating meeting minutes template...")
        
        # 議事録テンプレートを作成
        template_title = "📋 議事録テンプレート - チーム開発用"
        template_body = """# 議事録

## 📅 開催日時
YYYY/MM/DD HH:MM ～ HH:MM

## 👥 参加者
- [ ] メンバー1
- [ ] メンバー2
- [ ] メンバー3
- [ ] メンター

## 📋 進捗報告

### メンバー1
- 前回からの進捗：
- 今回の作業予定：
- 課題・困っていること：

### メンバー2
- 前回からの進捗：
- 今回の作業予定：
- 課題・困っていること：

### メンバー3
- 前回からの進捗：
- 今回の作業予定：
- 課題・困っていること：

## 🔍 メンターレビュー
- レビューコメント：
- アドバイス：
- 次回までの宿題：

## 📅 次回MTG
- 日時：YYYY/MM/DD HH:MM ～ HH:MM
- 議題：

## 📝 備考
- その他連絡事項：
- 次回までのタスク：

---
*このテンプレートをコピーして新しい議事録を作成してください*

**注意**: GitHub API の制限により、「議事録」専用カテゴリーは手動で作成する必要があります。
- GitHub リポジトリの Discussions タブ → Categories → New category
- 名前: 議事録
- 説明: チーム開発の議事録を管理するカテゴリーです
"""
        
        create_discussion(repository_id, category_id, template_title, template_body)
    elif template_exists:
        print(f"  ℹ️ Meeting minutes template already exists, skipping creation")
    else:
        print(f"  ⚠️ No discussion categories found")
        print(f"  💡 Please enable discussions first in repository settings")
        
        # API制限についてユーザーに通知
        create_category_via_web_api(repository_id, "議事録", "チーム開発の議事録を管理するカテゴリーです")
    
    print(f"\n✨ Discussions setup completed!")
    print(f"📌 Setup result:")
    if existing_categories:
        if template_exists:
            print(f"  • Meeting minutes template already exists")
        else:
            print(f"  • Meeting minutes template created in existing category")
    else:
        print(f"  • No existing categories found")
        
    print(f"  • Instructions provided for manual category creation")
    print(f"\n💡 Manual setup recommended:")
    print(f"  1. Go to https://github.com/{GITHUB_REPOSITORY}/discussions/categories")
    print(f"  2. Create new category: 議事録")
    print(f"  3. Move the template discussion to the new category")
    
    print(f"\n🔗 Access your discussions:")
    print(f"  https://github.com/{GITHUB_REPOSITORY}/discussions")
    
    return 0

if __name__ == '__main__':
    exit(main())