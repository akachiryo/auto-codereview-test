#!/usr/bin/env python3
"""
GitHub完結型自動化システム - シンプル実装版
Wiki、Projects、Issuesを自動生成するスクリプト
"""

import os
import time
import csv
import requests
from typing import Dict, List

# 環境変数から設定を取得
TEAM_SETUP_TOKEN = os.environ.get('TEAM_SETUP_TOKEN')
REPO = os.environ.get('REPO')
REPO_OWNER, REPO_NAME = REPO.split('/') if REPO else (None, None)
WIKI_PATH = os.environ.get('WIKI_PATH', 'wiki_content')

# GitHub API設定
API_BASE = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {TEAM_SETUP_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

# GraphQL API設定
GRAPHQL_URL = 'https://api.github.com/graphql'
GRAPHQL_HEADERS = {
    'Authorization': f'Bearer {TEAM_SETUP_TOKEN}',
    'Content-Type': 'application/json'
}


def make_request(method: str, url: str, **kwargs) -> requests.Response:
    """GitHub API リクエストの共通処理"""
    response = requests.request(method, url, headers=HEADERS, **kwargs)
    if response.status_code == 403 and 'rate limit' in response.text.lower():
        print("⏳ Rate limit reached. Waiting 60 seconds...")
        time.sleep(60)
        return make_request(method, url, **kwargs)
    return response


def graphql_request(query: str, variables: Dict = None) -> Dict:
    """GraphQL APIリクエスト"""
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    
    response = requests.post(GRAPHQL_URL, json=payload, headers=GRAPHQL_HEADERS)
    if response.status_code != 200:
        print(f"GraphQL Error: {response.status_code} - {response.text}")
        return {}
    
    data = response.json()
    if 'errors' in data:
        print(f"GraphQL Errors: {data['errors']}")
    return data.get('data', {})


def initialize_wiki_api():
    """GitHub API経由でWikiを初期化"""
    print("\n🌟 Initializing Wiki repository via GitHub API...")
    
    # まずリポジトリの情報を取得
    repo_url = f"{API_BASE}/repos/{REPO}"
    
    try:
        # リポジトリにWikiが有効化されているか確認
        response = make_request('GET', repo_url)
        if response.status_code == 200:
            repo_data = response.json()
            if repo_data.get('has_wiki', False):
                print("✅ Wiki is already enabled for this repository")
                return True
            else:
                # Wikiを有効化
                print("📝 Enabling Wiki for repository...")
                update_data = {'has_wiki': True}
                update_response = make_request('PATCH', repo_url, json=update_data)
                
                if update_response.status_code == 200:
                    print("✅ Wiki enabled successfully")
                    return True
                else:
                    print(f"⚠️ Failed to enable Wiki: {update_response.text}")
                    return True  # 続行
        
    except Exception as e:
        print(f"⚠️ Wiki initialization error: {str(e)}")
        print("💡 Continuing with Wiki creation process...")
        return True  # エラーでも続行
    
    return True


def create_wiki_pages():
    """Wikiページを作成"""
    print("\n📚 Creating Wiki pages...")
    
    # テーブル設計書の作成
    tables_content = generate_table_design()
    
    # 参考リンクページの作成
    links_content = f"""# 参考リンク

## チーム開発説明資料
- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)

## プロジェクト関連リンク
- [Issues](https://github.com/{REPO}/issues)
- [Projects](https://github.com/{REPO}/projects)
- [Discussions](https://github.com/{REPO}/discussions)

## 開発関連リンク
- [Figma デザイン](https://www.figma.com/file/l8Zzw1wPJBitm0bQMNXTdB/イマココSNS)
- [GitHub ベースリポジトリ](https://github.com/prum-jp/imakoko-base)
"""
    
    # Wikiディレクトリの存在確認と作成
    os.makedirs(WIKI_PATH, exist_ok=True)
    
    try:
        # Wiki repository に直接書き込み
        table_design_path = os.path.join(WIKI_PATH, 'テーブル設計書.md')
        reference_links_path = os.path.join(WIKI_PATH, '参考リンク.md')
        home_path = os.path.join(WIKI_PATH, 'Home.md')
        
        with open(table_design_path, 'w', encoding='utf-8') as f:
            f.write(tables_content)
        
        with open(reference_links_path, 'w', encoding='utf-8') as f:
            f.write(links_content)
            
        # Home ページの作成
        home_content = f"""# {REPO_NAME} Wiki

## 📋 ドキュメント一覧

- [[テーブル設計書]] - データベース設計の詳細
- [[参考リンク]] - プロジェクト関連リンクまとめ

## 🚀 自動生成

このWikiページは GitHub Actions により自動生成されています。

更新日時: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        with open(home_path, 'w', encoding='utf-8') as f:
            f.write(home_content)
        
        print("✅ Wiki pages generated successfully")
        print(f"📂 Files created in: {WIKI_PATH}")
        print("   • テーブル設計書.md")
        print("   • 参考リンク.md")
        print("   • Home.md")
        
    except Exception as e:
        print(f"❌ Failed to create wiki pages: {str(e)}")
        # フォールバック: ローカルディレクトリに保存
        os.makedirs('wiki_content_backup', exist_ok=True)
        with open('wiki_content_backup/table-design.md', 'w', encoding='utf-8') as f:
            f.write(tables_content)
        with open('wiki_content_backup/reference-links.md', 'w', encoding='utf-8') as f:
            f.write(links_content)
        print("📝 Wiki content saved to wiki_content_backup/ directory as fallback")


def generate_table_design() -> str:
    """CSVファイルからテーブル設計書を生成"""
    csv_path = 'data/imakoko_sns_tables.csv'
    
    if not os.path.exists(csv_path):
        return "# テーブル設計書\n\nテーブル設計ファイルが見つかりません。"
    
    content = "# テーブル設計書\n\n"
    content += "イマココSNSのデータベース設計書です。\n\n"
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # テーブルごとにグループ化
        tables = {}
        for row in rows:
            table_name = row['table_name']
            if table_name not in tables:
                tables[table_name] = {
                    'role': row['table_role'],
                    'columns': []
                }
            
            # 空のカラムは除外
            if row['logical_name'] and row['physical_name']:
                tables[table_name]['columns'].append(row)
        
        # 各テーブルの情報を出力
        for table_name, table_info in tables.items():
            content += f"## {table_name}\n\n"
            
            if table_info['role']:
                content += f"**役割**: {table_info['role']}\n\n"
            
            content += "| # | 論理名 | 物理名 | データ型 | 長さ | NOT NULL | PK | FK | 備考 |\n"
            content += "|---|--------|--------|----------|------|----------|----|----|------|\n"
            
            for col in table_info['columns']:
                num = col['column_no']
                logical = col['logical_name']
                physical = col['physical_name']
                dtype = col['data_type']
                length = col['length']
                not_null = "✓" if col['not_null'] == 'YES' else ""
                pk = "✓" if col['primary_key'] == 'YES' else ""
                fk = "✓" if col['foreign_key'] == 'YES' else ""
                note = col['note']
                
                content += f"| {num} | {logical} | {physical} | {dtype} | {length} | {not_null} | {pk} | {fk} | {note} |\n"
            
            content += "\n"
            
    except Exception as e:
        content += f"\nエラー: テーブル設計の読み込みに失敗しました - {str(e)}\n"
    
    return content


def get_repository_id():
    """リポジトリIDを取得"""
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
            owner {
                id
                __typename
            }
        }
    }
    """
    
    variables = {
        'owner': REPO_OWNER,
        'name': REPO_NAME
    }
    
    result = graphql_request(query, variables)
    if result and 'repository' in result:
        return {
            'repository_id': result['repository']['id'],
            'owner_id': result['repository']['owner']['id']
        }
    return None


def create_project():
    """GitHub Projects V2を作成（リポジトリレベル）"""
    print("\n📊 Creating GitHub Project...")
    
    repo_info = get_repository_id()
    if not repo_info:
        print("❌ Failed to get repository info")
        return None
    
    # リポジトリレベルのProjects V2を作成
    query = """
    mutation($ownerId: ID!, $repositoryId: ID!, $title: String!) {
        createProjectV2(input: {ownerId: $ownerId, repositoryId: $repositoryId, title: $title}) {
            projectV2 {
                id
                number
                title
                url
            }
        }
    }
    """
    
    variables = {
        'ownerId': repo_info['owner_id'],
        'repositoryId': repo_info['repository_id'],
        'title': 'イマココSNS'
    }
    
    result = graphql_request(query, variables)
    if not result or 'createProjectV2' not in result:
        print("❌ Failed to create project")
        return None
    
    project = result['createProjectV2']['projectV2']
    project_id = project['id']
    print(f"✅ Created project: {project['title']} (#{project['number']})")
    print(f"🔗 Project URL: {project['url']}")
    
    # プロジェクトのフィールドとビューを設定
    setup_project_fields_and_views(project_id)
    
    return project_id


def setup_project_fields_and_views(project_id: str):
    """プロジェクトのフィールドとビューを設定"""
    
    # カスタムフィールド作成用のクエリ
    create_custom_field_query = """
    mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
        createProjectV2Field(input: {
            projectId: $projectId,
            dataType: SINGLE_SELECT,
            name: $name,
            singleSelectOptions: $options
        }) {
            projectV2Field {
                ... on ProjectV2SingleSelectField {
                    id
                    name
                    options {
                        id
                        name
                    }
                }
            }
        }
    }
    """
    
    # タスク用ステータス
    task_statuses = [
        {"name": "Product Backlog", "color": "GRAY", "description": "プロダクトバックログ - 実装予定の機能やタスク"},
        {"name": "Sprint Backlog", "color": "BLUE", "description": "スプリントバックログ - 現在のスプリントで実装するタスク"},
        {"name": "In Progress", "color": "YELLOW", "description": "進行中 - 現在開発中のタスク"},
        {"name": "Review", "color": "ORANGE", "description": "レビュー中 - コードレビューやテスト中のタスク"},
        {"name": "Done", "color": "GREEN", "description": "完了 - 実装とテストが完了したタスク"}
    ]
    
    # テスト用ステータス
    test_statuses = [
        {"name": "Not Started", "color": "GRAY", "description": "未着手 - まだテストを開始していない"},
        {"name": "In Progress", "color": "YELLOW", "description": "実行中 - テストを実行中"},
        {"name": "Failed", "color": "RED", "description": "失敗 - テストが失敗している"},
        {"name": "Passed", "color": "GREEN", "description": "成功 - テストが成功している"},
        {"name": "Blocked", "color": "PURPLE", "description": "ブロック - 依存関係により実行できない"}
    ]
    
    # タスク用フィールドを作成
    task_variables = {
        'projectId': project_id,
        'name': 'TaskStatus',
        'options': task_statuses
    }
    
    task_result = graphql_request(create_custom_field_query, task_variables)
    if task_result and 'createProjectV2Field' in task_result:
        print("✅ Created TaskStatus field")
        field_info = task_result['createProjectV2Field']['projectV2Field']
        print(f"   📋 Field ID: {field_info['id']}")
        print("   📌 Task columns: Product Backlog → Sprint Backlog → In Progress → Review → Done")
    else:
        print("⚠️ TaskStatus field creation had issues")
    
    # 少し待機してからテスト用フィールドを作成（レート制限対策）
    time.sleep(1)
    
    # テスト用フィールドを作成
    test_variables = {
        'projectId': project_id,
        'name': 'TestStatus',
        'options': test_statuses
    }
    
    test_result = graphql_request(create_custom_field_query, test_variables)
    if test_result and 'createProjectV2Field' in test_result:
        print("✅ Created TestStatus field")
        field_info = test_result['createProjectV2Field']['projectV2Field']
        print(f"   📋 Field ID: {field_info['id']}")
        print("   🧪 Test columns: Not Started → In Progress → Failed/Passed → Blocked")
    else:
        print("⚠️ TestStatus field creation had issues")
    
    print("📋 Project setup completed with Task and Test fields")


def create_issues(project_id: str = None):
    """CSVファイルからIssuesを作成"""
    print("\n🎯 Creating Issues...")
    
    task_csv_path = 'data/tasks_for_issues.csv'
    test_csv_path = 'data/tests_for_issues.csv'
    
    task_issues = []
    test_issues = []
    
    # タスクIssueを作成
    if os.path.exists(task_csv_path):
        print("📝 Creating task issues...")
        task_issues = create_issues_from_csv(task_csv_path, 'task')
    
    # テストIssueを作成
    if os.path.exists(test_csv_path):
        print("🧪 Creating test issues...")
        test_issues = create_issues_from_csv(test_csv_path, 'test')
    
    # プロジェクトにIssueを追加（Projects V2用）
    if project_id:
        print(f"\n📌 Adding issues to project...")
        add_issues_to_project_v2(project_id, task_issues, 'task')
        add_issues_to_project_v2(project_id, test_issues, 'test')
    
    print(f"✅ Created {len(task_issues)} task issues and {len(test_issues)} test issues")


def create_issues_from_csv(csv_path: str, issue_type: str) -> List[Dict]:
    """CSVファイルからIssueを作成"""
    created_issues = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader, 1):
                if i > 30:  # 最初の30件のみ作成（制限対策）
                    print(f"⚠️ Limiting to first 30 {issue_type} issues to avoid rate limits")
                    break
                    
                title = row['title']
                body = row['body']
                
                # 既存のラベルを処理
                existing_labels = [label.strip() for label in row['labels'].split(',') if label.strip()]
                
                # issue_typeに基づいてラベルを追加
                if issue_type == 'task':
                    if 'task' not in existing_labels:
                        existing_labels.append('task')
                    if 'development' not in existing_labels:
                        existing_labels.append('development')
                elif issue_type == 'test':
                    if 'test' not in existing_labels:
                        existing_labels.append('test')
                    if 'qa' not in existing_labels:
                        existing_labels.append('qa')
                
                # Issue作成
                issue_data = {
                    'title': title,
                    'body': body,
                    'labels': existing_labels
                }
                
                response = make_request(
                    'POST',
                    f"{API_BASE}/repos/{REPO}/issues",
                    json=issue_data
                )
                
                if response.status_code == 201:
                    issue = response.json()
                    created_issues.append(issue)
                    print(f"  ✅ Created: {title[:50]}... [Labels: {', '.join(existing_labels)}]")
                else:
                    print(f"  ❌ Failed: {title[:50]}... - {response.text}")
                
                # Rate limit対策
                time.sleep(1)
                
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
    
    return created_issues


