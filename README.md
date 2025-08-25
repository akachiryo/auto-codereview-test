# イマココSNS開発プロジェクト

このプロジェクトは、アカデミー生を対象としたイマココSNSチーム開発用リポジトリです。

## 🚀 チーム開発環境自動セットアップ

### 1. GitHub Personal Access Tokenの作成

1. **Personal Access Tokenの作成**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic) をクリック
   - 必要なスコープ:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `project` (Full control of projects)
     - ✅ `write:discussion` (Read and write team discussions)

2. **Repository Secretへの登録**
   - このリポジトリ → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `TEAM_SETUP_TOKEN`
   - Secret: 作成したトークンを貼り付け

### 3. 自動セットアップ準備
wikiを変更可能状態にする

1. [wiki](../../wiki) に遷移
2. `Create the first page` ボタンをクリック
3. 何も編集せず右下の`Save page`ボタンをクリック
4. Home画面が表示される

### 2. 自動セットアップの実行
[![🚀 Team Setup](https://img.shields.io/badge/🚀_Team_Setup_v3.0-Click_to_Start-success?style=for-the-badge&logo=github)](../../actions/workflows/team-setup.yml)

1. 上記の「🚀 Team Setup」ボタンをクリック
2. `Run workflow` ボタンをクリックして実行
3. [Actions](../../actions) タブで進行状況を確認
4. 全セットアップが完了するまで待つ

### 3. 手動セットアップ
1. イマココSNS（KPT）のstatusをKPT用に変更する
- 変更前：Todo, In Progress, Done
- 変更後：Keep, Problem, Try, Done

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

## 🔧 トラブルシューティング

### 古いエラーが出る場合（v3.0移行後）
もし以下のエラーメッセージが表示される場合:
- `⚠️ Limiting to first 50 test issues to avoid rate limits`
- `⚠️ Limiting to first 30 issues for project addition`
- Wikiの Python indentation エラー

**これは古いコードが実行されている証拠です。**

### 解決手順
```bash
# 1. 環境をクリーンアップ
python scripts/cleanup_force_refresh.py

# 2. 環境を確認
python scripts/verify_environment.py

# 3. ワークフローを手動実行
# GitHub Actions タブで「🚀 Team Development Setup v3.0 (CONSOLIDATED)」を実行
```

## 📝 参考資料

- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)
- [Figma デザイン](https://www.figma.com/file/l8Zzw1wPJBitm0bQMNXTdB/イマココSNS)
