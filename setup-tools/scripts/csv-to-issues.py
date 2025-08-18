#!/usr/bin/env python3
import os
import sys
import pandas as pd
from github import Github
from dotenv import load_dotenv
import argparse
import time

load_dotenv()

def get_priority_label(priority):
    priority_map = {
        '高': 'priority:high',
        '中': 'priority:medium',
        '低': 'priority:low'
    }
    return priority_map.get(priority, 'priority:medium')

def get_type_label(task_type):
    type_map = {
        'タスク': 'type:task',
        'バグ': 'type:bug',
        '機能追加': 'type:feature',
        '改善': 'type:enhancement'
    }
    return type_map.get(task_type, 'type:task')

def create_issue_from_row(repo, row, created_issues):
    try:
        title = row['件名（必須）']
        body = row.get('詳細', '')
        task_type = row.get('種別名（必須）', 'タスク')
        priority = row.get('優先度名', '中')
        assignee = row.get('担当者ユーザ名', '')
        parent_issue = row.get('親課題', '')
        
        labels = []
        type_label = get_type_label(task_type)
        priority_label = get_priority_label(priority)
        
        try:
            repo.get_label(type_label.split(':')[1])
        except:
            repo.create_label(type_label.split(':')[1], "0366d6")
        labels.append(type_label.split(':')[1])
        
        try:
            repo.get_label(priority_label.split(':')[1])
        except:
            if 'high' in priority_label:
                repo.create_label(priority_label.split(':')[1], "d73a4a")
            elif 'medium' in priority_label:
                repo.create_label(priority_label.split(':')[1], "fbca04")
            else:
                repo.create_label(priority_label.split(':')[1], "0e8a16")
        labels.append(priority_label.split(':')[1])
        
        if parent_issue and not pd.isna(parent_issue):
            if parent_issue in created_issues:
                parent_number = created_issues[parent_issue]
                body = f"Parent Issue: #{parent_number}\n\n{body}"
        
        issue_params = {
            'title': title,
            'body': body,
            'labels': labels
        }
        
        if assignee and not pd.isna(assignee):
            try:
                user = repo.get_collaborators().get_page(0)
                for collaborator in user:
                    if collaborator.login == assignee:
                        issue_params['assignee'] = assignee
                        break
            except:
                pass
        
        issue = repo.create_issue(**issue_params)
        print(f"✅ Created issue #{issue.number}: {title}")
        
        time.sleep(1)
        
        return issue
        
    except Exception as e:
        print(f"❌ Error creating issue for '{title}': {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Convert Backlog CSV to GitHub Issues')
    parser.add_argument('--csv', type=str, default='data/sample-tasks.csv',
                       help='Path to CSV file')
    parser.add_argument('--repo', type=str, help='Repository name (owner/repo)')
    parser.add_argument('--token', type=str, help='GitHub token (or use TEAM_SETUP_TOKEN env var)')
    parser.add_argument('--dry-run', action='store_true', help='Print issues without creating them')
    
    args = parser.parse_args()
    
    token = args.token or os.getenv('TEAM_SETUP_TOKEN')
    if not token:
        print("❌ Error: GitHub token not provided. Set TEAM_SETUP_TOKEN environment variable or use --token")
        sys.exit(1)
    
    repo_name = args.repo or os.getenv('GITHUB_REPO')
    if not repo_name:
        print("❌ Error: Repository name not provided. Set GITHUB_REPO environment variable or use --repo")
        sys.exit(1)
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), args.csv)
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    print(f"📋 Reading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} tasks to import")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No issues will be created\n")
        for _, row in df.iterrows():
            print(f"Would create: {row['件名（必須）']}")
            print(f"  Type: {row.get('種別名（必須）', 'タスク')}")
            print(f"  Priority: {row.get('優先度名', '中')}")
            print(f"  Assignee: {row.get('担当者ユーザ名', 'unassigned')}")
            print()
        return
    
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    print(f"\n🚀 Creating issues in {repo_name}...\n")
    
    created_issues = {}
    
    for _, row in df.iterrows():
        issue = create_issue_from_row(repo, row, created_issues)
        if issue:
            created_issues[row['件名（必須）']] = issue.number
    
    print(f"\n✅ Successfully created {len(created_issues)}/{len(df)} issues")

if __name__ == "__main__":
    main()