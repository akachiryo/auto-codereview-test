# イマココSNS開発プロジェクト

このプロジェクトは、未経験エンジニア（アカデミー生）を対象としたチーム開発研修用リポジトリです。

## 🚀 チーム開発環境自動セットアップ

### ワンクリックで完全自動化

[![🚀 Team Setup](https://img.shields.io/badge/🚀_Team_Setup-Click_to_Start-success?style=for-the-badge&logo=github)](../../actions/workflows/team-setup.yml)

**リポジトリをcloneまたはtemplateでコピーし、README配置のボタンをワンクリックするだけで以下を完全自動生成：**

- 📊 **3つのGitHub Projects V2**
  - `イマココSNS（タスク）` - 開発タスク管理
  - `イマココSNS（テスト）` - テスト管理
  - `イマココSNS（KPTA）` - ふりかえり管理
  
- 🎯 **GitHub Issues**
  - タスクIssues（`data/tasks_for_issues.csv`から自動生成）
  - テストIssues（`data/tests_for_issues.csv`から自動生成）
  - 自動ラベル付与とプロジェクトへの紐付け
  
- 💬 **GitHub Discussions**
  - デフォルトカテゴリーの削除
  - 「議事録」カテゴリーの作成
  - 議事録テンプレートの投稿
  
- 📚 **GitHub Wiki**
  - HOMEページ
  - ルール（初期は空）
  - キックオフ（初期は空）
  - テーブル設計書（`data/imakoko_sns_tables.csv`から自動生成）

## 🔑 セットアップ手順

### 1. GitHub Personal Access Tokenの作成

1. **Personal Access Tokenの作成**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic) をクリック
   - 必要なスコープ:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `project` (Full control of projects)

2. **Repository Secretへの登録**
   - このリポジトリ → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `TEAM_SETUP_TOKEN`
   - Secret: 作成したトークンを貼り付け

### 2. Wikiの初期化

Wikiの「Create the first page」ボタンを押してWikiを有効化してください。
- リポジトリのWikiタブ → 「Create the first page」をクリック
- 何でも良いので適当にページを作成（後で自動上書きされます）

### 3. 自動セットアップの実行

1. 上記の「🚀 Team Setup」ボタンをクリック
2. `Run workflow` をクリック  
3. `Run workflow` ボタンをクリックして実行
4. Actions タブで進行状況を確認
5. 完了後、自動生成されたリソースを確認

## 📋 生成されるリソース

### GitHub Projects
- [Projects](../../projects) で3つのプロジェクトが確認できます
- タスクとテストのIssuesが自動的に各プロジェクトに紐付けられます

### GitHub Issues
- [Issues](../../issues) でタスクとテストのIssuesが確認できます
- 適切なラベルが自動付与されます

### GitHub Discussions
- [Discussions](../../discussions) で議事録カテゴリーとテンプレートが確認できます

### GitHub Wiki
- [Wiki](../../wiki) でテーブル設計書とその他のページが確認できます

## 🛠️ 開発環境

### 技術スタック

- **フレームワーク**: Spring Boot 3.2.0
- **データベース**: H2 Database (インメモリ)
- **ビルドツール**: Maven
- **コンテナ**: Docker

### 実行方法

```bash
# Docker Compose で起動
docker-compose up --build

# または Maven で起動
mvn spring-boot:run
```

アクセス: http://localhost:8080

## 📝 参考資料

- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)
- [Figma デザイン](https://www.figma.com/file/l8Zzw1wPJBitm0bQMNXTdB/イマココSNS)
- [GitHub ベースリポジトリ](https://github.com/prum-jp/imakoko-base)

## 📝 ライセンス

MIT License