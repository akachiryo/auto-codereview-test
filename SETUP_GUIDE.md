# 🚀 GitHub チーム開発環境セットアップガイド

## 🎯 このガイドの目的

BacklogとGoogleスプレッドシートを使った従来のチーム開発から、**GitHub完結型の開発環境**へ移行するための完全ガイドです。

## 📋 移行前後の比較

| 項目 | 移行前 | 移行後 |
|------|--------|--------|
| タスク管理 | Backlog | ✅ GitHub Issues |
| ドキュメント管理 | Googleスプレッドシート | ✅ GitHub Wiki |
| チーム議論 | メール・Slack分散 | ✅ GitHub Discussions |
| 進捗管理 | 手動更新 | ✅ GitHub Projects |
| 工数管理 | 手動集計 | ✅ Issues連携 |

## 🔧 事前準備（必須）

### 1. 🔑 GitHub Personal Access Token作成

#### ステップ1: Token生成
1. GitHub右上のプロフィール → **Settings**
2. 左サイドバー最下部の **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token (classic)** をクリック

#### ステップ2: Token設定
- **Note**: `チーム開発環境セットアップ用`
- **Expiration**: `90 days` (推奨)
- **スコープ選択**:
  - ✅ `repo` (Full control of private repositories)
  - ✅ `write:discussion` (Write discussions)
  - ✅ `project` (Full control of organization projects)
  - ✅ `admin:repo_hook` (Full control of repository hooks)

#### ステップ3: Token保存
🚨 **重要**: 生成されたトークンは一度しか表示されません。必ずコピーして安全な場所に保存してください。

### 2. 🏢 Repository Secret設定

#### リポジトリでの設定手順
1. リポジトリの **Settings** タブ
2. 左サイドバー **Secrets and variables** → **Actions**  
3. **New repository secret** をクリック
4. **Name**: `TEAM_SETUP_TOKEN`
5. **Secret**: 作成したTokenを貼り付け
6. **Add secret** をクリック

#### 設定確認
- Settings > Secrets で `TEAM_SETUP_TOKEN` が表示されていればOK ✅

### 3. 📊 BacklogデータのCSV準備（オプション）

Backlogからタスクデータを移行する場合:

1. **Backlogでのエクスポート**
   - プロジェクト設定 → 課題のインポート・エクスポート
   - CSVフォーマットでエクスポート

2. **CSVファイルの配置**
   ```bash
   # setup-tools/data/sample-tasks.csv を編集
   # または新しいCSVファイルを配置
   ```

3. **CSVフォーマット確認**
   ```csv
   件名（必須）,詳細,種別名（必須）,優先度名,担当者ユーザ名
   【機能追加】ユーザー登録,登録画面の実装,タスク,高,yamada
   ```

## 🚀 実行手順

### 方法1: ワンクリック実行（推奨）

1. **READMEの🚀ボタンクリック**
   - メインページの `🚀 Team Setup` ボタンをクリック

2. **GitHub Actions画面で実行**
   - `Run workflow` → `Run workflow` をクリック
   - 必要に応じてオプションを選択

3. **実行完了まで待機**
   - 通常2-3分で完了します
   - 緑のチェックマークが表示されれば成功

### 方法2: 手動実行

ローカル環境での実行:

```bash
# 1. リポジトリクローン
git clone https://github.com/your-org/your-repo.git
cd your-repo

# 2. 環境変数設定
export TEAM_SETUP_TOKEN="your_token_here"
export GITHUB_REPO="owner/repo-name"

# 3. 実行
cd setup-tools
pip install -r requirements.txt
./scripts/setup.sh
```

## 📋 実行後の確認ポイント

### ✅ 作成されるもの

#### 1. GitHub Issues
- BacklogのCSVデータが変換されてIssuesに表示
- ラベル（種別、優先度）が自動設定
- 担当者が自動アサイン

#### 2. GitHub Wiki
以下の9つのドキュメントが自動生成:
- 🏠 プロジェクトWiki (トップページ)
- 📊 テーブル設計書
- 🔌 API設計書
- 📝 コーディング規約
- 🎨 画面設計書
- 🚀 開発環境構築
- 🌿 Git運用ルール
- 🚢 デプロイ手順
- 🆘 トラブルシューティング

#### 3. GitHub Discussions
- 📅 会議議事録テンプレートが投稿済み

#### 4. GitHub Projects
- 🎯 タスク管理ボード（Issues連携済み）
- Status: To Do / In Progress / In Review / Done
- Priority: High / Medium / Low
- Effort: S / M / L / XL

### 📍 アクセス先

実行完了後、以下のリンクから各機能にアクセス:
- 📋 Issues: `https://github.com/owner/repo/issues`
- 📚 Wiki: `https://github.com/owner/repo/wiki`  
- 💬 Discussions: `https://github.com/owner/repo/discussions`
- 📊 Projects: `https://github.com/owner/repo/projects`

## 🐛 トラブルシューティング

### よくある問題と解決法

#### ❌ Token権限エラー
```
Error: 403 Forbidden
```
**解決法**: 
- Tokenのスコープを確認
- 必要スコープ: `repo`, `write:discussion`, `project`, `admin:repo_hook`

#### ❌ Wiki作成失敗  
```
Error: Wiki repository doesn't exist
```
**解決法**:
- Repository Settings > Features で Wiki を有効化
- しばらく待ってから再実行

#### ❌ Projects作成失敗
```
Error: GraphQL Error
```
**解決法**:
- GitHub Projects (Beta) が有効か確認
- Organization の場合、Projects 権限を確認

#### ❌ CSV読み込みエラー
```
Error: CSV file not found
```
**解決法**:
- CSVファイルパスを確認
- ファイルがUTF-8で保存されているか確認

### 🔄 再実行方法

#### 一部のコンポーネントのみ再実行
```bash
# Wikiのみ再作成
python setup-tools/scripts/create-wiki.py --repo owner/repo --token $TEAM_SETUP_TOKEN

# Projectsのみ再作成  
python setup-tools/scripts/setup-projects.py --repo owner/repo --token $TEAM_SETUP_TOKEN

# Discussionsのみ再作成
python setup-tools/scripts/create-discussions.py --repo owner/repo --token $TEAM_SETUP_TOKEN
```

#### 完全リセット後の再実行
1. Issues・Wiki・Projects・Discussions を手動削除
2. GitHub Actionsから再実行

## 👥 チーム導入のベストプラクティス

### 1. 段階的な導入
1. **Week 1**: 個人プロジェクトでテスト実行
2. **Week 2**: 小規模チーム（2-3人）で試行
3. **Week 3**: チーム全体で本格導入

### 2. チーム教育
- GitHub Issues の使い方講習
- Wiki ドキュメント更新ルール策定
- Discussions 活用方法の周知

### 3. 移行計画
1. **既存Backlogタスク**: CSV エクスポート → Issues 移行
2. **Googleスプレッドシート**: 内容確認 → Wiki 移行
3. **チーム慣習**: 新しいワークフローへの適応期間設定

## 📞 サポート・フィードバック

### 問題報告
- [Issues](https://github.com/your-org/your-repo/issues) でバグ報告
- [Discussions](https://github.com/your-org/your-repo/discussions) で質問・相談

### 改善提案  
- Pull Request で改善コードの提出歓迎
- 新機能要望も Issues で受付

---

**🎉 GitHub完結型チーム開発への移行、おめでとうございます！**

困った時はいつでも [Discussions](../discussions) で相談してください。