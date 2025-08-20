# イマココSNS開発プロジェクト

このプロジェクトは、イマココSNSの開発用リポジトリです。

## 🚀 チーム開発環境自動セットアップ

### ワンクリックで環境構築

[![🚀 Setup Team Environment](https://img.shields.io/badge/🚀_Setup-Click_to_Start-success?style=for-the-badge&logo=github)](../../actions/workflows/setup.yml)

**クリックするだけで以下を自動生成：**
- 📚 **GitHub Wiki**
  - テーブル設計書（データベース定義）
  - 参考リンクページ
- 📊 **GitHub Projects**
  - タスクビュー（Product Backlog → Sprint Backlog → In Progress → Review → Done）
  - テストビュー（Todo → In Progress → Done）
- 🎯 **GitHub Issues**
  - タスク用Issues（30個）
  - テスト用Issues（30個）

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
5. 完了後、Wiki・Projects・Issuesを確認

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