def add_issues_to_project_v2(project_id: str, issues: List[Dict], issue_type: str):
    """IssueをProjects V2に追加"""
    if not issues:
        return
    
    type_emoji = "📝" if issue_type == 'task' else "🧪"
    print(f"  {type_emoji} Adding {len(issues)} {issue_type} issues to project...")
    
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item {
                id
            }
        }
    }
    """
    
    for i, issue in enumerate(issues):
        if i >= 20:  # 少し制限を緩和
            print(f"    ⚠️ Limiting to first 20 {issue_type} issues for project addition")
            break
            
        variables = {
            'projectId': project_id,
            'contentId': issue['node_id']
        }
        
        result = graphql_request(query, variables)
        if result and 'addProjectV2ItemById' in result:
            print(f"    ✅ Added {issue_type}: {issue['title'][:40]}...")
        else:
            print(f"    ❌ Failed to add {issue_type}: {issue['title'][:40]}...")
        
        time.sleep(0.5)


def main():
    """メイン処理"""
    print("🚀 Starting GitHub Setup...")
    print(f"📦 Repository: {REPO}")
    
    if not TEAM_SETUP_TOKEN or not REPO:
        print("❌ Error: TEAM_SETUP_TOKEN and REPO environment variables are required")
        return 1
    
    try:
        # Wiki初期化（存在しない場合のみ）
        initialize_wiki_api()
        
        # Wiki作成
        create_wiki_pages()
        
        # Projects作成
        project_id = create_project()
        
        # Issues作成
        create_issues(project_id)
        
        print("\n✨ Setup completed!")
        print(f"📌 What was created:")
        print(f"  📚 Wiki pages automatically generated and pushed")
        print(f"  📊 GitHub Project 'イマココSNS' created")
        print(f"  📝 Task Issues created with TaskStatus field")
        print(f"  🧪 Test Issues created with TestStatus field")
        print(f"")
        print(f"📋 Access your resources:")
        print(f"  • Wiki: https://github.com/{REPO}/wiki")
        print(f"  • Projects: https://github.com/{REPO}/projects")
        print(f"  • Issues: https://github.com/{REPO}/issues")
        print(f"")
        print(f"🔧 Manual setup required: Create 2 views in your project")
        print(f"  【タスクビュー作成】")
        print(f"  1. Open your project → New view → Board")
        print(f"  2. Name: 'タスク'")
        print(f"  3. Group by: 'TaskStatus'")
        print(f"  4. Filter: label:task")
        print(f"")
        print(f"  【テストビュー作成】")
        print(f"  1. Open your project → New view → Board")
        print(f"  2. Name: 'テスト'")
        print(f"  3. Group by: 'TestStatus'")
        print(f"  4. Filter: label:test")
        print(f"")
        print(f"💡 Each view will show only relevant issues with proper status columns!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        return 1


if __name__ == '__main__':
    exit(main())