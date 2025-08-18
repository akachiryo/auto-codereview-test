#!/bin/bash

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SETUP_ALL=true
SETUP_ISSUES=false
SETUP_WIKI=false
SETUP_DISCUSSIONS=false
SETUP_PROJECTS=false
CSV_FILE="data/sample-tasks.csv"
DRY_RUN=false

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

print_header() {
    echo -e "${BLUE}"
    echo "======================================"
    echo "  GitHub Team Development Setup"
    echo "======================================"
    echo -e "${NC}"
    echo "🚀 Automating GitHub project setup..."
    echo ""
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -r, --repo REPO         Repository name (owner/repo)"
    echo "  -t, --token TOKEN       GitHub token"
    echo "  -c, --csv CSV_FILE      CSV file path (default: data/sample-tasks.csv)"
    echo "  --issues-only           Setup issues only"
    echo "  --wiki-only             Setup wiki only" 
    echo "  --discussions-only      Setup discussions only"
    echo "  --projects-only         Setup projects only"
    echo "  --dry-run               Show what would be done without making changes"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  GITHUB_TOKEN           GitHub personal access token"
    echo "  GITHUB_REPO            Repository name (owner/repo)"
    echo ""
    echo "Examples:"
    echo "  $0 --repo user/my-repo --token ghp_xxxx"
    echo "  $0 --issues-only --csv my-tasks.csv"
    echo "  $0 --dry-run"
}

check_dependencies() {
    echo -e "${YELLOW}📦 Checking dependencies...${NC}"
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        echo -e "${RED}❌ pip is required but not installed${NC}"
        exit 1
    fi
    
    # Install Python dependencies
    echo "  📋 Installing Python dependencies..."
    if command -v pip3 &> /dev/null; then
        pip3 install -r "$ROOT_DIR/requirements.txt" -q
    else
        pip install -r "$ROOT_DIR/requirements.txt" -q
    fi
    
    echo -e "${GREEN}  ✅ Dependencies installed${NC}"
}

check_environment() {
    echo -e "${YELLOW}🔧 Checking environment...${NC}"
    
    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${RED}❌ GITHUB_TOKEN environment variable is required${NC}"
        echo "   Get a token from: https://github.com/settings/tokens"
        echo "   Required scopes: repo, write:discussion, project"
        exit 1
    fi
    
    if [ -z "$GITHUB_REPO" ]; then
        echo -e "${RED}❌ GITHUB_REPO environment variable is required${NC}"
        echo "   Format: owner/repository-name"
        exit 1
    fi
    
    echo -e "${GREEN}  ✅ Environment configured${NC}"
    echo "     Repository: $GITHUB_REPO"
    echo "     Token: ${GITHUB_TOKEN:0:10}..."
}

setup_issues() {
    echo -e "${BLUE}🎯 Setting up Issues...${NC}"
    
    python3 "$SCRIPT_DIR/csv-to-issues.py" \
        --csv "$CSV_FILE" \
        --repo "$GITHUB_REPO" \
        --token "$GITHUB_TOKEN" \
        $([ "$DRY_RUN" = true ] && echo "--dry-run")
    
    echo -e "${GREEN}✅ Issues setup completed${NC}"
}

setup_wiki() {
    echo -e "${BLUE}📚 Setting up Wiki...${NC}"
    
    python3 "$SCRIPT_DIR/create-wiki.py" \
        --repo "$GITHUB_REPO" \
        --token "$GITHUB_TOKEN" \
        --retry-count 3
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Wiki setup completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Wiki setup had issues, but continuing...${NC}"
    fi
}

setup_discussions() {
    echo -e "${BLUE}💬 Setting up Discussions...${NC}"
    
    python3 "$SCRIPT_DIR/create-discussions.py" \
        --repo "$GITHUB_REPO" \
        --token "$GITHUB_TOKEN"
    
    echo -e "${GREEN}✅ Discussions setup completed${NC}"
}

setup_projects() {
    echo -e "${BLUE}📊 Setting up Projects...${NC}"
    
    python3 "$SCRIPT_DIR/setup-projects.py" \
        --repo "$GITHUB_REPO" \
        --token "$GITHUB_TOKEN" \
        --boards all \
        --retry-count 3
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Projects setup completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Projects setup had issues, but continuing...${NC}"
    fi
}

create_env_file() {
    if [ ! -f "$ROOT_DIR/.env" ]; then
        echo -e "${YELLOW}📝 Creating .env file...${NC}"
        cat > "$ROOT_DIR/.env" << EOF
# GitHub Configuration
GITHUB_TOKEN=$GITHUB_TOKEN
GITHUB_REPO=$GITHUB_REPO

# Optional: GitHub API Base URL (for GitHub Enterprise)
# GITHUB_API_URL=https://api.github.com

# CSV Configuration  
CSV_FILE=$CSV_FILE
EOF
        echo -e "${GREEN}  ✅ Created .env file${NC}"
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "  1. Check your repository: https://github.com/$GITHUB_REPO"
    echo "  2. Review created Issues: https://github.com/$GITHUB_REPO/issues"
    echo "  3. Browse Wiki pages: https://github.com/$GITHUB_REPO/wiki"
    echo "  4. Join Discussions: https://github.com/$GITHUB_REPO/discussions"
    echo "  5. Manage Projects: https://github.com/$GITHUB_REPO/projects"
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "  • Edit the templates in setup-tools/templates/ before running"
    echo "  • Modify CSV data in setup-tools/data/sample-tasks.csv"
    echo "  • Customize project boards after creation"
    echo "  • Add team members as collaborators"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--repo)
            GITHUB_REPO="$2"
            shift 2
            ;;
        -t|--token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        -c|--csv)
            CSV_FILE="$2"
            shift 2
            ;;
        --issues-only)
            SETUP_ALL=false
            SETUP_ISSUES=true
            shift
            ;;
        --wiki-only)
            SETUP_ALL=false
            SETUP_WIKI=true
            shift
            ;;
        --discussions-only)
            SETUP_ALL=false
            SETUP_DISCUSSIONS=true
            shift
            ;;
        --projects-only)
            SETUP_ALL=false
            SETUP_PROJECTS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header
    
    # Export environment variables for Python scripts
    export GITHUB_TOKEN
    export GITHUB_REPO
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
        echo ""
    fi
    
    check_dependencies
    check_environment
    create_env_file
    
    echo ""
    echo -e "${BLUE}🚀 Starting setup process...${NC}"
    echo ""
    
    if [ "$SETUP_ALL" = true ]; then
        setup_issues
        echo ""
        setup_wiki
        echo ""
        setup_discussions
        echo ""
        setup_projects
    else
        [ "$SETUP_ISSUES" = true ] && setup_issues && echo ""
        [ "$SETUP_WIKI" = true ] && setup_wiki && echo ""
        [ "$SETUP_DISCUSSIONS" = true ] && setup_discussions && echo ""
        [ "$SETUP_PROJECTS" = true ] && setup_projects && echo ""
    fi
    
    if [ "$DRY_RUN" != true ]; then
        print_summary
    fi
}

# Run main function
main