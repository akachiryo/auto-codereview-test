#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
from dotenv import load_dotenv

load_dotenv()

def clone_wiki(repo_url, wiki_dir):
    wiki_url = repo_url.replace('.git', '.wiki.git')
    if wiki_url.startswith('https://github.com/'):
        wiki_url = wiki_url
    else:
        wiki_url = f"https://github.com/{repo_url}.wiki.git"
    
    if os.path.exists(wiki_dir):
        shutil.rmtree(wiki_dir)
    
    print(f"📥 Cloning wiki repository: {wiki_url}")
    result = subprocess.run(['git', 'clone', wiki_url, wiki_dir], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️  Wiki repository doesn't exist. Creating new wiki...")
        os.makedirs(wiki_dir, exist_ok=True)
        subprocess.run(['git', 'init'], cwd=wiki_dir)
        subprocess.run(['git', 'remote', 'add', 'origin', wiki_url], cwd=wiki_dir)
        return False
    return True

def copy_templates(template_dir, wiki_dir):
    print("📄 Copying wiki templates...")
    
    files_to_copy = {
        'table-design.md': 'テーブル設計書.md',
        'table-design.md': 'Database-Design.md',
    }
    
    additional_pages = {
        'Home.md': '''# プロジェクトWiki

## 📚 ドキュメント一覧

### 設計書
- [テーブル設計書](テーブル設計書)
- [API設計書](API設計書)
- [画面設計書](画面設計書)

### 開発ガイド
- [開発環境構築](開発環境構築)
- [コーディング規約](コーディング規約)
- [Git運用ルール](Git運用ルール)

### 運用
- [デプロイ手順](デプロイ手順)
- [トラブルシューティング](トラブルシューティング)

### 参考リンク
- [GitHubリポジトリ](../)
- [Issues](../issues)
- [Pull Requests](../pulls)
- [Projects](../projects)

---

最終更新日: 2024-01-01
''',
        'API設計書.md': '''# API設計書

## 基本仕様

### ベースURL
```
https://api.example.com/v1
```

### 認証方式
Bearer Token (JWT)

### レスポンス形式
JSON

## エンドポイント一覧

### 認証 API

#### POST /auth/login
ユーザーログイン

**リクエスト:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**レスポンス:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com"
  }
}
```

### ユーザー API

#### GET /users
ユーザー一覧取得

#### GET /users/{id}
ユーザー詳細取得

#### POST /users
ユーザー作成

#### PUT /users/{id}
ユーザー更新

#### DELETE /users/{id}
ユーザー削除

## エラーレスポンス

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": {}
  }
}
```

## ステータスコード

| コード | 説明 |
|--------|------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Internal Server Error |
''',
        '開発環境構築.md': '''# 開発環境構築

## 必要なツール

- Git
- Docker & Docker Compose
- Node.js (v18以上)
- Python (v3.9以上)

## セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

### 2. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して必要な値を設定
```

### 3. Dockerコンテナの起動
```bash
docker-compose up -d
```

### 4. 依存関係のインストール
```bash
npm install
# または
pip install -r requirements.txt
```

### 5. データベースのセットアップ
```bash
npm run db:migrate
npm run db:seed
```

### 6. アプリケーションの起動
```bash
npm run dev
# または
python manage.py runserver
```

## トラブルシューティング

### ポートが使用中の場合
```bash
lsof -i :8080
kill -9 <PID>
```

### Dockerコンテナのリセット
```bash
docker-compose down -v
docker-compose up -d --build
```
''',
        'Git運用ルール.md': '''# Git運用ルール

## ブランチ戦略

### ブランチ種別

| ブランチ | 用途 | 命名規則 |
|---------|------|----------|
| main | 本番環境 | main |
| develop | 開発環境 | develop |
| feature | 機能開発 | feature/機能名 |
| bugfix | バグ修正 | bugfix/修正内容 |
| hotfix | 緊急修正 | hotfix/修正内容 |

## コミットメッセージ

### フォーマット
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type一覧
- feat: 新機能
- fix: バグ修正
- docs: ドキュメント
- style: フォーマット修正
- refactor: リファクタリング
- test: テスト
- chore: その他

### 例
```
feat(auth): ログイン機能を追加

JWTトークンを使用した認証機能を実装
- ログインAPI
- トークン検証ミドルウェア
- リフレッシュトークン機能

Issue #123
```

## プルリクエスト

### テンプレート
```markdown
## 概要
変更内容の概要

## 変更内容
- [ ] 変更点1
- [ ] 変更点2

## テスト
- [ ] ユニットテスト
- [ ] 結合テスト

## レビューポイント
特に確認してほしい箇所

## 関連Issue
#123
```

## マージルール
- レビュー承認: 1人以上
- CIパス必須
- コンフリクト解消必須
'''
    }
    
    for src_file, dest_file in files_to_copy.items():
        src_path = os.path.join(template_dir, src_file)
        dest_path = os.path.join(wiki_dir, dest_file)
        
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"  ✅ Copied {dest_file}")
    
    for filename, content in additional_pages.items():
        file_path = os.path.join(wiki_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Created {filename}")

def commit_and_push(wiki_dir, message="Initial wiki setup"):
    print("💾 Committing changes...")
    subprocess.run(['git', 'add', '.'], cwd=wiki_dir)
    subprocess.run(['git', 'commit', '-m', message], cwd=wiki_dir)
    
    print("📤 Pushing to remote...")
    result = subprocess.run(['git', 'push', 'origin', 'master'], cwd=wiki_dir, capture_output=True, text=True)
    
    if result.returncode != 0 and 'main' in result.stderr:
        result = subprocess.run(['git', 'push', 'origin', 'main'], cwd=wiki_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], cwd=wiki_dir, capture_output=True, text=True)
        if result.returncode != 0:
            result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], cwd=wiki_dir, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Wiki successfully created and pushed!")
    else:
        print(f"⚠️  Push may have failed. Manual push might be required.\n{result.stderr}")

def main():
    parser = argparse.ArgumentParser(description='Create GitHub Wiki pages')
    parser.add_argument('--repo', type=str, help='Repository (owner/repo)')
    parser.add_argument('--token', type=str, help='GitHub token')
    
    args = parser.parse_args()
    
    repo_name = args.repo or os.getenv('GITHUB_REPO')
    if not repo_name:
        print("❌ Error: Repository name required. Use --repo or set GITHUB_REPO")
        sys.exit(1)
    
    token = args.token or os.getenv('GITHUB_TOKEN')
    
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / 'templates' / 'wiki'
    wiki_dir = script_dir.parent / 'wiki-temp'
    
    repo_url = f"https://github.com/{repo_name}"
    if token:
        repo_url = f"https://{token}@github.com/{repo_name}"
    
    wiki_exists = clone_wiki(repo_url, wiki_dir)
    copy_templates(template_dir, wiki_dir)
    
    if wiki_exists:
        commit_and_push(wiki_dir, "Update wiki documentation")
    else:
        commit_and_push(wiki_dir, "Initial wiki setup")
    
    shutil.rmtree(wiki_dir)
    print("\n🎉 Wiki setup complete!")

if __name__ == "__main__":
    main()