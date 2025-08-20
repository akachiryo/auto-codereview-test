#!/usr/bin/env python3
"""
GitHub自動セットアップスクリプト
Wiki、Projects、Issuesを自動生成
"""

import os
import json
import time
import csv
import requests
from typing import Dict, List, Any

# 環境変数から設定を取得
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO = os.environ.get('REPO')
REPO_OWNER, REPO_NAME = REPO.split('/') if REPO else (None, None)

# GitHub API設定
API_BASE = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

# GraphQL API設定
GRAPHQL_URL = 'https://api.github.com/graphql'
GRAPHQL_HEADERS = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
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


def create_wiki():
    """Wikiページを作成"""
    print("\n📚 Creating Wiki pages...")
    
    # テーブル設計書の作成
    tables_content = generate_table_design()
    
    # 参考リンクページの作成
    links_content = """# 参考リンク

## チーム開発説明資料
- [チーム開発説明資料](https://docs.google.com/presentation/d/1XO9Ru_5e85g63vwidmGGKmOZdUMKjqPG/edit?slide=id.p1#slide=id.p1)

## プロジェクト関連リンク
- [Issues](https://github.com/{repo}/issues)
- [Projects](https://github.com/{repo}/projects)
- [Discussions](https://github.com/{repo}/discussions)
""".format(repo=REPO)
    
    # Wiki content をファイルとして保存（手動でWikiに貼り付け用）
    os.makedirs('wiki_content', exist_ok=True)
    
    with open('wiki_content/table-design.md', 'w', encoding='utf-8') as f:
        f.write(tables_content)
    
    with open('wiki_content/reference-links.md', 'w', encoding='utf-8') as f:
        f.write(links_content)
    
    print("📝 Wiki content saved to wiki_content/ directory")
    print("   Please manually create Wiki pages with the generated content")


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


def create_projects():
    """GitHub Projectsを作成"""
    print("\n📊 Creating Projects...")
    
    # GraphQLでプロジェクトを作成
    query = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 {
          id
          number
          title
        }
      }
    }
    """
    
    # リポジトリIDを取得
    repo_data = make_request('GET', f"{API_BASE}/repos/{REPO}")
    if repo_data.status_code != 200:
        print(f"❌ Failed to get repository info: {repo_data.text}")
        return
    
    repo_id = repo_data.json()['node_id']
    
    # プロジェクトを作成
    variables = {
        'ownerId': repo_id,
        'title': 'イマココSNS開発'
    }
    
    result = graphql_request(query, variables)
    if not result or 'createProjectV2' not in result:
        print("❌ Failed to create project")
        return None
    
    project = result['createProjectV2']['projectV2']
    project_id = project['id']
    print(f"✅ Created project: {project['title']} (#{project['number']})")
    
    # プロジェクトのフィールドとビューを設定
    setup_project_fields_and_views(project_id)
    
    return project_id


def setup_project_fields_and_views(project_id: str):
    """プロジェクトのフィールドとビューを設定"""
    
    # ステータスフィールドを作成
    create_status_field_query = """
    mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]) {
      createProjectV2Field(input: {
        projectId: $projectId,
        dataType: SINGLE_SELECT,
        name: $name,
        singleSelectOptions: $options
      }) {
        field {
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
        {"name": "Product Backlog", "color": "GRAY"},
        {"name": "Sprint Backlog", "color": "BLUE"},
        {"name": "In Progress", "color": "YELLOW"},
        {"name": "Review", "color": "ORANGE"},
        {"name": "Done", "color": "GREEN"}
    ]
    
    variables = {
        'projectId': project_id,
        'name': 'Status',
        'options': task_statuses
    }
    
    result = graphql_request(create_status_field_query, variables)
    if result:
        print("✅ Created Status field for project")
    
    # テスト用ステータス
    test_statuses = [
        {"name": "Todo", "color": "GRAY"},
        {"name": "In Progress", "color": "YELLOW"},
        {"name": "Done", "color": "GREEN"}
    ]
    
    variables = {
        'projectId': project_id,
        'name': 'Test Status',
        'options': test_statuses
    }
    
    result = graphql_request(create_status_field_query, variables)
    if result:
        print("✅ Created Test Status field for project")


def create_issues(project_id: str = None):
    """CSVファイルからIssuesを作成"""
    print("\n🎯 Creating Issues...")
    
    task_csv_path = 'data/imakoko_sns_task_template.csv'
    test_csv_path = 'data/imakoko_sns_test_template.csv'
    
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
    
    # プロジェクトにIssueを追加
    if project_id:
        add_issues_to_project(project_id, task_issues, 'Product Backlog')
        add_issues_to_project(project_id, test_issues, 'Todo')
    
    print(f"✅ Created {len(task_issues)} task issues and {len(test_issues)} test issues")


def create_issues_from_csv(csv_path: str, issue_type: str) -> List[Dict]:
    """CSVファイルからIssueを作成"""
    created_issues = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # タスクCSVの場合
                if 'title' in row:
                    title = row['title']
                    body = row.get('description', '')
                    labels = row.get('labels', '').split(',')
                # テストCSVの場合
                elif 'item' in row:
                    title = f"テスト: {row['screen']} - {row['item']}"
                    body = f"""## テストタイプ
{row.get('type', '')}

## 画面
{row.get('screen', '')}

## カテゴリ
{row.get('category', '')}

## 確認手順
{row.get('procedure', '')}

## 期待値
{row.get('expected', '')}"""
                    labels = row.get('labels', 'test').split(',')
                else:
                    continue
                
                # Issue作成
                issue_data = {
                    'title': title,
                    'body': body,
                    'labels': [label.strip() for label in labels if label.strip()]
                }
                
                response = make_request(
                    'POST',
                    f"{API_BASE}/repos/{REPO}/issues",
                    json=issue_data
                )
                
                if response.status_code == 201:
                    issue = response.json()
                    created_issues.append(issue)
                    print(f"  ✅ Created: {title}")
                else:
                    print(f"  ❌ Failed: {title} - {response.text}")
                
                # Rate limit対策
                time.sleep(0.5)
                
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
    
    return created_issues


def add_issues_to_project(project_id: str, issues: List[Dict], status: str):
    """IssueをProjectに追加"""
    if not issues:
        return
    
    print(f"  Adding {len(issues)} issues to project...")
    
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    """
    
    for issue in issues:
        variables = {
            'projectId': project_id,
            'contentId': issue['node_id']
        }
        
        result = graphql_request(query, variables)
        if result:
            print(f"    ✅ Added to project: {issue['title']}")
        
        time.sleep(0.3)


def main():
    """メイン処理"""
    print("🚀 Starting GitHub Setup...")
    print(f"📦 Repository: {REPO}")
    
    if not GITHUB_TOKEN or not REPO:
        print("❌ Error: GITHUB_TOKEN and REPO environment variables are required")
        return 1
    
    # Wiki作成
    create_wiki()
    
    # Projects作成
    project_id = create_projects()
    
    # Issues作成
    create_issues(project_id)
    
    print("\n✨ Setup completed!")
    print(f"📌 Next steps:")
    print(f"  1. Go to https://github.com/{REPO}/wiki to create Wiki pages")
    print(f"  2. Copy content from wiki_content/ directory")
    print(f"  3. Check Projects at https://github.com/{REPO}/projects")
    print(f"  4. Review Issues at https://github.com/{REPO}/issues")
    
    return 0


if __name__ == '__main__':
    exit(main())