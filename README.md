# イマココSNS開発プロジェクト

このプロジェクトは、イマココSNSの開発用リポジトリです。

## 🚀 GitHub完結型自動化システム

### ワンクリックで完全自動セットアップ

[![🚀 Setup Team Environment](https://img.shields.io/badge/🚀_Setup-Click_to_Start-success?style=for-the-badge&logo=github)](../../actions/workflows/setup.yml)

**リポジトリをcloneしてREADME配置のボタンをワンクリックするだけで以下を完全自動生成：**

- 📚 **GitHub Wiki（完全自動）**
  - **Wiki自動初期化**: 手動で「Create the first page」をクリックする必要なし！
  - `data/imakoko_sns_tables.csv`からテーブル設計書を自動生成
  - 参考リンクページとHomeページの自動作成
  - GitHub Actions内でWikiリポジトリに直接プッシュ
  
- 📊 **GitHub Projects V2（完全自動）**
  - プロジェクト名「イマココSNS」を自動作成
  - TaskStatusフィールド（Product Backlog → Sprint Backlog → In Progress → Review → Done）
  - TestStatusフィールド（Not Started → In Progress → Failed/Passed → Blocked）
  
- 🎯 **GitHub Issues（完全自動）**
  - `data/tasks_for_issues.csv`から自動的にタスクIssuesを作成
  - `data/tests_for_issues.csv`から自動的にテストIssuesを作成
  - 自動ラベル付与（task/development, test/qa）
  - プロジェクトへの自動紐付け

### 🔑 必須: GitHub Tokenの設定

**⚠️ この設定がないと実行できません！**

#### セットアップ手順

1. **Personal Access Tokenの作成**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic) をクリック
   - 必要なスコープ:
     - ✅ `repo` (Full control)
     - ✅ `project` (Full control)
   
2. **Repository Secretへの登録**
   - このリポジトリ → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `TEAM_SETUP_TOKEN`
   - Secret: 作成したトークンを貼り付け

### 📖 使い方

1. 上記のセットアップボタンをクリック
2. `Run workflow` をクリック  
3. `Run workflow` ボタンをクリックして実行
4. Actions タブで進行状況を確認
5. 完了後、自動生成されたリソースを確認

### ✨ 完全自動生成される内容

#### 📚 Wiki（手動作業不要！）
- **自動初期化**: Wikiが存在しない場合、自動的に初期ページを作成
- **テーブル設計書**: CSVから自動生成されたデータベース設計
- **参考リンク**: プロジェクト関連リンクまとめ  
- **Home**: Wiki のホームページ
- **完全自動**: 「Create the first page」の手動クリック不要！

#### 📊 Project Views（要手動設定）
完全自動生成後、以下の手順で2つのビューを作成してください：

**タスクビュー作成：**
1. [Projects](../../projects) → 作成されたプロジェクトを開く
2. New view → Board
3. Name: `タスク`
4. Group by: `TaskStatus`
5. Filter: `label:task`

**テストビュー作成：**
1. New view → Board  
2. Name: `テスト`
3. Group by: `TestStatus`
4. Filter: `label:test`

これで要件通りの「タスク」「テスト」の2つのビューが完成します！

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

## 📝 ライセンス

MIT License
