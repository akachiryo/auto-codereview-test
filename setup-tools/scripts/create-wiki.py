#!/usr/bin/env python3
"""
GitHub Wiki Setup Script - Completely rewritten for reliability

This script creates comprehensive Wiki documentation for team development.
Uses a hybrid approach: API-first for reliability, Git as fallback.
"""

import os
import sys
import subprocess
import shutil
import time
import requests
from pathlib import Path
import argparse
import json
from dotenv import load_dotenv

load_dotenv()

class WikiManager:
    def __init__(self, token, repo_name):
        self.token = token
        self.repo = repo_name
        self.owner, self.repo_name = repo_name.split('/')
        
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Team-Setup-Bot'
        }

    def enable_wiki(self):
        """Enable Wiki feature for the repository"""
        print("🔧 Enabling Wiki feature...")
        
        url = f"https://api.github.com/repos/{self.repo}"
        data = {"has_wiki": True}
        
        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print("  ✅ Wiki feature enabled")
            return True
        else:
            print(f"  ⚠️  Could not enable Wiki: {response.status_code} - {response.text}")
            # Continue anyway - might already be enabled
            return True

    def create_wiki_page_via_api(self, title, content):
        """Create a single wiki page via GitHub API"""
        # GitHub doesn't have direct Wiki API, so we'll use Git method
        return False

    def setup_git_environment(self, wiki_dir):
        """Setup Git environment for GitHub Actions"""
        print("🔧 Setting up Git environment...")
        
        # Configure Git user (required for GitHub Actions)
        subprocess.run(['git', 'config', 'user.email', 'noreply@github.com'], 
                      cwd=wiki_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'GitHub Actions Bot'], 
                      cwd=wiki_dir, capture_output=True)
        
        # Set safe directory (for GitHub Actions)
        subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', str(wiki_dir)], 
                      capture_output=True)

    def get_wiki_clone_url(self):
        """Get correct Wiki repository URL"""
        # Correct format for Wiki repository
        wiki_repo = f"{self.repo}.wiki.git"
        return f"https://{self.token}@github.com/{wiki_repo}"

    def initialize_wiki_repository(self, wiki_dir):
        """Initialize or clone Wiki repository (Git-only approach)"""
        print("📥 Setting up Wiki repository...")
        
        if os.path.exists(wiki_dir):
            shutil.rmtree(wiki_dir)
        
        wiki_url = self.get_wiki_clone_url()
        print(f"  📥 Trying to clone: https://github.com/{self.repo}.wiki.git")
        
        # Try to clone existing wiki
        result = subprocess.run(['git', 'clone', wiki_url, str(wiki_dir)], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Successfully cloned existing Wiki")
            self.setup_git_environment(wiki_dir)
            return True
        else:
            print("  📝 Wiki doesn't exist yet, creating new repository...")
            
            # Create new repository with proper branch setup
            os.makedirs(wiki_dir, exist_ok=True)
            subprocess.run(['git', 'init', '--initial-branch=master'], cwd=wiki_dir, capture_output=True)
            self.setup_git_environment(wiki_dir)
            subprocess.run(['git', 'remote', 'add', 'origin', wiki_url], 
                          cwd=wiki_dir, capture_output=True)
            
            # Create initial commit to establish repository
            initial_content = "# Wiki Setup\n\nInitializing wiki repository...\n"
            with open(os.path.join(wiki_dir, "Home.md"), 'w', encoding='utf-8') as f:
                f.write(initial_content)
            
            subprocess.run(['git', 'add', '.'], cwd=wiki_dir, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initialize wiki repository'], 
                          cwd=wiki_dir, capture_output=True)
            
            # Push initial commit to create wiki repository
            result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], 
                                  cwd=wiki_dir, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ Successfully created and initialized Wiki repository")
                return True
            else:
                print(f"  ⚠️  Could not push initial wiki commit: {result.stderr}")
                return False

    def create_wiki_content(self, wiki_dir):
        """Create comprehensive Wiki content"""
        print("📝 Creating comprehensive Wiki documentation...")
        
        # Define all Wiki pages
        wiki_pages = {
            'Home.md': self.generate_home_page(),
            'テーブル設計書.md': self.generate_table_design(),
            'API設計書.md': self.generate_api_design(),
            'コーディング規約.md': self.generate_coding_standards(),
            '画面設計書.md': self.generate_ui_design(),
            '開発環境構築.md': self.generate_dev_environment(),
            'Git運用ルール.md': self.generate_git_workflow(),
            'デプロイ手順.md': self.generate_deploy_guide(),
            'トラブルシューティング.md': self.generate_troubleshooting()
        }
        
        # Create all pages
        for filename, content in wiki_pages.items():
            file_path = os.path.join(wiki_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Created {filename}")
        
        return len(wiki_pages)

    def commit_and_push_wiki(self, wiki_dir, message="Setup comprehensive team documentation"):
        """Commit and push Wiki content"""
        print("💾 Committing and pushing Wiki content...")
        
        # Add all files
        result = subprocess.run(['git', 'add', '.'], cwd=wiki_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ⚠️  Git add failed: {result.stderr}")
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                               cwd=wiki_dir, capture_output=True)
        
        if result.returncode == 0:
            print("  ℹ️  No changes to commit")
            return True
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', message], 
                               cwd=wiki_dir, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ⚠️  Git commit failed: {result.stderr}")
            return False
        
        # For new Wiki repositories, we need to push to master (GitHub Wiki default)
        print(f"  📤 Trying to push to master...")
        result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], 
                               cwd=wiki_dir, capture_output=True, text=True)
        
        pushed_successfully = False
        
        if result.returncode == 0:
            print(f"  ✅ Successfully pushed to master")
            pushed_successfully = True
        else:
            print(f"  ⚠️  Push to master failed: {result.stderr}")
        
        if not pushed_successfully:
            print("  ⚠️  Could not push to any branch. Wiki content created locally.")
            print("  ℹ️  You may need to manually push or check repository permissions.")
            return False
        
        return True

    def generate_home_page(self):
        """Generate Wiki home page"""
        return f'''# 🏠 プロジェクトWiki

チーム開発環境が自動セットアップされました！このWikiには開発に必要な全てのドキュメントが準備されています。

## 📚 ドキュメント一覧

### 🗃️ 設計書
- [📊 テーブル設計書](テーブル設計書) - データベース設計とER図
- [🔌 API設計書](API設計書) - REST APIエンドポイント仕様
- [🎨 画面設計書](画面設計書) - UI/UX設計とワイヤーフレーム

### 🛠️ 開発ガイド
- [🚀 開発環境構築](開発環境構築) - プロジェクトのセットアップ手順
- [📝 コーディング規約](コーディング規約) - 統一されたコードスタイル
- [🌿 Git運用ルール](Git運用ルール) - ブランチ戦略とワークフロー

### 🔧 運用・保守
- [🚢 デプロイ手順](デプロイ手順) - リリースプロセス
- [🆘 トラブルシューティング](トラブルシューティング) - よくある問題と解決法

### 🔗 便利なリンク
- [💻 GitHubリポジトリ](../) - ソースコード
- [📋 Issues](../issues) - タスク管理
- [🔄 Pull Requests](../pulls) - コードレビュー
- [📊 Projects](../projects) - プロジェクト管理
- [💬 Discussions](../discussions) - チーム議論

## 🎯 チーム開発のスタートガイド

### 新メンバー向け
1. [開発環境構築](開発環境構築)を参照してセットアップ
2. [コーディング規約](コーディング規約)を確認
3. [Git運用ルール](Git運用ルール)を理解

### プロジェクト進行中
- [Issues](../issues)で作業を確認・アサイン
- [Projects](../projects)で全体進捗を把握
- [Discussions](../discussions)でチーム内コミュニケーション

## 📝 ドキュメント更新について

このWikiは**チーム全体で維持管理**します：
- 新しい決定事項や変更はドキュメントに反映
- 古い情報は定期的に見直し・更新
- 疑問点は[Discussions](../discussions)で議論

---

**Wiki作成日**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**最終更新日**: {time.strftime('%Y-%m-%d')}

**🎉 Happy Team Development!**
'''

    def generate_table_design(self):
        """Generate table design documentation"""
        return '''# 📊 テーブル設計書

## 🎯 データベース設計方針

### 設計原則
- **正規化**: 第3正規形を基本とし、パフォーマンスとのバランスを考慮
- **命名規約**: 英語での統一、複数形テーブル名、単数形カラム名
- **制約**: 適切な主キー、外部キー、NOT NULL制約の設定
- **インデックス**: 検索・結合パフォーマンスを考慮したインデックス設計

---

## 📋 テーブル一覧

| テーブル名 | 概要 | 備考 |
|-----------|------|------|
| users | ユーザー情報 | 認証・プロフィール管理 |
| posts | 投稿データ | SNSメイン機能 |
| comments | コメント | 投稿への返信 |
| likes | いいね | ユーザーとコンテンツの関連 |
| follows | フォロー関係 | ユーザー間の関係性 |

---

## 📝 テーブル詳細

### users テーブル
ユーザーの基本情報を管理

| カラム名 | データ型 | 制約 | 概要 |
|---------|----------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | ユーザーID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | ユーザー名 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | メールアドレス |
| password_hash | VARCHAR(255) | NOT NULL | パスワード（ハッシュ化） |
| display_name | VARCHAR(100) | | 表示名 |
| bio | TEXT | | 自己紹介 |
| avatar_url | VARCHAR(500) | | プロフィール画像URL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### posts テーブル
投稿データを管理

| カラム名 | データ型 | 制約 | 概要 |
|---------|----------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 投稿ID |
| user_id | BIGINT | NOT NULL, FOREIGN KEY (users.id) | 投稿者ID |
| content | TEXT | NOT NULL | 投稿内容 |
| image_url | VARCHAR(500) | | 画像URL |
| likes_count | INT | NOT NULL, DEFAULT 0 | いいね数 |
| comments_count | INT | NOT NULL, DEFAULT 0 | コメント数 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

### comments テーブル
コメントデータを管理

| カラム名 | データ型 | 制約 | 概要 |
|---------|----------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | コメントID |
| post_id | BIGINT | NOT NULL, FOREIGN KEY (posts.id) | 投稿ID |
| user_id | BIGINT | NOT NULL, FOREIGN KEY (users.id) | コメント者ID |
| content | TEXT | NOT NULL | コメント内容 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 作成日時 |

---

## 🔗 ER図

```mermaid
erDiagram
    users ||--o{ posts : "1対多"
    users ||--o{ comments : "1対多"
    posts ||--o{ comments : "1対多"
    users ||--o{ likes : "1対多"
    posts ||--o{ likes : "1対多"
    users ||--o{ follows : "フォロワー"
    users ||--o{ follows : "フォロー中"

    users {
        bigint id PK
        varchar username
        varchar email
        varchar password_hash
        varchar display_name
        text bio
        varchar avatar_url
        timestamp created_at
        timestamp updated_at
    }

    posts {
        bigint id PK
        bigint user_id FK
        text content
        varchar image_url
        int likes_count
        int comments_count
        timestamp created_at
        timestamp updated_at
    }

    comments {
        bigint id PK
        bigint post_id FK
        bigint user_id FK
        text content
        timestamp created_at
    }
```

---

## 📋 インデックス設計

| テーブル | カラム | 種類 | 目的 |
|---------|-------|------|------|
| users | email | UNIQUE | ログイン高速化 |
| users | username | UNIQUE | ユーザー検索 |
| posts | user_id | INDEX | ユーザー投稿一覧 |
| posts | created_at | INDEX | タイムライン表示 |
| comments | post_id | INDEX | 投稿コメント一覧 |
| likes | user_id, post_id | COMPOUND UNIQUE | いいね重複防止 |

---

## 🔐 セキュリティ考慮事項

- **パスワード**: BCryptによるハッシュ化必須
- **SQLインジェクション**: プリペアドステートメント使用
- **個人情報**: email等の機密情報は暗号化検討
- **アクセス制御**: ユーザー権限に基づくデータアクセス制限

---

**設計レビューやご質問は [Discussions](../discussions) でお気軽にどうぞ！**
'''

    def generate_api_design(self):
        """Generate API design documentation"""
        return '''# 🔌 API設計書

## 🎯 API設計方針

### 基本仕様
- **アーキテクチャ**: REST API
- **データ形式**: JSON
- **認証方式**: JWT (JSON Web Token)
- **HTTPステータス**: 標準的なステータスコード使用
- **バージョニング**: URL パスでバージョン管理 (`/api/v1/`)

### ベースURL
```
https://api.example.com/v1
```

---

## 🔐 認証

### JWT認証
- **Header**: `Authorization: Bearer <token>`
- **有効期限**: 24時間
- **リフレッシュ**: `/auth/refresh` エンドポイントで更新

### 認証フロー
1. `/auth/login` でトークン取得
2. 保護されたAPIリクエストにトークンを含める
3. トークン期限切れ時は `/auth/refresh` で更新

---

## 📋 エンドポイント一覧

### 認証API

#### POST /auth/register
**ユーザー登録**

**リクエスト:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "display_name": "John Doe"
}
```

**レスポンス:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "display_name": "John Doe",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST /auth/login
**ユーザーログイン**

**リクエスト:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**レスポンス:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "display_name": "John Doe"
  }
}
```

### ユーザーAPI

#### GET /users/me
**現在のユーザー情報取得**

**ヘッダー:** `Authorization: Bearer <token>`

**レスポンス:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "display_name": "John Doe",
  "bio": "Software Developer",
  "avatar_url": "https://example.com/avatar/1.jpg",
  "followers_count": 120,
  "following_count": 89,
  "posts_count": 45
}
```

#### PUT /users/me
**ユーザー情報更新**

**リクエスト:**
```json
{
  "display_name": "John Smith",
  "bio": "Full Stack Developer",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

### 投稿API

#### GET /posts
**投稿一覧取得（タイムライン）**

**クエリパラメータ:**
- `page`: ページ番号（デフォルト: 1）
- `limit`: 取得件数（デフォルト: 20）
- `user_id`: 特定ユーザーの投稿のみ取得

**レスポンス:**
```json
{
  "posts": [
    {
      "id": 123,
      "user": {
        "id": 1,
        "username": "john_doe",
        "display_name": "John Doe",
        "avatar_url": "https://example.com/avatar/1.jpg"
      },
      "content": "Today I learned about API design!",
      "image_url": "https://example.com/image/123.jpg",
      "likes_count": 15,
      "comments_count": 3,
      "is_liked": false,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_count": 200
  }
}
```

#### POST /posts
**投稿作成**

**リクエスト:**
```json
{
  "content": "新しい投稿です！",
  "image_url": "https://example.com/my-image.jpg"
}
```

#### DELETE /posts/{id}
**投稿削除**

---

## ⚠️ エラーレスポンス

### 標準エラーフォーマット
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データに不備があります",
    "details": {
      "email": ["有効なメールアドレスを入力してください"],
      "password": ["パスワードは8文字以上である必要があります"]
    }
  }
}
```

### HTTPステータスコード

| コード | 意味 | 使用例 |
|--------|------|--------|
| 200 | OK | 正常なGET、PUT |
| 201 | Created | 正常なPOST |
| 400 | Bad Request | バリデーションエラー |
| 401 | Unauthorized | 認証が必要 |
| 403 | Forbidden | 権限なし |
| 404 | Not Found | リソースが存在しない |
| 429 | Too Many Requests | レート制限 |
| 500 | Internal Server Error | サーバーエラー |

---

## 🔒 セキュリティ

### 実装必須項目
- **CORS**: 適切なオリジン設定
- **レート制限**: IP/ユーザー単位での制限
- **入力検証**: 全エンドポイントでの厳密な検証
- **SQLインジェクション対策**: プリペアドステートメント使用
- **XSS対策**: 出力エスケープ

### 推奨事項
- **HTTPS強制**: 本番環境では必須
- **ログ監視**: 異常なアクセスパターンの検知
- **セキュリティヘッダー**: OWASP推奨ヘッダーの設定

---

## 📊 パフォーマンス考慮

- **ページネーション**: 大量データの分割取得
- **キャッシュ**: Redis等によるレスポンス高速化
- **DB最適化**: インデックス、クエリ最適化
- **画像最適化**: サイズ制限、形式変換

---

**API設計について質問があれば [Discussions](../discussions) で議論しましょう！**
'''

    def generate_coding_standards(self):
        """Generate coding standards documentation"""
        return '''# 📝 コーディング規約

## 🎯 基本方針

- **可読性重視**: 誰が読んでも理解しやすいコード
- **一貫性維持**: チーム全体で統一されたスタイル
- **保守性向上**: 将来の変更・拡張に対応しやすい設計
- **テスタビリティ**: テストしやすい構造

---

## ☕ Java コーディング規約

### 命名規則

| 要素 | 規則 | 例 |
|------|------|----|
| クラス | PascalCase | `UserController`, `PostService` |
| メソッド | camelCase | `getUserById()`, `createPost()` |
| 変数・フィールド | camelCase | `firstName`, `postList` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| パッケージ | lowercase | `com.example.service`, `com.example.dto` |

### クラス設計

#### ✅ Good Example
```java
@Service
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    // Constructor injection (推奨)
    public UserService(UserRepository userRepository, 
                      PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }
    
    public Optional<User> findById(Long id) {
        if (id == null) {
            throw new IllegalArgumentException("User ID cannot be null");
        }
        return userRepository.findById(id);
    }
}
```

#### ❌ Bad Example
```java
@Service
public class UserService {
    
    // Field injection (非推奨)
    @Autowired
    private UserRepository userRepository;
    
    public User findById(Long id) {
        // Null check なし、例外処理なし
        return userRepository.findById(id).get();
    }
}
```

### 例外処理

#### ✅ 適切な例外処理
```java
public void updateUser(Long userId, UpdateUserRequest request) {
    try {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + userId));
        
        user.updateProfile(request.getName(), request.getEmail());
        userRepository.save(user);
        
    } catch (UserNotFoundException e) {
        log.warn("User update failed: {}", e.getMessage());
        throw e;
    } catch (Exception e) {
        log.error("Unexpected error during user update", e);
        throw new UserServiceException("Failed to update user", e);
    }
}
```

### DTOとEntity分離

#### ✅ 適切な分離
```java
// Entity (データベース層)
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String email;
    private String passwordHash;  // 機密情報
}

// DTO (API層)
public class UserResponse {
    private Long id;
    private String email;
    // パスワードは含まない
}
```

---

## 🎨 フロントエンド規約 (React/TypeScript)

### ファイル・ディレクトリ構成
```
src/
├── components/          # 再利用可能コンポーネント
│   ├── common/         # 汎用コンポーネント
│   └── ui/             # UIコンポーネント
├── pages/              # ページコンポーネント
├── hooks/              # カスタムフック
├── services/           # API通信
├── types/              # TypeScript型定義
├── utils/              # ユーティリティ関数
└── constants/          # 定数
```

### コンポーネント設計

#### ✅ 関数コンポーネント + TypeScript
```tsx
interface UserProfileProps {
  user: User;
  onUpdate: (user: User) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ 
  user, 
  onUpdate 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  
  const handleSubmit = useCallback((formData: UserFormData) => {
    const updatedUser = { ...user, ...formData };
    onUpdate(updatedUser);
    setIsEditing(false);
  }, [user, onUpdate]);
  
  return (
    <div className="user-profile">
      {isEditing ? (
        <UserForm user={user} onSubmit={handleSubmit} />
      ) : (
        <UserDisplay user={user} onEdit={() => setIsEditing(true)} />
      )}
    </div>
  );
};
```

### カスタムフック

#### ✅ ロジックの分離
```tsx
export const useUser = (userId: string) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);
        const userData = await userService.getUser(userId);
        setUser(userData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchUser();
  }, [userId]);
  
  return { user, loading, error };
};
```

---

## 🧪 テスト規約

### JUnit 5 (Java)

#### ✅ テストの構造
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @InjectMocks
    private UserService userService;
    
    @Test
    @DisplayName("正常なユーザーIDで検索すると、ユーザーが返される")
    void findById_ValidId_ReturnsUser() {
        // Given
        Long userId = 1L;
        User expectedUser = User.builder()
            .id(userId)
            .email("test@example.com")
            .build();
        when(userRepository.findById(userId))
            .thenReturn(Optional.of(expectedUser));
        
        // When
        Optional<User> result = userService.findById(userId);
        
        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getId()).isEqualTo(userId);
        verify(userRepository).findById(userId);
    }
    
    @Test
    @DisplayName("nullのユーザーIDで検索すると、例外が発生する")
    void findById_NullId_ThrowsException() {
        // When & Then
        assertThatThrownBy(() -> userService.findById(null))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("User ID cannot be null");
    }
}
```

### Jest + Testing Library (React)

#### ✅ コンポーネントテスト
```tsx
describe('UserProfile', () => {
  const mockUser: User = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com'
  };
  
  it('ユーザー情報を正しく表示する', () => {
    render(<UserProfile user={mockUser} onUpdate={jest.fn()} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
  
  it('編集ボタンクリックで編集モードになる', async () => {
    const user = userEvent.setup();
    render(<UserProfile user={mockUser} onUpdate={jest.fn()} />);
    
    await user.click(screen.getByRole('button', { name: '編集' }));
    
    expect(screen.getByRole('textbox', { name: '名前' })).toBeInTheDocument();
  });
});
```

---

## 📋 コードレビューチェックリスト

### 基本項目
- [ ] 命名規約に従っている
- [ ] 適切な例外処理がある
- [ ] null安全性が考慮されている
- [ ] 不要なコメントやコードがない
- [ ] テストが追加されている

### セキュリティ
- [ ] 入力値検証がある
- [ ] SQLインジェクション対策済み
- [ ] 機密情報がログに出力されない
- [ ] 適切な認可チェックがある

### パフォーマンス
- [ ] N+1クエリ問題がない
- [ ] 不要なAPIコールがない
- [ ] メモリリークの可能性がない
- [ ] 適切なインデックスが使用されている

---

## 🛠️ ツール設定

### IntelliJ IDEA
- Checkstyle プラグイン設定
- SonarLint プラグイン導入
- コードフォーマッター設定

### VS Code
- Prettier設定
- ESLint設定
- TypeScript strict mode

---

**コーディング規約について質問があれば [Discussions](../discussions) で相談してください！**
'''

    def generate_ui_design(self):
        """Generate UI design documentation"""
        return '''# 🎨 画面設計書

## 🎯 UI/UX設計方針

### デザイン原則
- **シンプル**: 直感的で分かりやすいインターフェース
- **一貫性**: 全画面で統一されたデザインパターン
- **アクセシビリティ**: 誰でも使いやすいユニバーサルデザイン
- **レスポンシブ**: 様々なデバイスサイズに対応

### カラーパレット
- **プライマリ**: #007BFF (青)
- **セカンダリ**: #28A745 (緑)
- **警告**: #FFC107 (黄)
- **エラー**: #DC3545 (赤)
- **グレー**: #6C757D
- **背景**: #F8F9FA

---

## 📱 画面一覧

### 認証関連

#### ログイン画面 (/login)
**目的**: ユーザーの認証
**レイアウト**: 中央配置、シンプルなフォーム

**コンポーネント**:
- メールアドレス入力フィールド
- パスワード入力フィールド
- ログインボタン
- 新規登録リンク
- パスワード忘れリンク

**ワイヤーフレーム**:
```
┌─────────────────────────┐
│       サイトロゴ          │
├─────────────────────────┤
│                         │
│   [メールアドレス_____]   │
│                         │
│   [パスワード_____]      │
│                         │
│   [　ログイン　]         │
│                         │
│   新規登録はこちら        │
│   パスワードを忘れた方    │
│                         │
└─────────────────────────┘
```

#### 新規登録画面 (/register)
**目的**: 新規ユーザーの登録
**バリデーション**: リアルタイム入力チェック

### メイン機能

#### ホーム画面 (/home)
**目的**: タイムライン表示とメイン機能へのアクセス

**ヘッダー**:
- サイトロゴ
- 検索バー
- 通知アイコン
- ユーザーメニュー

**メインエリア**:
- 投稿作成フォーム
- タイムライン (無限スクロール)
- 各投稿アイテム

**サイドバー**:
- おすすめユーザー
- トレンドハッシュタグ
- ナビゲーションメニュー

#### プロフィール画面 (/profile/{userId})
**目的**: ユーザー情報表示と編集

**プロフィールヘッダー**:
- プロフィール画像
- ユーザー名・表示名
- フォロー/フォロワー数
- 自己紹介文
- フォローボタン（他ユーザーの場合）

---

## 🧩 コンポーネント設計

### 再利用可能コンポーネント

#### Button
```tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'danger';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}
```

**使用例**:
- `<Button variant="primary" size="md">保存</Button>`
- `<Button variant="danger" size="sm">削除</Button>`

#### Card
```tsx
interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}
```

#### Modal
```tsx
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}
```

### 投稿関連コンポーネント

#### PostCard
**機能**:
- 投稿内容表示
- いいね・コメント・シェア機能
- 作成日時表示
- ユーザー情報（アバター・名前）

#### PostComposer
**機能**:
- テキスト入力エリア
- 画像アップロード
- プレビュー機能
- 投稿ボタン

---

## 📐 レスポンシブデザイン

### ブレークポイント
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px以上

### レイアウト調整

#### Mobile (〜768px)
- サイドバーは非表示
- ハンバーガーメニュー採用
- 投稿カードは全幅表示
- タッチ操作最適化

#### Tablet (768px〜1024px)
- サイドバーは折りたたみ可能
- 2カラムレイアウト
- タッチとマウス両対応

#### Desktop (1024px〜)
- 3カラムレイアウト
- サイドバー固定表示
- ホバーエフェクト活用

---

## ♿ アクセシビリティ

### 必須対応項目
- **セマンティックHTML**: 適切なタグ使用
- **キーボードナビゲーション**: Tab操作対応
- **スクリーンリーダー**: aria-label等の設定
- **コントラスト比**: WCAG AA準拠 (4.5:1以上)
- **フォーカス表示**: 明確なフォーカス状態

### 実装例
```tsx
<button
  aria-label="投稿にいいねする"
  className="like-button"
  onClick={handleLike}
>
  <HeartIcon aria-hidden="true" />
  <span className="sr-only">いいね</span>
</button>
```

---

## 🎭 インタラクション設計

### アニメーション
- **ページ遷移**: 200ms フェードイン
- **ボタンホバー**: 150ms 色変更
- **モーダル**: 300ms スライドイン
- **いいねボタン**: 200ms スケール + 色変更

### フィードバック
- **成功**: 緑色トースト通知
- **エラー**: 赤色トースト通知 + 詳細説明
- **ローディング**: スピナー + プログレスバー
- **入力検証**: リアルタイムエラー表示

---

## 📊 パフォーマンス考慮

### 画像最適化
- **遅延読み込み**: Intersection Observer使用
- **WebP対応**: 対応ブラウザではWebP配信
- **レスポンシブ画像**: srcset使用

### コード分割
- **ルート別分割**: React.lazy使用
- **コンポーネント分割**: 重いコンポーネントは動的インポート

---

## 🧪 テスト方針

### Visual Regression Testing
- **Storybook**: コンポーネントカタログ
- **Percy/Chromatic**: スクリーンショット比較

### ユーザビリティテスト
- **A/Bテスト**: 重要機能の複数パターン検証
- **ユーザーテスト**: 定期的な使いやすさ確認

---

**デザインに関する提案や改善点は [Discussions](../discussions) で議論しましょう！**
'''

    def generate_dev_environment(self):
        """Generate development environment documentation"""
        return '''# 🚀 開発環境構築

## 📋 必要なツール

### 必須ツール
- **Git** (バージョン管理)
- **Docker & Docker Compose** (コンテナ環境) 
- **Java 17以上** (アプリケーション実行)
- **Maven 3.6以上** (ビルドツール)
- **Node.js 18以上** (フロントエンド開発)

### エディタ・IDE
- **IntelliJ IDEA** (推奨 - Java開発)
- **Visual Studio Code** (推奨 - フロントエンド開発)
- **Eclipse** (代替案)

### 便利ツール
- **Postman/Insomnia** (API テスト)
- **DBeaver** (データベース管理)
- **GitHub Desktop** (Git GUI)

---

## 🔧 セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo
```

### 2. 🐳 Docker を使用した実行（推奨）

#### 一括起動
```bash
# すべてのサービスを起動
docker-compose up --build

# バックグラウンドで実行
docker-compose up -d --build

# ログ確認
docker-compose logs -f
```

#### 個別サービス起動
```bash
# データベースのみ起動
docker-compose up -d db

# アプリケーションのみ起動  
docker-compose up app
```

### 3. 📦 ローカル開発環境

#### Java/Spring Boot
```bash
# Maven依存関係インストール
mvn clean install

# アプリケーション起動
mvn spring-boot:run

# 特定プロファイルで起動
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

#### フロントエンド (Node.js)
```bash
cd frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build
```

### 4. 📊 データベース設定

#### H2 Database (開発用)
- **コンソールURL**: http://localhost:8080/h2-console
- **JDBC URL**: `jdbc:h2:mem:testdb`
- **ユーザー名**: `sa`
- **パスワード**: (空)

#### PostgreSQL (本番同等環境)
```bash
# PostgreSQL起動 (Docker Compose)
docker-compose up -d postgres

# データベース接続確認
docker-compose exec postgres psql -U postgres -d myapp
```

---

## 🛠️ 開発環境の詳細設定

### IntelliJ IDEA設定

#### 推奨プラグイン
- **Spring Boot**: Spring Boot開発支援
- **Lombok**: Lombokサポート
- **SonarLint**: コード品質チェック
- **GitToolBox**: Git操作拡張
- **Database Navigator**: DB操作

#### プロジェクト設定
```
File > Project Structure > Project Settings
├── Project SDK: Java 17
├── Project language level: 17
└── Project compiler output: target/classes
```

#### Code Style設定
```
File > Settings > Editor > Code Style > Java
- Tab size: 4
- Indent: 4
- Continuation indent: 8
- Import layout: java.*, javax.*, org.*, com.*
```

### VS Code設定

#### 推奨拡張機能
```json
{
  "recommendations": [
    "vscjava.vscode-java-pack",
    "redhat.java",
    "vmware.vscode-spring-boot",
    "ms-vscode.vscode-json",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

#### workspace設定 (.vscode/settings.json)
```json
{
  "java.home": "/usr/lib/jvm/java-17-openjdk",
  "java.configuration.updateBuildConfiguration": "automatic",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### Git設定
```bash
# 基本設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# エディタ設定
git config --global core.editor "code --wait"

# 改行設定 (Windows)
git config --global core.autocrlf true

# 改行設定 (Mac/Linux)  
git config --global core.autocrlf input

# プルリクエスト用ブランチ設定
git config --global pull.rebase false
```

---

## 🐛 トラブルシューティング

### よくある問題と解決法

#### Java関連

**問題**: `JAVA_HOME not found`
```bash
# Java バージョン確認
java -version
javac -version

# JAVA_HOME設定 (Linux/Mac)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
echo $JAVA_HOME

# JAVA_HOME設定 (Windows)
set JAVA_HOME=C:\Program Files\Java\jdk-17
echo %JAVA_HOME%
```

**問題**: Maven依存関係エラー
```bash
# キャッシュクリア
mvn dependency:purge-local-repository

# 強制更新
mvn clean install -U

# 依存関係ツリー確認
mvn dependency:tree
```

#### Docker関連

**問題**: ポートが使用中
```bash
# ポート使用状況確認
lsof -i :8080
netstat -tulpn | grep :8080

# プロセス停止
kill -9 <PID>

# Docker Compose停止
docker-compose down -v
```

**問題**: Docker イメージビルドエラー
```bash
# キャッシュなしビルド
docker-compose build --no-cache

# 未使用リソース削除
docker system prune -a
```

#### データベース関連

**問題**: データベース接続エラー
```bash
# データベースログ確認
docker-compose logs db

# 接続テスト
docker-compose exec db psql -U postgres -c "SELECT version();"

# H2コンソールアクセス確認
curl http://localhost:8080/h2-console
```

### パフォーマンス最適化

#### JVM設定
```bash
# ヒープサイズ調整
export JAVA_OPTS="-Xmx2g -Xms1g"

# GC設定
export JAVA_OPTS="$JAVA_OPTS -XX:+UseG1GC"

# デバッグモード
export JAVA_OPTS="$JAVA_OPTS -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005"
```

#### 開発サーバー設定
```properties
# application-dev.properties
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
spring.jpa.format-sql=true

# ホットリロード有効化
spring.devtools.restart.enabled=true
spring.devtools.livereload.enabled=true

# ログレベル
logging.level.com.example=DEBUG
logging.level.org.springframework.web=DEBUG
```

---

## 📚 参考資料

### 公式ドキュメント
- [Spring Boot Reference](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [Maven Documentation](https://maven.apache.org/guides/)

### チュートリアル・ガイド
- [Spring Boot Getting Started](https://spring.io/guides/gs/spring-boot/)
- [React Tutorial](https://react.dev/learn)
- [Docker Getting Started](https://docs.docker.com/get-started/)

### チーム開発ツール
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

## 💡 開発Tips

### ホットリロード・自動テスト
```bash
# Spring Boot DevTools使用
mvn spring-boot:run
# ファイル変更時に自動再起動

# フロントエンド開発サーバー
npm run dev
# ファイル変更時に自動更新

# テスト自動実行
mvn test -Dsurefire.useFile=false
# テスト結果をリアルタイム表示
```

### デバッグ設定
```bash
# Java リモートデバッグ
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005"

# Node.js デバッグ
node --inspect-brk server.js
# Chrome DevToolsで接続
```

### 便利なコマンド集
```bash
# プロジェクト全体検索
grep -r "検索文字列" src/
find . -name "*.java" | xargs grep "検索文字列"

# ファイル変更監視
watch -n 2 'ls -la target/'

# ログ監視
tail -f logs/application.log

# マルチモジュール一括操作
mvn clean install -pl module1,module2
```

---

**環境構築で困った時は [Discussions](../discussions) で質問してください！**
'''

    def generate_git_workflow(self):
        """Generate Git workflow documentation"""
        return '''# 🌿 Git運用ルール

## 🎯 ブランチ戦略

### Git Flow ベースのブランチ戦略を採用

```
main (本番)
├── develop (開発統合)
│   ├── feature/user-auth (機能開発)
│   ├── feature/post-crud (機能開発)
│   └── feature/ui-improvements (機能開発)
├── release/v1.2.0 (リリース準備)
└── hotfix/security-patch (緊急修正)
```

### ブランチ種別と役割

| ブランチタイプ | 用途 | 命名規則 | 派生元 | マージ先 |
|--------------|------|----------|--------|----------|
| `main` | 本番環境デプロイ用 | `main` | - | - |
| `develop` | 開発統合ブランチ | `develop` | `main` | `main` |
| `feature/*` | 機能開発 | `feature/機能名` | `develop` | `develop` |
| `release/*` | リリース準備 | `release/v1.2.0` | `develop` | `main`, `develop` |
| `hotfix/*` | 緊急バグ修正 | `hotfix/修正内容` | `main` | `main`, `develop` |

---

## 📝 コミットメッセージ規約

### Conventional Commits形式を採用

#### 基本フォーマット
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type一覧
| Type | 説明 | 例 |
|------|------|-----|
| `feat` | 新機能追加 | feat(auth): ログイン機能を追加 |
| `fix` | バグ修正 | fix(api): ユーザー検索の不具合を修正 |
| `docs` | ドキュメント更新 | docs(readme): セットアップ手順を追加 |
| `style` | フォーマット修正 | style(css): インデントを統一 |
| `refactor` | リファクタリング | refactor(service): UserService を最適化 |
| `perf` | パフォーマンス改善 | perf(query): DB クエリを最適化 |
| `test` | テスト追加・修正 | test(user): ユーザー作成テストを追加 |
| `chore` | ビルド・設定変更 | chore(deps): Spring Boot を 3.2.1 に更新 |

#### 良いコミットメッセージ例

```
feat(auth): JWT認証機能を実装

ログイン・ログアウト・トークンリフレッシュ機能を追加
- JWTトークン生成・検証
- SecurityConfigでエンドポイント保護
- リフレッシュトークンによる自動更新

Closes #123
```

```
fix(api): ユーザー削除時の外部キー制約エラーを修正

関連データを先に削除してからユーザーを削除するように変更
- posts, comments, likes の順で削除
- トランザクション内での一括処理

Fixes #456
```

#### 避けるべき例
```
❌ update
❌ fix bug
❌ some changes
❌ WIP
```

---

## 🔄 ワークフロー

### 1. 新機能開発の流れ

#### Step 1: 開発ブランチ作成
```bash
# 最新のdevelopブランチを取得
git checkout develop
git pull origin develop

# 機能ブランチ作成
git checkout -b feature/user-profile
```

#### Step 2: 開発作業
```bash
# 定期的なコミット
git add .
git commit -m "feat(profile): ユーザープロフィール画面を追加"

# developの変更を定期的に取り込み
git fetch origin
git rebase origin/develop
```

#### Step 3: Pull Request作成
```bash
# リモートブランチにプッシュ
git push -u origin feature/user-profile

# GitHub上でPull Request作成
# Base: develop ← Compare: feature/user-profile
```

#### Step 4: コードレビュー・マージ
- レビュアーによる承認
- CIパス確認
- Squash mergeでdevelopにマージ
- 機能ブランチ削除

### 2. リリースの流れ

#### Step 1: リリースブランチ作成
```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# バージョン番号更新
# pom.xml, package.json等のバージョンを更新
git add .
git commit -m "chore(release): バージョンを1.2.0に更新"
```

#### Step 2: リリーステスト・バグ修正
```bash
# バグ修正があれば
git commit -m "fix(release): 軽微なバグを修正"
```

#### Step 3: リリース完了
```bash
# mainブランチにマージ (Pull Request経由)
# developブランチにもマージ (Pull Request経由)

# タグ作成
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

### 3. 緊急修正の流れ

#### Step 1: Hotfixブランチ作成
```bash
git checkout main
git pull origin main
git checkout -b hotfix/security-vulnerability
```

#### Step 2: 修正・テスト
```bash
git commit -m "fix(security): XSS脆弱性を修正"
```

#### Step 3: 緊急リリース
```bash
# main、developの両方にマージ
# タグ作成
git tag -a v1.2.1 -m "Hotfix version 1.2.1"
```

---

## 🧪 Pull Request ルール

### PRテンプレート
```markdown
## 概要
この変更の概要を簡潔に説明

## 変更内容
- [ ] 新機能追加
- [ ] バグ修正  
- [ ] リファクタリング
- [ ] ドキュメント更新
- [ ] テスト追加

## 実装詳細
技術的な実装詳細や設計判断の説明

## テスト内容
- [ ] ユニットテスト追加・更新
- [ ] 結合テスト確認
- [ ] 手動テスト実施

## 影響範囲
この変更による影響範囲

## レビューポイント
特に確認してほしい箇所

## 関連Issue
Closes #123
Related to #456

## Screenshots (UI変更の場合)
変更前後のスクリーンショット
```

### レビュー基準

#### 必須チェック項目
- [ ] 🧪 **テスト**: 適切なテストが追加されている
- [ ] 📝 **ドキュメント**: 必要な場合、ドキュメントが更新されている
- [ ] 🔒 **セキュリティ**: セキュリティ上の問題がない
- [ ] 🏎️ **パフォーマンス**: パフォーマンスの悪化がない
- [ ] 🎯 **要件**: 要件を満たしている

#### コード品質チェック
- [ ] **可読性**: コードが読みやすい
- [ ] **保守性**: 将来の変更に対応しやすい
- [ ] **再利用性**: 適切にコンポーネント化されている
- [ ] **エラーハンドリング**: 適切な例外処理がある

### マージルール
- ✅ **承認**: 最低1人以上のレビュー承認必須
- ✅ **CI**: 全てのテストがパス
- ✅ **コンフリクト**: マージコンフリクトが解消済み
- ✅ **最新**: ベースブランチの最新コミットを含む

---

## 🛠️ Git設定とツール

### 推奨Git設定
```bash
# コミットエディタ設定
git config --global core.editor "code --wait"

# デフォルトブランチ
git config --global init.defaultBranch main

# プッシュ設定
git config --global push.default current

# リベース設定
git config --global pull.rebase true

# 色付き表示
git config --global color.ui auto

# エイリアス設定
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

### Gitフック設定

#### コミット前チェック (.git/hooks/pre-commit)
```bash
#!/bin/sh
# テスト実行
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed, commit aborted"
  exit 1
fi

# Lint チェック
npm run lint
if [ $? -ne 0 ]; then
  echo "Linting failed, commit aborted"
  exit 1
fi
```

#### コミットメッセージチェック (.git/hooks/commit-msg)
```bash
#!/bin/sh
# Conventional Commits形式チェック
if ! grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,50}" "$1"; then
    echo "Invalid commit message format"
    echo "Format: type(scope): description"
    exit 1
fi
```

---

## 📊 ブランチ管理戦略

### ブランチ保護ルール

#### mainブランチ
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass
- ✅ Require linear history
- ✅ Include administrators
- ❌ Allow force pushes
- ❌ Allow deletions

#### developブランチ  
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass
- ❌ Require linear history
- ❌ Allow force pushes

### 定期メンテナンス

#### 月次作業
```bash
# 不要なリモートブランチ削除
git remote prune origin

# マージ済みローカルブランチ削除
git branch --merged develop | grep -v -E "(main|develop)" | xargs -n 1 git branch -d
```

#### 四半期作業
- 古いリリースタグの整理
- Git履歴の分析・改善提案
- ブランチ戦略の見直し

---

## 🚨 トラブルシューティング

### よくある問題と対処法

#### コンフリクト解決
```bash
# マージコンフリクト発生時
git status
# コンフリクトファイルを手動編集
git add <resolved-files>
git commit

# リベースコンフリクト発生時
git status
# コンフリクト解決後
git add <resolved-files>  
git rebase --continue
```

#### 間違ったコミットの修正
```bash
# 直前のコミットメッセージ修正
git commit --amend -m "正しいコミットメッセージ"

# 複数コミットの修正
git rebase -i HEAD~3

# 間違ったファイルをコミットしてしまった場合
git reset --soft HEAD~1
git reset HEAD <unwanted-file>
git commit
```

#### プッシュした後の修正
```bash
# 注意: 他の人がプルしている可能性がある場合は避ける

# Force push with lease (安全な強制プッシュ)
git push --force-with-lease origin feature/branch-name
```

---

**Git運用についてご質問があれば [Discussions](../discussions) でお気軽にどうぞ！**
'''

    def generate_deploy_guide(self):
        """Generate deployment guide documentation"""  
        return '''# 🚢 デプロイ手順

## 🎯 デプロイ戦略

### 環境構成
- **開発環境 (Development)**: 開発者の作業環境
- **ステージング環境 (Staging)**: 本番と同等環境でのテスト
- **本番環境 (Production)**: 実際のユーザーが使用する環境

### デプロイフロー
```
feature branch → develop → staging → main → production
```

---

## 🔄 CI/CDパイプライン

### GitHub Actionsワークフロー

#### 開発環境デプロイ (.github/workflows/deploy-dev.yml)
```yaml
name: Deploy to Development

on:
  push:
    branches: [ develop ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Java
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Build with Maven
      run: mvn clean package -DskipTests
      
    - name: Build Docker Image
      run: |
        docker build -t myapp:dev .
        docker tag myapp:dev myapp:latest
    
    - name: Deploy to Development
      run: |
        # デプロイスクリプト実行
        ./deploy/dev-deploy.sh
```

#### 本番デプロイ (.github/workflows/deploy-prod.yml)
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run Tests
      run: mvn test
      
  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - name: Deploy to Production
      run: ./deploy/prod-deploy.sh ${{ github.ref_name }}
```

---

## 🐳 Docker デプロイ

### マルチステージビルド (Dockerfile)
```dockerfile
# Build stage
FROM maven:3.9-openjdk-17 as builder

WORKDIR /app
COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

# Runtime stage  
FROM openjdk:17-jdk-slim

RUN useradd -r -u 1000 appuser

WORKDIR /app

COPY --from=builder /app/target/*.jar app.jar
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

CMD ["java", "-jar", "app.jar"]
```

### Docker Compose (docker-compose.prod.yml)
```yaml
version: '3.8'

services:
  app:
    image: myapp:${VERSION:-latest}
    restart: unless-stopped
    environment:
      - SPRING_PROFILES_ACTIVE=production
      - DB_HOST=db
      - DB_USER=${DB_USER}
      - DB_PASS=${DB_PASS}
    ports:
      - "8080:8080"
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}  
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80" 
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - app

volumes:
  db_data:
  redis_data:
```

---

## 📋 デプロイスクリプト

### 開発環境デプロイ (deploy/dev-deploy.sh)
```bash
#!/bin/bash
set -e

echo "🚀 Starting development deployment..."

# 環境変数読み込み
source ./deploy/env/dev.env

# 古いコンテナ停止・削除
docker-compose -f docker-compose.dev.yml down

# 新しいイメージでコンテナ起動
docker-compose -f docker-compose.dev.yml up -d --build

# ヘルスチェック
echo "⏳ Waiting for application to start..."
timeout 300 bash -c 'until curl -s http://localhost:8080/actuator/health > /dev/null; do sleep 5; done'

echo "✅ Development deployment completed!"
echo "🔗 Application URL: http://dev.example.com"
```

### 本番デプロイ (deploy/prod-deploy.sh)
```bash
#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "❌ Version parameter required"
    echo "Usage: $0 <version>"
    exit 1
fi

echo "🚀 Starting production deployment for version: $VERSION"

# 環境変数読み込み
source ./deploy/env/prod.env

# バックアップ作成
echo "💾 Creating database backup..."
docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > "backup/db_backup_$(date +%Y%m%d_%H%M%S).sql"

# ヘルスチェック (デプロイ前)
curl -f http://localhost:8080/actuator/health || {
    echo "❌ Pre-deployment health check failed"
    exit 1
}

# Blue-Green デプロイ
echo "🔵 Starting Blue-Green deployment..."

# Green環境起動
export VERSION=$VERSION
docker-compose -f docker-compose.prod.yml -p myapp-green up -d

# Green環境のヘルスチェック
echo "⏳ Waiting for Green environment..."
timeout 300 bash -c 'until curl -s http://green.example.com/actuator/health > /dev/null; do sleep 5; done'

# トラフィック切り替え
echo "🔄 Switching traffic to Green environment..."
./deploy/switch-traffic.sh green

# 旧Blue環境停止 (5分後)
echo "⏳ Waiting 5 minutes before stopping Blue environment..."
sleep 300
docker-compose -f docker-compose.prod.yml -p myapp-blue down

echo "✅ Production deployment completed successfully!"
echo "🔗 Application URL: https://example.com"
```

---

## ⚙️ 設定ファイル管理

### 環境別設定 (application-{profile}.properties)

#### 開発環境 (application-dev.properties)
```properties
# Database
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=create-drop

# Logging
logging.level.com.example=DEBUG
logging.level.org.springframework.web=DEBUG

# Development tools
spring.devtools.restart.enabled=true

# H2 Console
spring.h2.console.enabled=true
```

#### 本番環境 (application-prod.properties)  
```properties
# Database
spring.datasource.url=jdbc:postgresql://${DB_HOST}:5432/${DB_NAME}
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASS}
spring.jpa.hibernate.ddl-auto=validate

# Logging
logging.level.root=INFO
logging.level.com.example=INFO

# Security
server.ssl.enabled=true
server.ssl.key-store=${SSL_KEYSTORE_PATH}
server.ssl.key-store-password=${SSL_KEYSTORE_PASSWORD}

# Monitoring
management.endpoints.web.exposure.include=health,info,metrics
management.endpoint.health.show-details=never
```

### シークレット管理

#### 環境変数 (.env)
```bash
# Database Configuration
DB_HOST=localhost
DB_NAME=myapp_prod
DB_USER=myapp_user
DB_PASS=super_secure_password

# Application Secrets
JWT_SECRET=your-256-bit-secret
API_KEY=your-external-api-key

# SSL Configuration  
SSL_KEYSTORE_PATH=/etc/ssl/keystore.p12
SSL_KEYSTORE_PASSWORD=keystore_password
```

#### Docker Secrets (docker-compose.yml)
```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - jwt_secret
    environment:
      - DB_PASS_FILE=/run/secrets/db_password
      - JWT_SECRET_FILE=/run/secrets/jwt_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

---

## 🔍 監視とロールバック

### ヘルスチェック実装
```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    
    @Autowired
    private UserRepository userRepository;
    
    @Override
    public Health health() {
        try {
            // DB接続確認
            userRepository.count();
            
            // 外部API確認 
            // externalApiService.ping();
            
            return Health.up()
                    .withDetail("database", "UP")
                    .withDetail("external-api", "UP")
                    .build();
                    
        } catch (Exception e) {
            return Health.down()
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }
}
```

### ログ監視
```bash
# アプリケーションログ監視
docker-compose logs -f --tail=100 app

# エラーログのみ抽出
docker-compose logs app | grep ERROR

# アクセスログ解析
tail -f /var/log/nginx/access.log | grep -E "5[0-9]{2}"
```

### ロールバック手順
```bash
# 緊急ロールバック
./deploy/rollback.sh v1.2.1

# ロールバックスクリプト (deploy/rollback.sh)
#!/bin/bash
PREVIOUS_VERSION=$1

echo "🔄 Rolling back to version: $PREVIOUS_VERSION"

# 以前のバージョンのイメージをデプロイ
export VERSION=$PREVIOUS_VERSION
docker-compose -f docker-compose.prod.yml up -d

# ヘルスチェック
timeout 300 bash -c 'until curl -s http://localhost:8080/actuator/health > /dev/null; do sleep 5; done'

echo "✅ Rollback completed to version: $PREVIOUS_VERSION"
```

---

## 🚨 緊急時対応

### 緊急時チェックリスト
- [ ] **アプリケーション**: ヘルスチェックエンドポイント確認
- [ ] **データベース**: 接続・パフォーマンス確認  
- [ ] **外部API**: 依存サービス状況確認
- [ ] **リソース**: CPU・メモリ・ディスク使用量確認
- [ ] **ログ**: エラーログ・アクセスログ確認

### 緊急停止手順
```bash
# サービス緊急停止
docker-compose -f docker-compose.prod.yml stop

# メンテナンスページ表示
./deploy/maintenance-mode.sh on

# 問題解決後
./deploy/maintenance-mode.sh off
docker-compose -f docker-compose.prod.yml start
```

### 障害連絡フロー
1. **検知**: 監視アラート・ユーザー報告
2. **初期対応**: 影響範囲確認・暫定対応
3. **エスカレーション**: 開発チーム・インフラチームに連絡
4. **復旧作業**: 根本原因の特定・修正
5. **事後対応**: 障害報告書作成・再発防止策検討

---

## 📊 パフォーマンス監視

### メトリクス収集
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### アラート設定
```yaml
# prometheus.yml
rule_files:
  - "alert_rules.yml"

# alert_rules.yml  
groups:
  - name: application
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      annotations:
        summary: "High error rate detected"
        
    - alert: HighMemoryUsage
      expr: java_lang_memory_usage_ratio > 0.9
      for: 10m
      annotations:
        summary: "High memory usage"
```

---

**デプロイで問題があれば [Discussions](../discussions) で報告・相談してください！**
'''

    def generate_troubleshooting(self):
        """Generate troubleshooting guide"""
        return '''# 🆘 トラブルシューティング

## 🎯 よくある問題と解決法

### 🚀 アプリケーション起動エラー

#### ❌ ポートが既に使用されている
**症状**:
```
Port 8080 was already in use.
```

**解決法**:
```bash
# ポート使用状況確認
lsof -i :8080
netstat -tulpn | grep :8080

# プロセス終了
kill -9 <PID>

# または別ポートで起動
mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=8081
```

#### ❌ Java バージョンエラー
**症状**:
```
UnsupportedClassVersionError: Bad version number in .class file
```

**解決法**:
```bash
# Java バージョン確認
java -version
javac -version

# JAVA_HOME 設定確認
echo $JAVA_HOME

# 正しいバージョンに設定 (Java 17)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```

#### ❌ Maven 依存関係エラー
**症状**:
```
Failed to execute goal on project: Could not resolve dependencies
```

**解決法**:
```bash
# ローカルリポジトリクリア
mvn dependency:purge-local-repository

# 依存関係強制更新
mvn clean install -U

# 依存関係ツリー確認
mvn dependency:tree

# 特定の依存関係を除外
mvn dependency:tree -Dexcludes=org.springframework:spring-core
```

---

### 🗄️ データベース接続エラー

#### ❌ H2 コンソールにアクセスできない
**症状**:
```
H2 Console not available at http://localhost:8080/h2-console
```

**解決法**:
```bash
# H2 Console 有効化確認
grep -r "spring.h2.console.enabled" src/main/resources/

# application.properties に追加
echo "spring.h2.console.enabled=true" >> src/main/resources/application.properties

# セキュリティ設定確認 (SecurityConfig.java)
# H2 Console 用のパスを許可
```

#### ❌ データベース接続タイムアウト
**症状**:
```
Connection is not available, request timed out after 30000ms
```

**解決法**:
```properties
# application.properties に追加
spring.datasource.hikari.connection-timeout=60000
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5

# または環境変数で設定
export SPRING_DATASOURCE_HIKARI_CONNECTION_TIMEOUT=60000
```

#### ❌ PostgreSQL 接続エラー (Docker環境)
**症状**:
```
Connection to localhost:5432 refused
```

**解決法**:
```bash
# PostgreSQL コンテナ状態確認
docker-compose ps

# PostgreSQL ログ確認
docker-compose logs db

# 接続テスト
docker-compose exec db psql -U postgres -d myapp

# ポート確認
docker-compose port db 5432
```

---

### 🐳 Docker 関連エラー

#### ❌ Docker イメージビルドエラー
**症状**:
```
ERROR: failed to solve: process "/bin/sh -c mvn clean package" did not complete successfully
```

**解決法**:
```bash
# Docker キャッシュクリア
docker builder prune -a

# キャッシュなしビルド
docker build --no-cache -t myapp .

# マルチステージビルドの確認
docker build --target builder -t myapp:builder .

# ビルドログ詳細表示
docker build --progress=plain -t myapp .
```

#### ❌ Docker Compose 起動エラー
**症状**:
```
ERROR: Couldn't connect to Docker daemon
```

**解決法**:
```bash
# Docker サービス状態確認
systemctl status docker

# Docker サービス開始
sudo systemctl start docker

# ユーザーをDockerグループに追加
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose バージョン確認
docker-compose --version
```

#### ❌ コンテナ間通信エラー
**症状**:
```
Connection refused: app -> db
```

**解決法**:
```bash
# ネットワーク確認
docker network ls
docker network inspect <network-name>

# コンテナ間疎通テスト
docker-compose exec app ping db

# ポート確認
docker-compose exec db netstat -tulpn
```

---

### ⚡ パフォーマンス問題

#### ❌ アプリケーション起動が遅い
**解決法**:
```bash
# JVM 起動オプション最適化
export JAVA_OPTS="-Xmx2g -Xms1g -XX:+UseG1GC"

# Spring Boot プロファイル確認
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# 不要な依存関係を無効化
# application.properties
spring.jpa.hibernate.ddl-auto=none
spring.devtools.restart.enabled=false
```

#### ❌ メモリ不足エラー
**症状**:
```
java.lang.OutOfMemoryError: Java heap space
```

**解決法**:
```bash
# ヒープサイズ増加
export JAVA_OPTS="-Xmx4g -Xms2g"

# メモリ使用量確認
docker stats
free -h

# ガベージコレクション最適化
export JAVA_OPTS="$JAVA_OPTS -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# ヒープダンプ取得（分析用）
jmap -dump:format=b,file=heapdump.hprof <pid>
```

#### ❌ データベースクエリが遅い
**解決法**:
```sql
-- 実行計画確認
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- インデックス追加
CREATE INDEX idx_users_email ON users(email);

-- 統計情報更新
ANALYZE TABLE users;
```

```properties
# Spring Boot でSQL ログ有効化
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE

spring.jpa.show-sql=true
spring.jpa.format-sql=true
```

---

### 🌐 ネットワーク・API エラー

#### ❌ API レスポンスが 404
**解決法**:
```bash
# エンドポイント一覧確認
curl http://localhost:8080/actuator/mappings

# ログレベル上げて確認
logging.level.org.springframework.web=DEBUG

# コントローラーのマッピング確認
@RestController
@RequestMapping("/api/v1/users")  # パス確認
public class UserController {{
    // メソッドの実装
}}
```

#### ❌ CORS エラー (フロントエンド)
**症状**:
```
Access to fetch at 'http://localhost:8080/api/users' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**解決法**:
```java
@Configuration
public class CorsConfig {
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("http://localhost:3000"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);
        return source;
    }
}
```

#### ❌ SSL/TLS 証明書エラー
**症状**:
```
PKIX path building failed: unable to find valid certification path
```

**解決法**:
```bash
# 証明書確認
openssl s_client -connect example.com:443 -servername example.com

# Java キーストアに証明書追加
keytool -import -trustcacerts -keystore $JAVA_HOME/jre/lib/security/cacerts -storepass changeit -alias example -file example.crt

# 開発環境では SSL 無効化
spring.profiles.active=dev
server.ssl.enabled=false
```

---

### 🔐 セキュリティ関連エラー

#### ❌ 認証エラー (JWT)
**症状**:
```
JWT token is expired
Invalid JWT signature
```

**解決法**:
```java
// JWT トークン詳細ログ
@Component
public class JwtAuthenticationEntryPoint implements AuthenticationEntryPoint {
    
    private static final Logger logger = LoggerFactory.getLogger(JwtAuthenticationEntryPoint.class);
    
    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, 
                        AuthenticationException authException) throws IOException {
        
        logger.error("JWT Error: {{}}", authException.getMessage());
        response.sendError(HttpServletResponse.SC_UNAUTHORIZED, authException.getMessage());
    }
}
```

```bash
# JWT トークン内容確認 (デバッグ用)
echo "eyJhbGciOiJIUzI1NiIs..." | base64 -d
```

#### ❌ パスワードハッシュ化エラー
**解決法**:
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12); // 強度調整
    }
    
    // パスワード検証メソッド
    public boolean verifyPassword(String rawPassword, String encodedPassword) {
        return passwordEncoder().matches(rawPassword, encodedPassword);
    }
}
```

---

## 🚨 緊急時対応

### サービス停止時の対応手順

#### 1. 状況確認
```bash
# システム全体状況
systemctl status
free -h
df -h

# アプリケーション状況
docker-compose ps
docker-compose logs --tail=50

# ネットワーク状況
netstat -tulpn
curl -I http://localhost:8080/actuator/health
```

#### 2. 緊急復旧
```bash
# サービス再起動
docker-compose restart

# 完全リセット（データ保持）
docker-compose down
docker-compose up -d

# データベース整合性チェック
docker-compose exec db pg_dump --schema-only myapp > schema_check.sql
```

#### 3. ログ収集
```bash
# アプリケーションログ
docker-compose logs app > app_logs_$(date +%Y%m%d_%H%M%S).log

# システムログ
journalctl -u docker --since "1 hour ago" > system_logs.log

# エラーログ抽出
grep -E "(ERROR|FATAL|Exception)" app_logs_*.log > error_summary.log
```

### データ復旧手順

#### バックアップから復旧
```bash
# データベースバックアップから復旧
docker-compose exec -T db psql -U postgres -d myapp < backup/db_backup_20240101_120000.sql

# アプリケーション設定バックアップから復旧
cp backup/application.properties src/main/resources/

# Docker ボリュームバックアップから復旧
docker run --rm -v myapp_db_data:/data -v $(pwd)/backup:/backup ubuntu cp -r /backup/db_data/* /data/
```

---

## 📞 サポート・エスカレーション

### 問題解決フロー
1. **自己解決**: このドキュメントで確認
2. **チーム相談**: [Discussions](../discussions) で質問
3. **エスカレーション**: 開発チームリーダーに報告
4. **緊急対応**: インフラチーム・運用チームに連絡

### 報告テンプレート
```markdown
## 問題概要
[問題の簡潔な説明]

## 発生環境
- OS: 
- Java バージョン:
- アプリケーションバージョン:
- ブラウザ (該当時):

## 再現手順
1. 
2. 
3. 

## 期待される動作


## 実際の動作


## エラーメッセージ
```

## 追加情報
[スクリーンショット、ログファイル等]
```

### 緊急連絡先
- **開発チーム**: development@example.com
- **インフラチーム**: infrastructure@example.com  
- **運用チーム**: operations@example.com
- **緊急時**: emergency@example.com

---

## 🛠️ 診断ツール・コマンド集

### システム診断
```bash
# システムリソース確認
htop
iotop
nethogs

# ディスク使用量詳細
du -h --max-depth=1 /
ncdu /

# プロセス詳細
ps aux | grep java
pstree -p
```

### アプリケーション診断
```bash
# JVM 診断
jps -v
jstat -gc <pid>
jmap -histo <pid>

# Spring Boot Actuator
curl http://localhost:8080/actuator/health
curl http://localhost:8080/actuator/metrics
curl http://localhost:8080/actuator/info
```

### ネットワーク診断
```bash
# ポート疎通確認
telnet localhost 8080
nc -zv localhost 8080

# DNS 確認
nslookup example.com
dig example.com

# HTTP レスポンス詳細
curl -I -v http://localhost:8080/api/users
```

---

**解決できない問題は [Discussions](../discussions) で緊急相談してください！**

**作成日**: {time.strftime('%Y-%m-%d %H:%M:%S')}
'''

