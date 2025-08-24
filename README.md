# Spring Boot User Management Application

シンプルなユーザー管理機能を提供するSpring Bootアプリケーションです。

## ✨ 機能

- **ユーザー管理**: CRUD操作によるユーザー管理
- **認証機能**: BCryptを使用した安全なパスワードハッシュ化
- **RESTful API**: 標準的なRESTエンドポイント
- **エラーハンドリング**: 適切な例外処理とレスポンス
- **データベース**: H2インメモリデータベース

## 🛠️ 技術スタック

- **フレームワーク**: Spring Boot 3.2.0
- **Javaバージョン**: Java 17
- **データベース**: H2 Database (インメモリ)
- **ビルドツール**: Maven
- **コンテナ**: Docker
- **セキュリティ**: Spring Security, BCrypt

## 🚀 実行方法

```bash
# Docker Compose で起動
docker-compose up --build

# または Maven で起動
mvn spring-boot:run
```

アクセス: http://localhost:8080

## 📝 APIエンドポイント

### ユーザー管理
- `GET /api/users` - 全ユーザー取得
- `GET /api/users/{id}` - ユーザー取得
- `POST /api/users` - ユーザー作成
- `PUT /api/users/{id}` - ユーザー更新
- `DELETE /api/users/{id}` - ユーザー削除
- `GET /api/users/search?name={name}` - ユーザー検索

### 認証
- `POST /api/users/login` - ログイン
- `POST /api/users/{id}/change-password` - パスワード変更

## 🔒 セキュリティ機能

- BCryptによるパスワードハッシュ化
- 環境変数による設定管理
- パスワード強度チェック（大文字、小文字、数字、特殊文字必須）
- 適切なエラーハンドリング

## 📋 プロジェクト管理機能

このリポジトリにはGitHub Actionsを使用したプロジェクト管理機能が含まれています。

### 自動セットアップワークフロー
`.github/workflows/team-setup.yml` により、以下を自動生成できます：
- GitHub Projects
- Issues
- Discussions
- Wikiページ

## 📝 ライセンス

MIT License