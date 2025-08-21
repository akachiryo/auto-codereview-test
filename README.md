# イマココSNS開発プロジェクト

このプロジェクトは、未経験エンジニア（アカデミー生）を対象としたチーム開発研修用リポジトリです。

## 🚀 チーム開発環境自動セットアップ

### バッチ処理による安定した自動化

[![🚀 Main Setup](https://img.shields.io/badge/🚀_Main_Setup-Start_Here-success?style=for-the-badge&logo=github)](../../actions/workflows/team-setup-main.yml)

**リポジトリをcloneまたはtemplateでコピーし、上記ボタンをクリックして段階的に以下を自動生成：**

### 🔄 自動セットアップフロー

#### **Step 1: メインセットアップ** ← まずここから開始
- 📊 **3つのGitHub Projects V2**
  - `イマココSNS（タスク）` - 開発タスク管理
  - `イマココSNS（テスト）` - テスト管理
  - `イマココSNS（KPTA）` - ふりかえり管理
  
- 💬 **GitHub Discussions**
  - 自動で有効化
  - 議事録テンプレートの投稿
  
- 📚 **GitHub Wiki**
  - HOMEページ
  - ルール（初期は空）
  - キックオフ（初期は空）
  - テーブル設計書（`data/imakoko_sns_tables.csv`から自動生成）

#### **Step 2-5: Issue作成バッチ** ← 自動で順次実行
- 🎯 **197件の全GitHub Issues**
  - **Batch 1**: Issues 1-50
  - **Batch 2**: Issues 51-100  
  - **Batch 3**: Issues 101-150
  - **Batch 4**: Issues 151-197
  - 自動ラベル付与とプロジェクトへの紐付け
  - Rate Limit完全対応

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

### 2. ~~Wikiの初期化~~ ← 不要！

~~Wikiの初期化は自動化されているため手動操作不要です~~
✅ **Wiki有効化とページ作成は完全自動化済み**

### 3. 自動セットアップの実行

1. 上記の「🚀 Main Setup」ボタンをクリック
2. `Run workflow` をクリック  
3. `Run workflow` ボタンをクリックして実行
4. **重要**: メインセットアップが完了すると、Issue作成バッチが自動で順次実行されます
5. [Actions](../../actions) タブで全体の進行状況を確認
6. 全バッチ完了まで約10-15分程度お待ちください

### 📊 実行監視

- **メインセットアップ**: Projects、Wiki、Discussionsを作成
- **Issue Batch 1-4**: 自動で30秒間隔で順次実行
- **完了確認**: 最終バッチで全体サマリーを表示

## 📋 生成されるリソース

### GitHub Projects
- [Projects](../../projects) で3つのプロジェクトが確認できます
- **197件**のタスクとテストIssuesが各プロジェクトに自動紐付け

### GitHub Issues  
- [Issues](../../issues) で**197件**のIssuesが確認できます
- タスク: 15件、テスト: 182件
- 適切なラベルが自動付与されプロジェクトに紐付け済み

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

## 📝 参考資料

- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)
- [Figma デザイン](https://www.figma.com/file/l8Zzw1wPJBitm0bQMNXTdB/イマココSNS)
- [GitHub ベースリポジトリ](https://github.com/prum-jp/imakoko-base)

## 📝 ライセンス

MIT License