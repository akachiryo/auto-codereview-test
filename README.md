# イマココSNS開発プロジェクト

このプロジェクトは、未経験エンジニア（アカデミー生）を対象としたチーム開発研修用リポジトリです。

## 🚀 チーム開発環境自動セットアップ v3.0

### 🆕 単一統合ワークフローで完全自動化

[![🚀 Team Setup v3.0](https://img.shields.io/badge/🚀_Team_Setup_v3.0-Click_to_Start-success?style=for-the-badge&logo=github)](../../actions/workflows/team-setup.yml)

**上記ボタンをクリックするだけで、全ての環境が自動セットアップされます！**

### ✨ v4.1の改善点
- 🆕 **単一統合ワークフロー**: 複数ファイルを一つに統合
- 📊 **制限なし**: 50件の制限や30件の制限を完全撤廣
- 🧠 **スマート自動処理**: CSVサイズを自動検出し最適バッチ作成
- ⚡ **依存関係なし**: 標準ライブラリのみ使用でエラー防止
- 🔍 **診断機能強化**: バージョン識別とログ改善
- 🛠️ **トラブルシューティング**: 完全な問題解決ガイド

### ✨ 自動生成される環境

- 📊 **3つのGitHub Projects V2**
  - `イマココSNS（タスク）` - 開発タスク管理
  - `イマココSNS（テスト）` - テスト管理
  - `イマココSNS（KPTA）` - ふりかえり管理
  
- 🎯 **249件のGitHub Issues**
  - タスク15件 + テスト234件（CSVの全データ）
  - 自動ラベル付与
  - プロジェクトへの自動紐付け（全件）
  - v4.1: スマート自動バッチ処理（**100%カバレッジ保証**）
  
- 💬 **GitHub Discussions**
  - 自動で有効化
  - 議事録テンプレートの投稿
  
- 📚 **GitHub Wiki**
  - HOMEページ
  - テーブル設計書（CSVから自動生成）
  - ルール・キックオフページ（テンプレート）

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

### 2. 自動セットアップの実行

1. 上記の「🚀 Team Setup」ボタンをクリック
2. `Run workflow` をクリック  
3. `Run workflow` ボタンをクリックして実行
4. [Actions](../../actions) タブで進行状況を確認
5. 約**2-3分**で全セットアップが完了します（v4.1: スマート処理）

### 📊 処理の流れ

1. **Projects作成**: 3つのプロジェクトを作成
2. **Discussions設定**: 有効化とテンプレート作成
3. **Wiki生成**: ページ自動生成とプッシュ
4. **Issue作成**: **スマート自動バッチ**で249件を一括作成（v4.1: 漏れなし）
5. **完了通知**: 全体サマリーを表示

## 📋 生成されるリソース

### GitHub Projects
- [Projects](../../projects) で3つのプロジェクトが確認できます
- **249件**のタスクとテストIssuesが各プロジェクトに自動紐付け（v3.0: 全件）

### GitHub Issues  
- [Issues](../../issues) で**249件**のIssuesが確認できます
- タスク: 15件、テスト: 234件（CSVの全データ）
- v3.0: 適切なラベルが自動付与されプロジェクトに全件紐付け

### GitHub Discussions
- [Discussions](../../discussions) で議事録テンプレートが確認できます
- 自動で有効化、議事録カテゴリーは手動作成を推奨

### GitHub Wiki
- [Wiki](../../wiki) で4つのページが確認できます
- テーブル設計書はCSVから自動生成済み

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

### バージョン確認
ワークフロー実行時に以下が表示されるかチェック:
- ワークフロー名: `🧠 Create ALL Issues - Smart Auto-Batching`
- ログに `SMART v4.1` や `INTELLIGENT PROCESSING` が表示される
- 249件のIssueが一括作成される（15タスク + 234テスト）
- 結果統計が `smart_issue_creation_result.txt` に保存される

## 📝 参考資料

- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)
- [Figma デザイン](https://www.figma.com/file/l8Zzw1wPJBitm0bQMNXTdB/イマココSNS)
- [GitHub ベースリポジトリ](https://github.com/prum-jp/imakoko-base)

## 📝 ライセンス

MIT License