# Gemini Code Assist テスト用サンプルプロジェクト

このプロジェクトは、Gemini Code Assist GitHub App の効果を検証するためのサンプル Java Spring Boot アプリケーションです。

## 🎯 プロジェクトの目的

- **コードレビュー AI の効果検証**: 意図的に改善点を含んだコードで AI レビューの精度を確認
- **未経験者育成支援**: AI レビューを活用した効率的な学習プロセスの検証
- **チーム開発効率化**: 自動コードレビューによる開発スピード向上の測定

## 🚀 チーム開発環境自動セットアップ

### ワンクリック環境構築

[![🚀 Team Setup](https://img.shields.io/badge/🚀_Team_Setup-Click_to_Start-blue?style=for-the-badge)](../../actions/workflows/team-setup.yml)

**BacklogからGitHub完結型の開発環境へ移行！**

このボタンをクリックして以下を自動生成：
- 📋 **GitHub Issues** (BacklogのCSVデータから変換)
- 📚 **GitHub Wiki** (テーブル設計書・技術ドキュメント)
- 💬 **GitHub Discussions** (議事録テンプレート・チーム会話)
- 📊 **GitHub Projects** (タスクボード・テストボード)

### 必要な準備

1. **GitHub Tokenの設定**
   ```bash
   # Repository Settings > Secrets and variables > Actions
   # GITHUB_TOKEN を設定（スコープ: repo, write:discussion, project）
   ```

2. **CSVデータの配置**
   ```bash
   # setup-tools/data/sample-tasks.csv を編集
   # Backlogからエクスポートしたデータを配置
   ```

### 手動セットアップ（オプション）

```bash
cd setup-tools
./scripts/setup.sh --dry-run  # プレビュー
./scripts/setup.sh            # 実行
```

## 🚀 クイックスタート（従来のアプリ起動）

### 前提条件

#### 🐳 Docker を使用する場合（推奨）

- Docker
- Docker Compose

#### 📦 ローカル環境で実行する場合

- Java 17 以上
- Maven 3.6 以上

### 実行方法

#### 🐳 Docker を使用した実行（推奨）

```bash
# プロジェクトのクローン
git clone <repository-url>
cd auto-codereview-test

# Docker Compose でアプリケーションを起動
docker-compose up --build

# バックグラウンドで実行する場合
docker-compose up -d --build
```

#### 📦 Maven を使用した実行

```bash
# Maven がインストールされている場合
mvn spring-boot:run
```

#### 🔧 Docker のみを使用した実行

```bash
# Docker イメージをビルド
docker build -t auto-codereview-test .

# コンテナを実行
docker run -p 8080:8080 auto-codereview-test
```

### アクセス情報

- **アプリケーション**: http://localhost:8080
- **H2 データベースコンソール**: http://localhost:8080/h2-console
  - JDBC URL: `jdbc:h2:mem:testdb`
  - ユーザー名: `sa`
  - パスワード: (空)

## 📋 API エンドポイント

### ユーザー管理 API

| メソッド | エンドポイント                  | 説明             |
| -------- | ------------------------------- | ---------------- |
| GET      | `/api/users`                    | 全ユーザー取得   |
| GET      | `/api/users/{id}`               | 特定ユーザー取得 |
| POST     | `/api/users`                    | ユーザー作成     |
| PUT      | `/api/users/{id}`               | ユーザー更新     |
| DELETE   | `/api/users/{id}`               | ユーザー削除     |
| POST     | `/api/users/login`              | ユーザー認証     |
| GET      | `/api/users/search?name={name}` | ユーザー検索     |

### サンプルリクエスト

```bash
# ユーザー作成
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "テストユーザー",
    "email": "test@example.com",
    "password": "password123"
  }'

# ユーザー一覧取得
curl http://localhost:8080/api/users
```

## ⚠️ 意図的に含まれている問題点

このサンプルコードには、教育目的で以下の問題が意図的に含まれています：

### セキュリティ問題

- パスワードの平文保存
- SQL インジェクションの脆弱性
- 認証・認可の不備
- 機密情報のログ出力
- 弱い暗号化アルゴリズム使用

### パフォーマンス問題

- N+1 クエリ問題
- 不要な処理の実行
- 非効率なデータ取得

### 設計・保守性の問題

- フィールドインジェクションの使用
- 例外処理の不備
- 適切でないメソッド名
- DTO の不適切な使用

### テストの問題

- テストケースの不足
- エッジケースの未考慮
- セキュリティテストの不備

## 🔍 Gemini Code Assist での検証ポイント

### 期待される AI レビュー指摘事項

1. **セキュリティ関連**

   - パスワードハッシュ化の必要性
   - SQL インジェクション対策
   - 認証・認可の実装

2. **ベストプラクティス**

   - コンストラクタインジェクションの推奨
   - 適切な例外処理
   - DTO とエンティティの分離

3. **パフォーマンス**

   - クエリ最適化の提案
   - 不要な処理の削除

4. **テスト品質**
   - テストケースの追加提案
   - モックの適切な使用

## 📊 効果測定

### 測定指標

- AI が検出した問題の数と種類
- 指摘の精度（真陽性/偽陽性）
- 学習効果（レビュー前後の理解度）
- 開発効率（レビュー時間の短縮）

### 期待される効果

- **未経験者の学習加速**: 具体的な改善点の理解
- **コード品質向上**: 基本的な問題の早期発見
- **レビュー効率化**: 人間レビュアーの負荷軽減

## 🛠️ 開発環境

### 使用技術

- **フレームワーク**: Spring Boot 3.2.0
- **データベース**: H2 Database (インメモリ)
- **ORM**: Spring Data JPA
- **テスト**: JUnit 5, Mockito
- **ビルドツール**: Maven

### プロジェクト構成

```
src/
├── main/
│   ├── java/com/example/autocodereviewtest/
│   │   ├── controller/     # REST API コントローラー
│   │   ├── service/        # ビジネスロジック
│   │   ├── repository/     # データアクセス層
│   │   ├── model/          # エンティティクラス
│   │   ├── dto/            # データ転送オブジェクト
│   │   └── util/           # ユーティリティクラス
│   └── resources/
│       └── application.properties
└── test/
    └── java/               # テストクラス
```

## 📝 ライセンス

このプロジェクトは教育目的で作成されており、MIT ライセンスの下で公開されています。

## 🤝 コントリビューション

このプロジェクトは Gemini Code Assist のテスト用です。改善提案やバグ報告は歓迎しますが、意図的な問題点の修正は避けてください。

## 💡 次のステップ

1. **プロジェクトの実行確認**

   ```bash
   # Docker Compose を使用（推奨）
   docker-compose up --build

   # または Maven を使用
   mvn spring-boot:run
   ```

2. **Gemini Code Assist GitHub App をインストール**

3. **PR を作成して AI レビューを体験**

4. **指摘内容を分析して学習効果を測定**

5. **チーム内でのフィードバック収集**

---

**注意**: このコードは教育・検証目的で作成されており、本番環境での使用は推奨されません。
