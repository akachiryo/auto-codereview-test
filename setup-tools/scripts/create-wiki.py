#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import time
import requests
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
    
    # Add more comprehensive pages
    comprehensive_pages = {
        'コーディング規約.md': '''# 📝 コーディング規約

## 🎯 基本方針

- **可読性重視**: 誰が読んでも理解しやすいコード
- **一貫性維持**: チーム全体で統一されたスタイル  
- **保守性向上**: 将来の変更・拡張に対応しやすい設計

## ☕ Java コーディング規約

### 命名規則

| 要素 | 規則 | 例 |
|------|------|----|  
| クラス | PascalCase | `UserController` |
| メソッド | camelCase | `getUserById()` |
| 変数・フィールド | camelCase | `firstName` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| パッケージ | lowercase | `com.example.service` |

---

**コーディング規約について質問があれば [Discussions](../discussions) で相談してください！**
''',
        '画面設計書.md': '''# 🎨 画面設計書

## 🎯 UI/UX設計方針

### デザイン原則
- **シンプル**: 直感的で分かりやすいインターフェース
- **一貫性**: 全画面で統一されたデザインパターン
- **アクセシビリティ**: 誰でも使いやすいユニバーサルデザイン
- **レスポンシブ**: 様々なデバイスサイズに対応

---

**デザインに関する提案や改善点は [Discussions](../discussions) で議論しましょう！**
''',
        'デプロイ手順.md': '''# 🚢 デプロイ手順

## 🚀 本番デプロイフロー

### 1. 事前準備
- [ ] テスト実行・完了確認
- [ ] リリースノート作成
- [ ] データベースマイグレーション確認

### 2. デプロイ実行
```bash
# 本番デプロイ
./deploy/production-deploy.sh v1.2.0
```

### 3. デプロイ後確認
- [ ] アプリケーション起動確認
- [ ] ヘルスチェック通過確認
- [ ] 主要機能動作確認

---

**デプロイで問題があれば [Discussions](../discussions) で報告・相談してください！**
''',
        'トラブルシューティング.md': f'''# 🆘 トラブルシューティング

## 🐛 よくある問題と解決法

### アプリケーション起動エラー
```bash
# ログ確認
docker-compose logs app

# ポート確認
lsof -i :8080

# 再起動
docker-compose restart
```

### データベース接続エラー
```bash
# H2コンソール確認
curl http://localhost:8080/h2-console

# データベース状態確認
docker-compose logs db
```

### ビルドエラー
```bash
# 依存関係更新
mvn clean install

# キャッシュクリア
mvn dependency:purge-local-repository
```

## 🚨 緊急時対応

### サービス停止時
1. **即座に影響範囲を特定**
2. **ログ・メトリクス確認**  
3. **必要に応じてロールバック実行**
4. **チームに状況共有**

### データ消失時
1. **被害状況の確認**
2. **バックアップからの復旧**
3. **原因調査・再発防止策検討**

---

**解決できない問題は [Discussions](../discussions) で緊急相談してください！**

**作成日**: {time.strftime('%Y-%m-%d %H:%M:%S')}
'''
    }
    
    additional_pages = {
        'Home.md': f'''# 🏠 プロジェクトWiki

チーム開発環境が自動セットアップされました！このWikiには開発に必要な全てのドキュメントが準備されています。

## 📚 ドキュメント一覧

### 🗃️ 設計書
- [📊 テーブル設計書](テーブル設計書) - データベース設計とER図
- [🔌 API設計書](API設計書) - REST APIエンドポイント仕様
- [🎨 画面設計書](画面設計書) - UI/UX設計とワイヤーフレーム

### 🛠️ 開発ガイド
- [🚀 開発環境構築](開発環境構築) - プロジェクトのセットアップ手順
- [📝 コーディング規約](コーディング規約) - 統一されたコードスタイル
- [🌿 Git運用ルール](Git運用ルール) - ブランチ戦略とワークフロー

### 🔧 運用・保守
- [🚢 デプロイ手順](デプロイ手順) - リリースプロセス
- [🆘 トラブルシューティング](トラブルシューティング) - よくある問題と解決法

### 🔗 便利なリンク
- [💻 GitHubリポジトリ](../) - ソースコード
- [📋 Issues](../issues) - タスク管理
- [🔄 Pull Requests](../pulls) - コードレビュー
- [📊 Projects](../projects) - プロジェクト管理
- [💬 Discussions](../discussions) - チーム議論

## 🎯 チーム開発のスタートガイド

### 新メンバー向け
1. [開発環境構築](開発環境構築)を参照してセットアップ
2. [コーディング規約](コーディング規約)を確認
3. [Git運用ルール](Git運用ルール)を理解

### プロジェクト進行中
- [Issues](../issues)で作業を確認・アサイン
- [Projects](../projects)で全体進捗を把握
- [Discussions](../discussions)でチーム内コミュニケーション

## 📝 ドキュメント更新について

このWikiは**チーム全体で維持管理**します：
- 新しい決定事項や変更はドキュメントに反映
- 古い情報は定期的に見直し・更新
- 疑問点は[Discussions](../discussions)で議論

---

**Wiki作成日**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**最終更新日**: {time.strftime('%Y-%m-%d')}
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
        '開発環境構築.md': '''# 🚀 開発環境構築

## 📋 必要なツール

### 必須ツール
- **Git** (バージョン管理)
- **Docker & Docker Compose** (コンテナ環境)
- **Java 17以上** (アプリケーション実行)
- **Maven** (ビルドツール)

### エディタ・IDE
- **Visual Studio Code** (推奨)
- **IntelliJ IDEA** 
- **Eclipse**

### 便利ツール
- **Postman** (API テスト)
- **DBeaver** (データベース管理)

## 🔧 セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

### 2. 🐳 Docker を使用した実行（推奨）
```bash
# Docker Compose でアプリケーションを起動
docker-compose up --build

# バックグラウンドで実行する場合
docker-compose up -d --build
```

### 3. 📦 Maven を使用した実行
```bash
# Mavenがインストールされている場合
mvn spring-boot:run
```

### 4. 🔧 Docker のみを使用した実行
```bash
# Docker イメージをビルド
docker build -t auto-codereview-test .

# コンテナを実行
docker run -p 8080:8080 auto-codereview-test
```

### 5. 動作確認
- **アプリケーション**: http://localhost:8080
- **H2 データベースコンソール**: http://localhost:8080/h2-console
  - JDBC URL: `jdbc:h2:mem:testdb`
  - ユーザー名: `sa`
  - パスワード: (空)

## 🛠️ 開発環境の詳細設定

### VS Code 推奨拡張機能
```json
{
  "recommendations": [
    "vscjava.vscode-java-pack",
    "redhat.java",
    "vmware.vscode-spring-boot",
    "ms-vscode.vscode-json"
  ]
}
```

### Git設定
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Maven設定確認
```bash
mvn --version
# Java version: 17以上が表示されることを確認
```

## 🐛 トラブルシューティング

### ポートが使用中の場合
```bash
# ポート使用状況確認
lsof -i :8080

# プロセス終了
kill -9 <PID>
```

### Dockerコンテナの完全リセット
```bash
# 全コンテナ・ボリューム削除
docker-compose down -v

# 再ビルド・起動
docker-compose up -d --build
```

### Java/Maven関連エラー
```bash
# Javaバージョン確認
java -version

# Maven依存関係クリア・再インストール
mvn clean install
```

### データベース接続エラー
```bash
# H2コンソールアクセス確認
curl http://localhost:8080/h2-console

# アプリケーションログ確認
docker-compose logs app
```

## 📚 参考資料

- [Spring Boot公式ドキュメント](https://spring.io/projects/spring-boot)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [Maven公式ガイド](https://maven.apache.org/guides/)
- [H2 Database](http://www.h2database.com/)

## 💡 開発Tips

### ホットリロード
```bash
# Spring Boot DevToolsを使用（pom.xmlに設定済み）
mvn spring-boot:run
# ファイル変更時に自動再起動
```

### デバッグモード
```bash
# リモートデバッグ有効化
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005"
```

### ログレベル変更
```properties
# application.properties
logging.level.com.example=DEBUG
logging.level.org.springframework=INFO
```

---

**環境構築で困った時は [Discussions](../discussions) で質問してください！**
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
    
    # Create comprehensive pages first
    for filename, content in comprehensive_pages.items():
        file_path = os.path.join(wiki_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Created {filename}")
    
    # Then create additional pages  
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

def enable_wiki(repo_name, token):
    """Enable Wiki for the repository"""
    print("🔧 Ensuring Wiki is enabled...")
    
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    url = f"https://api.github.com/repos/{repo_name}"
    
    # First check if wiki is already enabled
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        if repo_data.get('has_wiki', False):
            print("  ✅ Wiki already enabled")
            return True
    
    # Enable wiki
    data = {"has_wiki": True}
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("  ✅ Wiki enabled successfully")
        return True
    else:
        print(f"  ⚠️  Could not enable Wiki: {response.status_code}")
        return False

def create_initial_wiki_page(repo_name, token):
    """Create initial wiki page via API to initialize wiki repository"""
    print("📝 Creating initial wiki page...")
    
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    url = f"https://api.github.com/repos/{repo_name}/wiki"
    
    # Create a simple initial page
    data = {
        "title": "Home",
        "content": "# Wiki Setup\n\nInitializing wiki...",
        "format": "markdown"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("  ✅ Initial wiki page created")
        return True
    else:
        print(f"  ⚠️  Could not create initial page: {response.status_code}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create GitHub Wiki pages')
    parser.add_argument('--repo', type=str, help='Repository (owner/repo)')
    parser.add_argument('--token', type=str, help='GitHub token')
    parser.add_argument('--retry-count', type=int, default=3, help='Retry attempts')
    
    args = parser.parse_args()
    
    repo_name = args.repo or os.getenv('GITHUB_REPO')
    if not repo_name:
        print("❌ Error: Repository name required. Use --repo or set GITHUB_REPO")
        sys.exit(1)
    
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ Error: GitHub token required. Use --token or set GITHUB_TOKEN")
        sys.exit(1)
    
    print(f"🚀 Setting up Wiki for {repo_name}...")
    
    # Step 1: Enable Wiki
    if not enable_wiki(repo_name, token):
        print("❌ Failed to enable Wiki")
        sys.exit(1)
    
    # Step 2: Create initial page to initialize wiki repo
    time.sleep(2)  # Wait for wiki to be ready
    if not create_initial_wiki_page(repo_name, token):
        print("⚠️  Could not create initial page via API, trying Git method...")
    
    # Step 3: Setup wiki content via Git
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / 'templates' / 'wiki'
    wiki_dir = script_dir.parent / 'wiki-temp'
    
    repo_url = f"https://github.com/{repo_name}"
    if token:
        repo_url = f"https://{token}@github.com/{repo_name}"
    
    # Try multiple times to clone/setup wiki
    for attempt in range(args.retry_count):
        try:
            print(f"📥 Attempt {attempt + 1}/{args.retry_count}: Setting up wiki content...")
            
            # Wait a bit between attempts
            if attempt > 0:
                time.sleep(5)
            
            wiki_exists = clone_wiki(repo_url, wiki_dir)
            copy_templates(template_dir, wiki_dir)
            
            if wiki_exists:
                commit_and_push(wiki_dir, "Update wiki documentation")
            else:
                commit_and_push(wiki_dir, "Initial wiki setup with comprehensive documentation")
            
            shutil.rmtree(wiki_dir)
            print(f"\n🎉 Wiki setup complete! Visit: https://github.com/{repo_name}/wiki")
            return
            
        except Exception as e:
            print(f"  ❌ Attempt {attempt + 1} failed: {str(e)}")
            if os.path.exists(wiki_dir):
                shutil.rmtree(wiki_dir)
            
            if attempt == args.retry_count - 1:
                print(f"\n❌ Wiki setup failed after {args.retry_count} attempts")
                print("   Try running again in a few minutes or check repository permissions")
                sys.exit(1)

if __name__ == "__main__":
    main()