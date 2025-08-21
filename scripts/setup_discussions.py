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

def get_repository_info() -> Optional[Dict]:
    """リポジトリ情報とDiscussionカテゴリーを取得"""
    # API Reference: https://docs.github.com/en/graphql/reference/objects#repository
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
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
        return result['repository']
    return None

def delete_category(category_id: str, category_name: str) -> bool:
    """Discussionカテゴリーを削除"""
    # API Reference: https://docs.github.com/en/graphql/reference/mutations#deletediscussioncategory
    query = """
    mutation($categoryId: ID!) {
        deleteDiscussionCategory(input: {categoryId: $categoryId}) {
            repository {
                id
            }
        }
    }
    """
    
    variables = {
        'categoryId': category_id
    }
    
    result = graphql_request(query, variables)
    if result and 'deleteDiscussionCategory' in result:
        print(f"  ✅ Deleted category: {category_name}")
        return True
    else:
        print(f"  ❌ Failed to delete category: {category_name}")
        return False

def create_category(repository_id: str, name: str, description: str) -> Optional[str]:
    """Discussionカテゴリーを作成"""
    # API Reference: https://docs.github.com/en/graphql/reference/mutations#creatediscussioncategory
    query = """
    mutation($repositoryId: ID!, $name: String!, $description: String!) {
        createDiscussionCategory(input: {
            repositoryId: $repositoryId,
            name: $name,
            description: $description,
            format: OPEN
        }) {
            category {
                id
                name
                slug
            }
        }
    }
    """
    
    variables = {
        'repositoryId': repository_id,
        'name': name,
        'description': description
    }
    
    result = graphql_request(query, variables)
    if result and 'createDiscussionCategory' in result:
        category = result['createDiscussionCategory']['category']
        print(f"  ✅ Created category: {category['name']} (slug: {category['slug']})")
        return category['id']
    else:
        print(f"  ❌ Failed to create category: {name}")
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
    print("💬 Setting up GitHub Discussions...")
    print(f"📦 Repository: {GITHUB_REPOSITORY}")
    
    # リポジトリ情報取得
    repo_info = get_repository_info()
    if not repo_info:
        print("❌ Failed to get repository information")
        return 1
    
    repository_id = repo_info['id']
    existing_categories = repo_info['discussionCategories']['nodes']
    
    print(f"\n🗑️ Removing default categories...")
    # デフォルトカテゴリーを削除
    for category in existing_categories:
        delete_category(category['id'], category['name'])
        time.sleep(1)  # Rate limit対策
    
    print(f"\n📝 Creating '議事録' category...")
    # 議事録カテゴリーを作成
    category_id = create_category(
        repository_id,
        "議事録",
        "チーム開発の議事録を管理するカテゴリーです"
    )
    
    if category_id:
        time.sleep(2)  # カテゴリー作成後の待機
        
        print(f"\n📋 Creating meeting minutes template...")
        # 議事録テンプレートを作成
        template_title = "📋 議事録テンプレート"
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
"""
        
        create_discussion(repository_id, category_id, template_title, template_body)
    
    print(f"\n✨ Discussions setup completed!")
    print(f"📌 Created:")
    print(f"  • '議事録' category")
    print(f"  • Meeting minutes template")
    
    print(f"\n🔗 Access your discussions:")
    print(f"  https://github.com/{GITHUB_REPOSITORY}/discussions")
    
    return 0

if __name__ == '__main__':
    exit(main())