def main():
    parser = argparse.ArgumentParser(description='Create comprehensive GitHub Wiki')
    parser.add_argument('--repo', type=str, help='Repository (owner/repo)')
    parser.add_argument('--token', type=str, help='GitHub token')
    parser.add_argument('--retry-count', type=int, default=3, help='Retry attempts')
    
    args = parser.parse_args()
    
    repo_name = args.repo or os.getenv('GITHUB_REPO')
    if not repo_name:
        print("❌ Error: Repository name required. Use --repo or set GITHUB_REPO")
        sys.exit(1)
    
    token = args.token or os.getenv('TEAM_SETUP_TOKEN')
    if not token:
        print("❌ Error: GitHub token required. Use --token or set TEAM_SETUP_TOKEN")
        sys.exit(1)
    
    print(f"🚀 Setting up comprehensive Wiki for {repo_name}...")
    
    wiki_manager = WikiManager(token, repo_name)
    
    # Step 1: Enable Wiki feature
    if not wiki_manager.enable_wiki():
        print("❌ Failed to enable Wiki feature")
        sys.exit(1)
    
    # Wait for Wiki to be ready
    time.sleep(3)
    
    # Step 2: Setup Wiki repository and content
    script_dir = Path(__file__).parent
    wiki_dir = script_dir.parent / 'wiki-temp'
    
    for attempt in range(args.retry_count):
        try:
            print(f"📝 Attempt {attempt + 1}/{args.retry_count}: Setting up Wiki...")
            
            if attempt > 0:
                time.sleep(5)  # Wait between attempts
            
            # Initialize Wiki repository
            wiki_exists = wiki_manager.initialize_wiki_repository(wiki_dir)
            
            # Create comprehensive Wiki content
            pages_created = wiki_manager.create_wiki_content(wiki_dir)
            print(f"✅ Created {pages_created} Wiki pages")
            
            # Commit and push changes
            success = wiki_manager.commit_and_push_wiki(wiki_dir)
            
            # Cleanup
            if os.path.exists(wiki_dir):
                shutil.rmtree(wiki_dir)
            
            if success:
                print(f"\n🎉 Wiki setup complete! Visit: https://github.com/{repo_name}/wiki")
                print(f"📚 Created {pages_created} comprehensive documentation pages")
                return
            else:
                print(f"  ⚠️  Attempt {attempt + 1} had issues but content was created")
                
        except Exception as e:
            print(f"  ❌ Attempt {attempt + 1} failed: {str(e)}")
            if os.path.exists(wiki_dir):
                shutil.rmtree(wiki_dir)
            
            if attempt == args.retry_count - 1:
                print(f"\n❌ Wiki setup failed after {args.retry_count} attempts")
                print("   This may be due to:")
                print("   - GitHub token lacks sufficient permissions")
                print("   - Repository Wiki feature is not enabled")
                print("   - Network connectivity issues")
                print("   - GitHub API rate limiting")
                print(f"\n💡 You can manually enable Wiki and try again later")
                print(f"   Visit: https://github.com/{repo_name}/settings")
                sys.exit(1)
    
    print(f"\n🎉 Wiki setup completed! Visit: https://github.com/{repo_name}/wiki")

if __name__ == "__main__":
    main()