#!/usr/bin/env python3
import os
import sys
import requests
import json
from pathlib import Path
import argparse
from dotenv import load_dotenv

load_dotenv()

class GitHubDiscussions:
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        self.graphql_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def enable_discussions(self):
        """Enable Discussions for the repository"""
        url = f"https://api.github.com/repos/{self.repo}"
        
        data = {
            "has_discussions": True
        }
        
        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print("✅ Discussions enabled for repository")
            return True
        else:
            print(f"⚠️  Could not enable discussions: {response.text}")
            return False

    def get_repository_id(self):
        """Get repository ID for GraphQL operations"""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
            }
        }
        """
        
        owner, name = self.repo.split('/')
        variables = {"owner": owner, "name": name}
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['repository']['id']
        else:
            print(f"❌ Error getting repository ID: {response.text}")
            return None

    def get_discussion_categories(self):
        """Get existing discussion categories"""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                discussionCategories(first: 20) {
                    nodes {
                        id
                        name
                        emoji
                        description
                    }
                }
            }
        }
        """
        
        owner, name = self.repo.split('/')
        variables = {"owner": owner, "name": name}
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['repository']['discussionCategories']['nodes']
        else:
            print(f"❌ Error getting categories: {response.text}")
            return []

    def create_discussion(self, title, body, category_id):
        """Create a new discussion"""
        repo_id = self.get_repository_id()
        if not repo_id:
            return False
        
        mutation = """
        mutation($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
            createDiscussion(input: {
                repositoryId: $repositoryId,
                categoryId: $categoryId,
                title: $title,
                body: $body
            }) {
                discussion {
                    id
                    number
                    title
                    url
                }
            }
        }
        """
        
        variables = {
            "repositoryId": repo_id,
            "categoryId": category_id,
            "title": title,
            "body": body
        }
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": mutation, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            discussion = data['data']['createDiscussion']['discussion']
            print(f"✅ Created discussion: {discussion['title']} (#{discussion['number']})")
            return discussion
        else:
            print(f"❌ Error creating discussion: {response.text}")
            return None

def load_template(template_path):
    """Load discussion template from file"""
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"⚠️  Template not found: {template_path}")
        return None

def create_sample_discussions(gh_discussions, template_dir):
    """Create sample discussions with templates"""
    
    categories = gh_discussions.get_discussion_categories()
    
    category_map = {cat['name']: cat['id'] for cat in categories}
    
    general_category_id = category_map.get('General')
    
    if not general_category_id:
        print("⚠️  General category not found, using first available category")
        general_category_id = categories[0]['id'] if categories else None
    
    if not general_category_id:
        print("❌ No discussion categories found")
        return
    
    discussions_to_create = [
        {
            'title': '📅 会議議事録テンプレート',
            'template_file': 'meeting-template.md',
            'description': 'チームミーティングや打ち合わせの議事録テンプレートです。',
            'category_id': general_category_id
        },
        {
            'title': '🎯 プロジェクト概要と目標',
            'template_file': None,
            'body': '''# 🎯 プロジェクト概要と目標

## プロジェクト概要
このプロジェクトの概要と目標について説明します。

## 主な目標
1. **目標1**: 具体的な目標の説明
2. **目標2**: 具体的な目標の説明
3. **目標3**: 具体的な目標の説明

## 成功指標
- 指標1: 具体的な数値目標
- 指標2: 具体的な数値目標
- 指標3: 具体的な数値目標

## チームメンバー
- **プロジェクトマネージャー**: @username
- **リードエンジニア**: @username
- **フロントエンド**: @username
- **バックエンド**: @username
- **デザイナー**: @username

## スケジュール
| フェーズ | 開始日 | 終了日 | 担当者 |
|----------|--------|--------|--------|
| 設計フェーズ | MM/DD | MM/DD | @username |
| 開発フェーズ | MM/DD | MM/DD | @username |
| テストフェーズ | MM/DD | MM/DD | @username |
| リリース | MM/DD | MM/DD | @username |

## 関連リンク
- [プロジェクトボード](../projects)
- [Wiki](../wiki)
- [Issues](../issues)
''',
            'category_id': general_category_id
        },
        {
            'title': '💡 アイデア・提案募集',
            'template_file': None,
            'body': '''# 💡 アイデア・提案募集

プロジェクトを改善するためのアイデアや提案を募集しています！

## 提案方法
新しいアイデアがある場合は、以下の形式で投稿してください：

### 📝 提案テンプレート
```markdown
## 提案の概要
簡潔に提案内容を説明

## 背景・課題
現在の課題や改善したい点

## 提案する解決策
具体的な解決方法

## 期待される効果
この提案によって期待される改善効果

## 実装の難易度
- 簡単 / 普通 / 難しい

## 関連Issue
#xxx (関連するIssueがあれば)
```

## 過去のアイデア
- アイデア1: 採用済み ✅
- アイデア2: 検討中 🤔  
- アイデア3: 保留 ⏸️

お気軽にアイデアをお聞かせください！
''',
            'category_id': general_category_id
        },
        {
            'title': '📚 ナレッジベース',
            'template_file': None,
            'body': '''# 📚 ナレッジベース

開発で得た知見やtipsを共有する場です。

## 技術Tips
### フロントエンド
- React のベストプラクティス
- CSS の効率的な書き方
- パフォーマンス最適化

### バックエンド  
- API設計のコツ
- データベース最適化
- セキュリティ対策

### DevOps
- Docker活用法
- CI/CD改善
- 監視・ログ管理

## トラブルシューティング
よくある問題と解決方法をまとめています。

### エラー対処法
- エラー1: 原因と解決法
- エラー2: 原因と解決法

### 環境構築時の注意点
- 注意点1
- 注意点2

## 参考資料
- [公式ドキュメント](https://example.com)
- [チュートリアル](https://example.com)
- [サンプルコード](https://example.com)

新しい知見を得た際は、ぜひこちらで共有してください！
''',
            'category_id': general_category_id
        }
    ]
    
    created_count = 0
    
    for discussion in discussions_to_create:
        if discussion['template_file']:
            template_path = os.path.join(template_dir, discussion['template_file'])
            body = load_template(template_path)
            if body:
                body = f"{discussion['description']}\n\n{body}"
        else:
            body = discussion['body']
        
        if body:
            result = gh_discussions.create_discussion(
                discussion['title'],
                body,
                discussion['category_id']
            )
            if result:
                created_count += 1
    
    print(f"\n✅ Created {created_count}/{len(discussions_to_create)} discussions")

def main():
    parser = argparse.ArgumentParser(description='Setup GitHub Discussions with templates')
    parser.add_argument('--repo', type=str, help='Repository (owner/repo)')
    parser.add_argument('--token', type=str, help='GitHub token')
    
    args = parser.parse_args()
    
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ Error: GitHub token required. Use --token or set GITHUB_TOKEN")
        sys.exit(1)
    
    repo_name = args.repo or os.getenv('GITHUB_REPO')
    if not repo_name:
        print("❌ Error: Repository name required. Use --repo or set GITHUB_REPO")
        sys.exit(1)
    
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / 'templates' / 'discussions'
    
    print(f"🚀 Setting up discussions for {repo_name}...")
    
    gh_discussions = GitHubDiscussions(token, repo_name)
    
    gh_discussions.enable_discussions()
    
    print("📝 Creating discussion templates...")
    create_sample_discussions(gh_discussions, template_dir)
    
    print("\n🎉 Discussions setup complete!")
    print(f"Visit: https://github.com/{repo_name}/discussions")

if __name__ == "__main__":
    main()