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
    
    # Wiki content をファイルとして保存（GitHub API経由では直接作成不可のため）
    os.makedirs('wiki_content', exist_ok=True)
    
    with open('wiki_content/table-design.md', 'w', encoding='utf-8') as f:
        f.write(tables_content)
    
    with open('wiki_content/reference-links.md', 'w', encoding='utf-8') as f:
        f.write(links_content)
    
    print("📝 Wiki content saved to wiki_content/ directory")
    print("📌 Manual step required: Please create Wiki pages with the generated content")


def generate_table_design() -> str:
    """CSVファイルからテーブル設計書を生成"""
    csv_path = 'data/imakoko_sns_tables.csv'
    
    if not os.path.exists(csv_path):
        return "# テーブル設計書\n\nテーブル設計ファイルが見つかりません。"
    
    content = "# テーブル設計書\n\n"
    
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
        }
    }
    """
    
    variables = {
        'owner': REPO_OWNER,
        'name': REPO_NAME
    }
    
    result = graphql_request(query, variables)
    if result and 'repository' in result:
        return result['repository']['id']
    return None


def create_project():
    """GitHub Projectsを作成（リポジトリレベル）"""
    print("\n📊 Creating GitHub Project...")
    
    # REST APIを使用してリポジトリレベルのプロジェクトを作成
    project_data = {
        'name': 'イマココSNS開発',
        'body': 'イマココSNS開発用のプロジェクト管理ボード'
    }
    
    response = make_request(
        'POST',
        f"{API_BASE}/repos/{REPO}/projects",
        json=project_data
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to create project: {response.text}")
        return None
    
    project = response.json()
    project_id = project['id']
    print(f"✅ Created project: {project['name']} (#{project['number']})")
    print(f"🔗 Project URL: {project['html_url']}")
    
    # プロジェクトのカラムを設定
    setup_project_columns(project_id)
    
    return project_id


def setup_project_columns(project_id: str):
    """プロジェクトのカラムを設定"""
    
    # 基本的なカラムを作成
    columns = [
        "Product Backlog",
        "Sprint Backlog", 
        "In Progress",
        "Review",
        "Done"
    ]
    
    for column_name in columns:
        column_data = {
            'name': column_name
        }
        
        response = make_request(
            'POST',
            f"{API_BASE}/projects/{project_id}/columns",
            json=column_data
        )
        
        if response.status_code == 201:
            print(f"✅ Created column: {column_name}")
        else:
            print(f"❌ Failed to create column {column_name}: {response.text}")
        
        time.sleep(0.5)  # Rate limit対策
    
    print("📋 Project columns configured successfully")


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
    
    # プロジェクトにIssueを追加（Classic Projects用）
    if project_id:
        add_issues_to_classic_project(project_id, task_issues + test_issues)
    
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
                labels = [label.strip() for label in row['labels'].split(',') if label.strip()]
                
                # Issue作成
                issue_data = {
                    'title': title,
                    'body': body,
                    'labels': labels
                }
                
                response = make_request(
                    'POST',
                    f"{API_BASE}/repos/{REPO}/issues",
                    json=issue_data
                )
                
                if response.status_code == 201:
                    issue = response.json()
                    created_issues.append(issue)
                    print(f"  ✅ Created: {title[:50]}...")
                else:
                    print(f"  ❌ Failed: {title[:50]}... - {response.text}")
                
                # Rate limit対策
                time.sleep(1)
                
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
    
    return created_issues


def add_issues_to_classic_project(project_id: str, issues: List[Dict]):
    """IssueをClassic Projectに追加"""
    if not issues:
        return
    
    print(f"  Adding {len(issues)} issues to project...")
    
    # プロジェクトのカラムを取得
    columns_response = make_request(
        'GET',
        f"{API_BASE}/projects/{project_id}/columns"
    )
    
    if columns_response.status_code != 200:
        print("❌ Failed to get project columns")
        return
    
    columns = columns_response.json()
    if not columns:
        print("❌ No columns found in project")
        return
    
    # 最初のカラム（Product Backlog）にIssueを追加
    first_column_id = columns[0]['id']
    
    for i, issue in enumerate(issues):
        if i >= 10:  # 制限対策
            print(f"  ⚠️ Limiting to first 10 issues for project addition")
            break
            
        card_data = {
            'content_id': issue['id'],
            'content_type': 'Issue'
        }
        
        response = make_request(
            'POST',
            f"{API_BASE}/projects/columns/{first_column_id}/cards",
            json=card_data
        )
        
        if response.status_code == 201:
            print(f"    ✅ Added to project: {issue['title'][:40]}...")
        else:
            print(f"    ❌ Failed to add: {issue['title'][:40]}...")
        
        time.sleep(0.5)


def main():
    """メイン処理"""
    print("🚀 Starting GitHub Setup...")
    print(f"📦 Repository: {REPO}")
    
    if not TEAM_SETUP_TOKEN or not REPO:
        print("❌ Error: TEAM_SETUP_TOKEN and REPO environment variables are required")
        return 1
    
    try:
        # Wiki作成
        create_wiki_pages()
        
        # Projects作成
        project_id = create_project()
        
        # Issues作成
        create_issues(project_id)
        
        print("\n✨ Setup completed!")
        print(f"📌 Next steps:")
        print(f"  1. Go to https://github.com/{REPO}/wiki to create Wiki pages")
        print(f"  2. Copy content from wiki_content/ directory")
        print(f"  3. Check Projects at https://github.com/{REPO}/projects")
        print(f"  4. Review Issues at https://github.com/{REPO}/issues")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        return 1


if __name__ == '__main__':
    exit(main())