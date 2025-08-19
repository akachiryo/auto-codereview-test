#!/usr/bin/env python3
"""
GitHub Projects v2 Setup Script - Completely rewritten based on official GitHub API

Creates comprehensive project boards with Issues integration:
1. Task Management Board - Main project board with Issues
2. Test Management Board - Test case tracking
3. Sprint Management Board - Agile development tracking

Uses the latest GitHub Projects v2 API with proper GraphQL queries.
"""

import os
import sys
import requests
import json
import time
import argparse
from dotenv import load_dotenv

load_dotenv()

class GitHubProjectsManager:
    def __init__(self, token, repo_name):
        self.token = token
        self.repo = repo_name
        self.owner, self.repo_name = repo_name.split('/')
        
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Team-Setup-Bot'
        }
        
        self.graphql_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Team-Setup-Bot'
        }

    def execute_graphql_query(self, query, variables=None):
        """Execute GraphQL query with proper error handling"""
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
            
        response = requests.post(
            'https://api.github.com/graphql',
            headers=self.graphql_headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"❌ GraphQL request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
        data = response.json()
        
        if 'errors' in data:
            print(f"❌ GraphQL errors: {data['errors']}")
            return None
            
        return data.get('data')

    def get_repository_info(self):
        """Get repository and owner information"""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
                name
                owner {
                    id
                    login
                    __typename
                }
            }
        }
        """
        
        variables = {"owner": self.owner, "name": self.repo_name}
        data = self.execute_graphql_query(query, variables)
        
        if data and 'repository' in data:
            return data['repository']
        else:
            print(f"❌ Could not get repository information for {self.repo}")
            return None

    def create_project_v2(self, title, owner_id):
        """Create a new GitHub Project v2"""
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
        
        data = self.execute_graphql_query(mutation, variables)
        
        if data and 'createProjectV2' in data:
            project = data['createProjectV2']['projectV2']
            print(f"  ✅ Created project: {project['title']} (#{project['number']})")
            return project
        else:
            print(f"❌ Failed to create project: {title}")
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
        
        data = self.execute_graphql_query(mutation, variables)
        
        if data and 'linkRepositoryToProject' in data:
            print(f"  ✅ Linked repository to project")
            return True
        else:
            print(f"  ⚠️  Could not link repository to project")
            return False

    def get_project_fields(self, project_id):
        """Get project field information"""
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
        data = self.execute_graphql_query(query, variables)
        
        if data and 'node' in data and data['node']:
            return data['node']['fields']['nodes']
        else:
            print(f"❌ Could not get project fields")
            return []

    def create_single_select_field(self, project_id, field_name, options):
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
            "name": field_name,
            "dataType": "SINGLE_SELECT",
            "options": options
        }
        
        data = self.execute_graphql_query(mutation, variables)
        
        if data and 'createProjectV2Field' in data:
            field = data['createProjectV2Field']['projectV2Field']
            print(f"    ✅ Created field: {field['name']}")
            return field
        else:
            print(f"    ⚠️  Could not create field: {field_name}")
            return None

    def get_repository_issues(self):
        """Get repository issues to add to project"""
        query = """
        query($owner: String!, $name: String!, $first: Int!) {
            repository(owner: $owner, name: $name) {
                issues(first: $first, states: [OPEN]) {
                    nodes {
                        id
                        number
                        title
                        state
                    }
                }
            }
        }
        """
        
        variables = {
            "owner": self.owner, 
            "name": self.repo_name,
            "first": 20
        }
        
        data = self.execute_graphql_query(query, variables)
        
        if data and 'repository' in data:
            issues = data['repository']['issues']['nodes']
            print(f"  📋 Found {len(issues)} open issues")
            return issues
        else:
            print(f"  ℹ️  No issues found or could not fetch issues")
            return []

    def add_issue_to_project(self, project_id, issue_id):
        """Add an issue to a project using the correct API"""
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {
                projectId: $projectId,
                contentId: $contentId
            }) {
                item {
                    id
                    content {
                        ... on Issue {
                            number
                            title
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "projectId": project_id,
            "contentId": issue_id
        }
        
        data = self.execute_graphql_query(mutation, variables)
        
        if data and 'addProjectV2ItemById' in data:
            item = data['addProjectV2ItemById']['item']
            issue_info = item['content']
            print(f"    ✅ Added issue #{issue_info['number']}: {issue_info['title']}")
            return item
        else:
            print(f"    ⚠️  Could not add issue to project")
            return None

    def setup_task_management_board(self, owner_id, repository_id):
        """Create main task management board"""
        print("📋 Creating Task Management Board...")
        
        # Create project
        project = self.create_project_v2("🎯 タスク管理ボード", owner_id)
        if not project:
            return None
        
        project_id = project['id']
        
        # Link repository
        self.link_repository_to_project(project_id, repository_id)
        
        # Wait for project to be ready
        time.sleep(3)
        
        # Create Status field
        print("  🔧 Creating Status field...")
        status_options = [
            {"name": "📝 To Do", "color": "GRAY"},
            {"name": "🔄 In Progress", "color": "YELLOW"},
            {"name": "👀 In Review", "color": "BLUE"},
            {"name": "✅ Done", "color": "GREEN"}
        ]
        self.create_single_select_field(project_id, "Status", status_options)
        
        # Wait between field creations
        time.sleep(2)
        
        # Create Priority field
        print("  🔧 Creating Priority field...")
        priority_options = [
            {"name": "🔥 High", "color": "RED"},
            {"name": "🟡 Medium", "color": "YELLOW"},
            {"name": "🟢 Low", "color": "GREEN"}
        ]
        self.create_single_select_field(project_id, "Priority", priority_options)
        
        # Wait between field creations
        time.sleep(2)
        
        # Create Effort field
        print("  🔧 Creating Effort field...")
        effort_options = [
            {"name": "S (1-2h)", "color": "GREEN"},
            {"name": "M (3-8h)", "color": "YELLOW"},
            {"name": "L (1-2d)", "color": "ORANGE"},
            {"name": "XL (3-5d)", "color": "RED"}
        ]
        self.create_single_select_field(project_id, "Effort", effort_options)
        
        # Wait for fields to be created
        time.sleep(3)
        
        # Add existing issues to the project
        print("  📋 Adding issues to project...")
        issues = self.get_repository_issues()
        
        added_count = 0
        for issue in issues[:10]:  # Limit to first 10 issues
            if self.add_issue_to_project(project_id, issue['id']):
                added_count += 1
                time.sleep(1)  # Rate limiting
        
        if added_count > 0:
            print(f"  ✅ Added {added_count} issues to the task board")
        else:
            print(f"  ℹ️  No issues were added (this is normal for new repositories)")
        
        return project

    def setup_test_management_board(self, owner_id, repository_id):
        """Create test management board"""
        print("🧪 Creating Test Management Board...")
        
        # Create project
        project = self.create_project_v2("🧪 テスト管理ボード", owner_id)
        if not project:
            return None
        
        project_id = project['id']
        
        # Link repository
        self.link_repository_to_project(project_id, repository_id)
        
        # Wait for project to be ready
        time.sleep(3)
        
        # Create Test Status field
        print("  🔧 Creating Test Status field...")
        test_status_options = [
            {"name": "📝 Not Started", "color": "GRAY"},
            {"name": "🧪 Testing", "color": "YELLOW"},
            {"name": "✅ Passed", "color": "GREEN"},
            {"name": "❌ Failed", "color": "RED"},
            {"name": "⚠️ Blocked", "color": "ORANGE"}
        ]
        self.create_single_select_field(project_id, "Test Status", test_status_options)
        
        # Wait between field creations
        time.sleep(2)
        
        # Create Test Type field
        print("  🔧 Creating Test Type field...")
        test_type_options = [
            {"name": "Unit Test", "color": "BLUE"},
            {"name": "Integration Test", "color": "PURPLE"},
            {"name": "E2E Test", "color": "PINK"},
            {"name": "Manual Test", "color": "GRAY"}
        ]
        self.create_single_select_field(project_id, "Test Type", test_type_options)
        
        # Wait between field creations
        time.sleep(2)
        
        # Create Environment field
        print("  🔧 Creating Environment field...")
        env_options = [
            {"name": "Development", "color": "YELLOW"},
            {"name": "Staging", "color": "BLUE"},
            {"name": "Production", "color": "GREEN"}
        ]
        self.create_single_select_field(project_id, "Environment", env_options)
        
        return project

    def setup_sprint_management_board(self, owner_id, repository_id):
        """Create sprint management board"""
        print("🏃‍♂️ Creating Sprint Management Board...")
        
        # Create project
        project = self.create_project_v2("🏃‍♂️ スプリント管理", owner_id)
        if not project:
            return None
        
        project_id = project['id']
        
        # Link repository
        self.link_repository_to_project(project_id, repository_id)
        
        # Wait for project to be ready
        time.sleep(3)
        
        # Create Sprint field
        print("  🔧 Creating Sprint field...")
        sprint_options = [
            {"name": "Sprint 1", "color": "BLUE"},
            {"name": "Sprint 2", "color": "GREEN"},
            {"name": "Sprint 3", "color": "YELLOW"},
            {"name": "Backlog", "color": "GRAY"}
        ]
        self.create_single_select_field(project_id, "Sprint", sprint_options)
        
        # Wait between field creations
        time.sleep(2)
        
        # Create Story Points field
        print("  🔧 Creating Story Points field...")
        story_point_options = [
            {"name": "1", "color": "GREEN"},
            {"name": "2", "color": "GREEN"},
            {"name": "3", "color": "YELLOW"},
            {"name": "5", "color": "YELLOW"},
            {"name": "8", "color": "ORANGE"},
            {"name": "13", "color": "RED"}
        ]
        self.create_single_select_field(project_id, "Story Points", story_point_options)
        
        return project

def main():
    parser = argparse.ArgumentParser(description='Setup GitHub Projects v2 boards')
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
        boards_to_create = ['task', 'test', 'sprint']
    
    print(f"🚀 Setting up GitHub Projects v2 for {repo_name}...")
    
    for attempt in range(args.retry_count):
        try:
            print(f"📊 Attempt {attempt + 1}/{args.retry_count}: Creating projects...")
            
            if attempt > 0:
                time.sleep(5)  # Wait between attempts
            
            projects_manager = GitHubProjectsManager(token, repo_name)
            
            # Get repository information
            repo_info = projects_manager.get_repository_info()
            if not repo_info:
                raise Exception("Failed to get repository information")
            
            owner_id = repo_info['owner']['id']
            repository_id = repo_info['id']
            
            print(f"  📁 Repository: {repo_info['name']}")
            print(f"  👤 Owner: {repo_info['owner']['login']} ({repo_info['owner']['__typename']})")
            
            created_projects = []
            
            # Create Task Management Board
            if 'task' in boards_to_create:
                task_project = projects_manager.setup_task_management_board(owner_id, repository_id)
                if task_project:
                    created_projects.append(task_project)
            
            # Create Test Management Board
            if 'test' in boards_to_create:
                test_project = projects_manager.setup_test_management_board(owner_id, repository_id)
                if test_project:
                    created_projects.append(test_project)
            
            # Create Sprint Management Board
            if 'sprint' in boards_to_create:
                sprint_project = projects_manager.setup_sprint_management_board(owner_id, repository_id)
                if sprint_project:
                    created_projects.append(sprint_project)
            
            print(f"\n✅ Successfully created {len(created_projects)} project board(s)!")
            
            if created_projects:
                print(f"\n📊 Created Projects:")
                for project in created_projects:
                    print(f"  - {project['title']}: {project['url']}")
                
                print(f"\n🔗 All Projects: https://github.com/{repo_name}/projects")
            
            return  # Success, exit
            
        except Exception as e:
            print(f"  ❌ Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt == args.retry_count - 1:
                print(f"\n❌ Projects setup failed after {args.retry_count} attempts")
                print(f"\n🔍 Possible causes:")
                print(f"   - GitHub token lacks 'project' scope")
                print(f"   - Repository doesn't have Projects enabled")
                print(f"   - Rate limiting or API issues")
                print(f"   - GraphQL API changes")
                print(f"\n💡 Solutions:")
                print(f"   - Check token permissions: https://github.com/settings/tokens")
                print(f"   - Enable Projects in repository settings")
                print(f"   - Wait a few minutes and try again")
                print(f"   - Check repository: https://github.com/{repo_name}/settings")
                sys.exit(1)
            else:
                print(f"  🔄 Retrying in 10 seconds...")
                time.sleep(10)

if __name__ == "__main__":
    main()