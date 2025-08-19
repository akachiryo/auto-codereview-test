#!/usr/bin/env python3
"""
GitHub Projects v2 Setup Script - Fixed and tested for repository-level projects

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

    def create_project_v2(self, title, owner_id, repository_id=None):
        """Create a new GitHub Project v2 linked to repository"""
        if repository_id:
            # Create project linked to repository
            mutation = """
            mutation($ownerId: ID!, $title: String!, $repositoryId: ID!) {
                createProjectV2(input: {
                    ownerId: $ownerId,
                    title: $title,
                    repositoryId: $repositoryId
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
                "title": title,
                "repositoryId": repository_id
            }
        else:
            # Create standalone project
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

    # Note: linkRepositoryToProject mutation does not support Projects v2
    # Instead, we specify repositoryId during project creation

    def link_project_v2_to_repository(self, project_id, repository_id):
        """Alternative method to link project to repository (if needed)"""
        mutation = """
        mutation($projectId: ID!, $repositoryId: ID!) {
            linkProjectV2ToRepository(input: {
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
        
        if data and 'linkProjectV2ToRepository' in data:
            print(f"  ✅ Linked project to repository (alternative method)")
            return True
        else:
            print(f"  ⚠️  Could not link project to repository (alternative method)")
            return False

    # Note: createProjectV2View mutation does not exist in GitHub GraphQL API
    # Projects v2 uses default views, and board layout depends on field configuration

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
        
        # Create project linked to repository
        project = self.create_project_v2("🎯 タスク管理ボード", owner_id, repository_id)
        if not project:
            return None
        
        project_id = project['id']
        
        # Wait for project to be fully created
        print("  ⏳ Waiting for project to be ready...")
        time.sleep(3)
        
        # Create Status field
        print("  🔧 Creating Status field...")
        status_options = [
            {"name": "📝 To Do", "color": "GRAY", "description": "Tasks not yet started"},
            {"name": "🔄 In Progress", "color": "YELLOW", "description": "Tasks currently being worked on"},
            {"name": "👀 In Review", "color": "BLUE", "description": "Tasks under review"},
            {"name": "✅ Done", "color": "GREEN", "description": "Completed tasks"}
        ]
        status_field = self.create_single_select_field(project_id, "Status", status_options)
        
        # Wait between field creations for API rate limiting
        time.sleep(3)
        
        # Create Priority field
        print("  🔧 Creating Priority field...")
        priority_options = [
            {"name": "🔥 High", "color": "RED", "description": "High priority tasks requiring immediate attention"},
            {"name": "🟡 Medium", "color": "YELLOW", "description": "Medium priority tasks"},
            {"name": "🟢 Low", "color": "GREEN", "description": "Low priority tasks"}
        ]
        self.create_single_select_field(project_id, "Priority", priority_options)
        
        # Wait between field creations for API rate limiting
        time.sleep(3)
        
        # Create Effort field
        print("  🔧 Creating Effort field...")
        effort_options = [
            {"name": "S (1-2h)", "color": "GREEN", "description": "Small tasks taking 1-2 hours"},
            {"name": "M (3-8h)", "color": "YELLOW", "description": "Medium tasks taking 3-8 hours"},
            {"name": "L (1-2d)", "color": "ORANGE", "description": "Large tasks taking 1-2 days"},
            {"name": "XL (3-5d)", "color": "RED", "description": "Extra large tasks taking 3-5 days"}
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
        
        # Note: Projects v2 automatically provides board and table views
        print("  ✅ Project configured - Board view available by default")
        
        return project

    def setup_test_management_board(self, owner_id, repository_id):
        """Create test management board"""
        print("🧪 Creating Test Management Board...")
        
        # Create project linked to repository
        project = self.create_project_v2("🧪 テスト管理ボード", owner_id, repository_id)
        if not project:
            return None
        
        project_id = project['id']
        
        # Wait for project to be fully created
        print("  ⏳ Waiting for project to be ready...")
        time.sleep(3)
        
        # Create Test Status field
        print("  🔧 Creating Test Status field...")
        test_status_options = [
            {"name": "📝 Not Started", "color": "GRAY", "description": "Tests not yet started"},
            {"name": "🧪 Testing", "color": "YELLOW", "description": "Tests currently running"},
            {"name": "✅ Passed", "color": "GREEN", "description": "Tests passed successfully"},
            {"name": "❌ Failed", "color": "RED", "description": "Tests failed"},
            {"name": "⚠️ Blocked", "color": "ORANGE", "description": "Tests blocked by dependencies"}
        ]
        test_status_field = self.create_single_select_field(project_id, "Test Status", test_status_options)
        
        # Wait between field creations for API rate limiting
        time.sleep(3)
        
        # Create Test Type field
        print("  🔧 Creating Test Type field...")
        test_type_options = [
            {"name": "Unit Test", "color": "BLUE", "description": "Individual component testing"},
            {"name": "Integration Test", "color": "PURPLE", "description": "Multiple component integration testing"},
            {"name": "E2E Test", "color": "PINK", "description": "End-to-end user workflow testing"},
            {"name": "Manual Test", "color": "GRAY", "description": "Manual testing procedures"}
        ]
        self.create_single_select_field(project_id, "Test Type", test_type_options)
        
        # Wait between field creations for API rate limiting
        time.sleep(3)
        
        # Create Environment field
        print("  🔧 Creating Environment field...")
        env_options = [
            {"name": "Development", "color": "YELLOW", "description": "Development environment"},
            {"name": "Staging", "color": "BLUE", "description": "Staging environment for testing"},
            {"name": "Production", "color": "GREEN", "description": "Live production environment"}
        ]
        self.create_single_select_field(project_id, "Environment", env_options)
        
        # Note: Projects v2 automatically provides board and table views
        print("  ✅ Test project configured - Board view available by default")
        
        return project

    def setup_sprint_management_board(self, owner_id, repository_id):
        """Create sprint management board"""
        print("🏃‍♂️ Creating Sprint Management Board...")
        
        # Create project linked to repository
        project = self.create_project_v2("🏃‍♂️ スプリント管理", owner_id, repository_id)
        if not project:
            return None
        
        project_id = project['id']
        
        # Wait for project to be fully created
        print("  ⏳ Waiting for project to be ready...")
        time.sleep(3)
        
        # Create Sprint field
        print("  🔧 Creating Sprint field...")
        sprint_options = [
            {"name": "Sprint 1", "color": "BLUE", "description": "First sprint iteration"},
            {"name": "Sprint 2", "color": "GREEN", "description": "Second sprint iteration"},
            {"name": "Sprint 3", "color": "YELLOW", "description": "Third sprint iteration"},
            {"name": "Backlog", "color": "GRAY", "description": "Items not yet assigned to a sprint"}
        ]
        sprint_field = self.create_single_select_field(project_id, "Sprint", sprint_options)
        
        # Wait between field creations for API rate limiting
        time.sleep(3)
        
        # Create Story Points field
        print("  🔧 Creating Story Points field...")
        story_point_options = [
            {"name": "1", "color": "GREEN", "description": "Very small task - 1 point"},
            {"name": "2", "color": "GREEN", "description": "Small task - 2 points"},
            {"name": "3", "color": "YELLOW", "description": "Medium task - 3 points"},
            {"name": "5", "color": "YELLOW", "description": "Large task - 5 points"},
            {"name": "8", "color": "ORANGE", "description": "Very large task - 8 points"},
            {"name": "13", "color": "RED", "description": "Epic task - 13 points"}
        ]
        self.create_single_select_field(project_id, "Story Points", story_point_options)
        
        # Note: Projects v2 automatically provides board and table views
        print("  ✅ Sprint project configured - Board view available by default")
        
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
    print(f"  🔑 Token available: {'Yes' if token else 'No'}")
    print(f"  📊 Boards to create: {boards_to_create}")
    print(f"  📁 Working directory: {os.getcwd()}")
    
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