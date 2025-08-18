# 🚀 GitHub Team Development Environment Setup

BacklogからGitHub完結型のチーム開発環境へ自動移行するツールセットです。

## 📋 概要

現在のチーム開発環境：
- GitHub（コード管理）
- Googleスプレッドシート（テーブル定義書・テスト仕様書）  
- Backlog（タスク管理）

↓ **自動化により移行** ↓

GitHub完結型環境：
- 📋 **GitHub Issues** (タスク管理)
- 📚 **GitHub Wiki** (ドキュメント管理)
- 💬 **GitHub Discussions** (チーム議論)
- 📊 **GitHub Projects** (プロジェクト管理)

## 🛠️ セットアップ方法

### 1. ワンクリックセットアップ（推奨）

1. リポジトリのREADMEで **🚀 Team Setup** ボタンをクリック
2. GitHub Actions画面で設定を選択して実行

### 2. 手動セットアップ

```bash
# 1. 依存関係インストール
pip install -r requirements.txt

# 2. 環境変数設定
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="owner/repo-name"

# 3. セットアップ実行
./scripts/setup.sh
```

### 3. 個別セットアップ

```bash
# Issues作成のみ
python scripts/csv-to-issues.py --repo owner/repo --token $GITHUB_TOKEN

# Wiki作成のみ  
python scripts/create-wiki.py --repo owner/repo --token $GITHUB_TOKEN

# Discussions作成のみ
python scripts/create-discussions.py --repo owner/repo --token $GITHUB_TOKEN

# Projects作成のみ
python scripts/setup-projects.py --repo owner/repo --token $GITHUB_TOKEN
```

## 📁 ディレクトリ構造

```
setup-tools/
├── scripts/                 # セットアップスクリプト
│   ├── setup.sh             # メイン実行スクリプト
│   ├── csv-to-issues.py     # CSV→Issues変換
│   ├── create-wiki.py       # Wiki生成
│   ├── create-discussions.py # Discussions生成
│   └── setup-projects.py    # Projects設定
├── templates/               # テンプレートファイル
│   ├── wiki/
│   │   └── table-design.md  # テーブル設計書テンプレート
│   └── discussions/
│       └── meeting-template.md # 議事録テンプレート
├── data/
│   └── sample-tasks.csv     # サンプルタスクデータ
├── requirements.txt         # Python依存関係
└── README.md               # このファイル
```

## 📊 BacklogデータをGitHubに移行

### CSVフォーマット

BacklogからエクスポートしたCSVを `data/sample-tasks.csv` に配置：

| 項目 | GitHub Issues変換先 |
|------|-------------------|
| 件名（必須） | Issue Title |
| 詳細 | Issue Body |
| 種別名（必須） | Label (type:task, type:bug等) |
| 優先度名 | Label (priority:high等) |
| 担当者ユーザ名 | Assignee |
| 親課題 | Parent Issue参照 |

### 変換例

```csv
件名（必須）,詳細,種別名（必須）,優先度名,担当者ユーザ名
【SNS】ユーザー登録機能,ユーザー登録画面の実装,タスク,高,yamada
【SNS】ログイン機能,ログイン画面の実装,タスク,中,tanaka
```

↓ 変換後 ↓

- **Issue**: `【SNS】ユーザー登録機能` 
- **Labels**: `task`, `priority:high`
- **Assignee**: `@yamada`

## 🎯 生成されるGitHubコンテンツ

### GitHub Issues
- BacklogタスクをIssuesに変換
- 種別・優先度をラベルで管理
- 担当者の自動アサイン

### GitHub Wiki  
- テーブル設計書
- API設計書
- 開発環境構築手順
- Git運用ルール

### GitHub Discussions
- 議事録テンプレート
- プロジェクト概要
- アイデア・提案募集
- ナレッジベース

### GitHub Projects
- **タスク管理ボード**: ToDo/In Progress/In Review/Done
- **テスト管理ボード**: テストケース管理
- **スプリント管理**: アジャイル開発用

## ⚙️ 設定オプション

### 環境変数

```bash
# 必須
GITHUB_TOKEN=ghp_xxxxxxxxxxxx    # GitHubトークン
GITHUB_REPO=owner/repo-name      # リポジトリ名

# オプション
CSV_FILE=data/custom-tasks.csv   # カスタムCSVファイル
GITHUB_API_URL=https://api.github.com  # GitHub Enterprise用
```

### GitHub Token必要スコープ

- `repo` (リポジトリフルアクセス)
- `write:discussion` (Discussions作成・編集)
- `project` (Projects作成・編集)

## 🚨 トラブルシューティング

### よくある問題

**1. GitHub Token権限不足**
```bash
Error: 403 Forbidden
```
→ トークンのスコープを確認（repo, write:discussion, project）

**2. CSV読み込みエラー**  
```bash
Error: CSV file not found
```
→ ファイルパスを確認、UTF-8で保存されているかチェック

**3. Wiki作成失敗**
```bash
Error: Wiki repository doesn't exist
```
→ リポジトリのSettings > Wikiを有効化

**4. Projects作成失敗**
```bash
Error: GraphQL Error
```  
→ GitHub Projects v2が有効か確認

### デバッグモード

```bash
# ドライランで確認
./scripts/setup.sh --dry-run

# 詳細ログ出力
export DEBUG=true
python scripts/csv-to-issues.py --dry-run
```

## 🤝 カスタマイズ

### テンプレート編集

```bash
# Wikiテンプレート編集
vi templates/wiki/table-design.md

# Discussionsテンプレート編集  
vi templates/discussions/meeting-template.md
```

### 新しいスクリプト追加

1. `scripts/` にPythonスクリプト作成
2. `setup.sh` に呼び出し処理を追加
3. `requirements.txt` に依存関係を追加

## 📈 効果測定

### 期待される効果

- ✅ **タスク管理統合**: Backlog → GitHub Issues
- ✅ **ドキュメント一元化**: Googleドライブ → GitHub Wiki
- ✅ **コミュニケーション改善**: メール → GitHub Discussions
- ✅ **プロジェクト可視化**: 手動更新 → GitHub Projects自動連携

### 移行前後の比較

| 項目 | 移行前 | 移行後 |
|------|--------|--------|
| タスク管理 | Backlog | GitHub Issues |
| ドキュメント | Googleドライブ | GitHub Wiki |
| 議事録 | メール/Slack | GitHub Discussions |
| 進捗管理 | Excel | GitHub Projects |
| 工数管理 | 手動入力 | Issue連携 |

## 📞 サポート

問題や改善提案があれば、以下の方法でお知らせください：

1. GitHub Issuesで報告
2. GitHub Discussionsで議論
3. プルリクエストで改善提案

---

**🎉 Happy Team Development with GitHub!**