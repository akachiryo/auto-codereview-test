#!/usr/bin/env python3
import os
import sys
import requests
import json
import time
import argparse
from dotenv import load_dotenv

load_dotenv()

class GitHubProjects:
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo
        self.graphql_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_repository_info(self):
        """Get repository ID and owner info"""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
                owner {
                    id
                    login
                }
            }
        }
        """
        
        owner, name = self.repo.split('/')
        variables = {"owner": owner, "name": name}
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['repository']
        else:
            print(f"❌ Error getting repository info: {response.text}")
            return None

    def create_project(self, title, description, owner_id):
        """Create a new project (v2)"""
        mutation = """
        mutation($ownerId: ID!, $title: String!) {
            createProjectV2(input: {
                ownerId: $ownerId,
                title: $title
            }) {
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
            "ownerId": owner_id,
            "title": title
        }
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": mutation, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL Error: {data['errors']}")
                return None
            project = data['data']['createProjectV2']['projectV2']
            print(f"✅ Created project: {project['title']} (#{project['number']})")
            return project
        else:
            print(f"❌ Error creating project: {response.text}")
            return None

    def get_project_fields(self, project_id):
        """Get project fields"""
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    fields(first: 20) {
                        nodes {
                            __typename
                            ... on ProjectV2Field {
                                id
                                name
                                dataType
                            }
                            ... on ProjectV2FieldCommon {
                                id
                                name
                                dataType
                            }
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                dataType
                                options {
                                    id
                                    name
                                    color
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        variables = {"projectId": project_id}
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['node']['fields']['nodes']
        else:
            print(f"❌ Error getting project fields: {response.text}")
            return []

    def create_single_select_field(self, project_id, name, options):
        """Create a single select field with options"""
        mutation = """
        mutation($projectId: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
            createProjectV2Field(input: {
                projectId: $projectId,
                name: $name,
                dataType: $dataType,
                singleSelectOptions: $options
            }) {
                projectV2Field {
                    __typename
                    ... on ProjectV2SingleSelectField {
                        id
                        name
                        options {
                            id
                            name
                            color
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "projectId": project_id,
            "name": name,
            "dataType": "SINGLE_SELECT",
            "options": options
        }
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": mutation, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' not in data:
                field = data['data']['createProjectV2Field']['projectV2Field']
                print(f"  ✅ Created field: {name}")
                return field
        
        print(f"⚠️  Could not create field '{name}': {response.text if response.status_code != 200 else data.get('errors', '')}")
        return None

    def link_repository_to_project(self, project_id, repository_id):
        """Link repository to project"""
        mutation = """
        mutation($projectId: ID!, $repositoryId: ID!) {
            linkRepositoryToProject(input: {
                projectId: $projectId,
                repositoryId: $repositoryId
            }) {
                project {
                    id
                }
            }
        }
        """
        
        variables = {
            "projectId": project_id,
            "repositoryId": repository_id
        }
        
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json={"query": mutation, "variables": variables}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' not in data:
                print(f"  ✅ Linked repository to project")
                return True
        
        print(f"⚠️  Could not link repository to project")
        return False

def setup_task_board(gh_projects, owner_id, repository_id):
    """Setup main task management board"""
    project_config = {
        'title': '🎯 タスク管理ボード',
        'description': 'プロジェクトのメインタスク管理を行うボードです。ToDo、進行中、完了の状態でタスクを管理します。'
    }
    
    project = gh_projects.create_project(
        project_config['title'],
        project_config['description'],
        owner_id
    )
    
    if not project:
        return None
    
    gh_projects.link_repository_to_project(project['id'], repository_id)
    
    # Wait a bit for project creation to complete
    time.sleep(2)
    
    # Create Status field with options
    status_options = [
        {"name": "📝 To Do", "color": "GRAY"},
        {"name": "🔄 In Progress", "color": "YELLOW"},
        {"name": "👀 In Review", "color": "BLUE"},
        {"name": "✅ Done", "color": "GREEN"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Status", status_options)
    
    # Create Priority field
    priority_options = [
        {"name": "🔥 High", "color": "RED"},
        {"name": "🟡 Medium", "color": "YELLOW"},
        {"name": "🟢 Low", "color": "GREEN"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Priority", priority_options)
    
    # Create Effort field
    effort_options = [
        {"name": "S (1-2h)", "color": "GREEN"},
        {"name": "M (3-8h)", "color": "YELLOW"},
        {"name": "L (1-2d)", "color": "ORANGE"},
        {"name": "XL (3-5d)", "color": "RED"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Effort", effort_options)
    
    return project

def setup_test_board(gh_projects, owner_id, repository_id):
    """Setup test management board"""
    project_config = {
        'title': '🧪 テスト管理ボード',
        'description': 'テストケースとテスト実行状況を管理するボードです。'
    }
    
    project = gh_projects.create_project(
        project_config['title'],
        project_config['description'],
        owner_id
    )
    
    if not project:
        return None
    
    gh_projects.link_repository_to_project(project['id'], repository_id)
    
    time.sleep(2)
    
    # Test Status field
    test_status_options = [
        {"name": "📝 Not Started", "color": "GRAY"},
        {"name": "🧪 Testing", "color": "YELLOW"},
        {"name": "✅ Passed", "color": "GREEN"},
        {"name": "❌ Failed", "color": "RED"},
        {"name": "⚠️ Blocked", "color": "ORANGE"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Test Status", test_status_options)
    
    # Test Type field
    test_type_options = [
        {"name": "Unit Test", "color": "BLUE"},
        {"name": "Integration Test", "color": "PURPLE"},
        {"name": "E2E Test", "color": "PINK"},
        {"name": "Manual Test", "color": "GRAY"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Test Type", test_type_options)
    
    # Environment field
    env_options = [
        {"name": "Development", "color": "YELLOW"},
        {"name": "Staging", "color": "BLUE"},
        {"name": "Production", "color": "GREEN"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Environment", env_options)
    
    return project

def setup_sprint_board(gh_projects, owner_id, repository_id):
    """Setup sprint management board"""
    project_config = {
        'title': '🏃‍♂️ スプリント管理',
        'description': 'スプリント単位での開発管理を行うボードです。'
    }
    
    project = gh_projects.create_project(
        project_config['title'],
        project_config['description'],
        owner_id
    )
    
    if not project:
        return None
    
    gh_projects.link_repository_to_project(project['id'], repository_id)
    
    time.sleep(2)
    
    # Sprint field
    sprint_options = [
        {"name": "Sprint 1", "color": "BLUE"},
        {"name": "Sprint 2", "color": "GREEN"},
        {"name": "Sprint 3", "color": "YELLOW"},
        {"name": "Backlog", "color": "GRAY"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Sprint", sprint_options)
    
    # Story Points field - using text field since numbers aren't supported in single select
    story_point_options = [
        {"name": "1", "color": "GREEN"},
        {"name": "2", "color": "GREEN"},
        {"name": "3", "color": "YELLOW"},
        {"name": "5", "color": "YELLOW"},
        {"name": "8", "color": "ORANGE"},
        {"name": "13", "color": "RED"}
    ]
    
    gh_projects.create_single_select_field(project['id'], "Story Points", story_point_options)
    
    return project

def add_sample_items_to_project(gh_projects, project_id, repository_id):
    """Add sample items to project board"""
    
    # First, get all issues from the repository to add them as project items
    import requests
    
    # Get repository issues
    repo_url = f"https://api.github.com/repos/{gh_projects.repo}/issues?state=all&per_page=10"
    headers = {'Authorization': f'token {gh_projects.token}', 'Accept': 'application/vnd.github.v3+json'}
    
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        issues = response.json()
        
        for issue in issues:
            # Add issue to project
            mutation = """
            mutation($projectId: ID!, $contentId: ID!) {
                addProjectV2ItemByContentId(input: {
                    projectId: $projectId,
                    contentId: $contentId
                }) {
                    item {
                        id
                        content {
                            ... on Issue {
                                title
                                number
                            }
                        }
                    }
                }
            }
            """
            
            variables = {
                "projectId": project_id,
                "contentId": issue['node_id']
            }
            
            item_response = requests.post(
                'https://api.github.com/graphql',
                headers=gh_projects.graphql_headers,
                json={"query": mutation, "variables": variables}
            )
            
            if item_response.status_code == 200:
                item_data = item_response.json()
                if 'errors' not in item_data:
                    print(f"  ✅ Added issue #{issue['number']} to project")
                    time.sleep(0.5)  # Rate limiting

def main():
    parser = argparse.ArgumentParser(description='Setup GitHub Projects boards')
    parser.add_argument('--repo', type=str, help='Repository (owner/repo)')
    parser.add_argument('--token', type=str, help='GitHub token')
    parser.add_argument('--boards', nargs='+', choices=['task', 'test', 'sprint', 'all'], 
                       default=['all'], help='Which boards to create')
    parser.add_argument('--retry-count', type=int, default=3, help='Retry attempts')
    
    args = parser.parse_args()
    
    token = args.token or os.getenv('TEAM_SETUP_TOKEN')
    if not token:
        print("❌ Error: GitHub token required. Use --token or set TEAM_SETUP_TOKEN")
        sys.exit(1)
    
    repo_name = args.repo or os.getenv('GITHUB_REPO')
    if not repo_name:
        print("❌ Error: Repository name required. Use --repo or set GITHUB_REPO")
        sys.exit(1)
    
    boards_to_create = args.boards
    if 'all' in boards_to_create:
        boards_to_create = ['task']  # Focus on task board for reliability
    
    print(f"🚀 Setting up GitHub Projects for {repo_name}...")
    
    for attempt in range(args.retry_count):
        try:
            print(f"📊 Attempt {attempt + 1}/{args.retry_count}: Creating projects...")
            
            if attempt > 0:
                time.sleep(3)  # Wait between attempts
            
            gh_projects = GitHubProjects(token, repo_name)
            
            repo_info = gh_projects.get_repository_info()
            if not repo_info:
                raise Exception("Failed to get repository information")
            
            owner_id = repo_info['owner']['id']
            repository_id = repo_info['id']
            
            created_projects = []
            
            if 'task' in boards_to_create:
                print("\n📋 Creating Task Management Board...")
                task_project = setup_task_board(gh_projects, owner_id, repository_id)
                if task_project:
                    created_projects.append(task_project)
                    print("📝 Adding issues to task board...")
                    time.sleep(3)  # Wait for project setup to complete
                    try:
                        add_sample_items_to_project(gh_projects, task_project['id'], repository_id)
                    except Exception as e:
                        print(f"  ⚠️  Could not add issues to project: {e}")
                        print("  ℹ️  Project created successfully, issues can be added manually later")
            
            if 'test' in boards_to_create:
                print("\n🧪 Creating Test Management Board...")
                test_project = setup_test_board(gh_projects, owner_id, repository_id)
                if test_project:
                    created_projects.append(test_project)
            
            if 'sprint' in boards_to_create:
                print("\n🏃‍♂️ Creating Sprint Management Board...")
                sprint_project = setup_sprint_board(gh_projects, owner_id, repository_id)
                if sprint_project:
                    created_projects.append(sprint_project)
            
            print(f"\n✅ Successfully created {len(created_projects)} project board(s)!")
            
            print("\n📊 Created Projects:")
            for project in created_projects:
                print(f"  - {project['title']}: {project['url']}")
            
            print(f"\n🔗 Visit: https://github.com/{repo_name}/projects")
            return  # Success, exit
            
        except Exception as e:
            print(f"  ❌ Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt == args.retry_count - 1:
                print(f"\n❌ Projects setup failed after {args.retry_count} attempts")
                print("   Possible causes:")
                print("   - GitHub token lacks 'project' scope")
                print("   - Repository doesn't have Projects enabled")
                print("   - Rate limiting or API issues")
                print("   Try again later or check permissions")
                sys.exit(1)
            else:
                print(f"  🔄 Retrying in 5 seconds...")
                time.sleep(5)

if __name__ == "__main__":
    main()