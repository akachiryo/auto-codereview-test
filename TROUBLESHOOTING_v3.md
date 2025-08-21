# 🔧 Troubleshooting Guide v3.0 (CONSOLIDATED)

## 🚨 Known Issue: Old Code Still Running

If you're still seeing these error messages despite our v3.0 updates:
- `⚠️ Limiting to first 50 test issues to avoid rate limits`
- `⚠️ Limiting to first 30 issues for project addition`
- Python indentation errors in Wiki setup

**This means old cached workflow code is still executing instead of our new v3.0 version.**

## 🔍 Diagnostic Steps

### Step 1: Verify Workflow Version
1. Go to your repository's Actions tab
2. Check the workflow name - it should show: `🚀 Team Development Setup v3.0 (CONSOLIDATED)`
3. If it shows the old name without "v3.0", you're running old code

### Step 2: Check Workflow File
1. Verify `.github/workflows/team-setup.yml` exists
2. Check that old workflow files are deleted:
   - `team-setup-main.yml`
   - `team-setup-issues-1.yml` through `team-setup-issues-4.yml`
   - `team-setup-complete.yml`

### Step 3: Look for Version Markers
When the v3.0 workflow runs, you should see:
```
🔍 TEAM SETUP WORKFLOW v3.0 (CONSOLIDATED) STARTING
📊 GITHUB PROJECTS CREATION v3.0 (CONSOLIDATED)
💬 DISCUSSIONS SETUP v3.0 (CONSOLIDATED)
📚 WIKI SETUP v3.0 (CONSOLIDATED)
🎯 BATCH ISSUE CREATION SYSTEM v3.0 (CONSOLIDATED)
📊 CRITICAL: This is v3.0 with NO hardcoded limits
```

## 🛠️ Solution Steps

### Option 1: Force Refresh (Recommended)
```bash
# Run the cleanup script
python scripts/cleanup_force_refresh.py

# Verify environment
python scripts/verify_environment.py

# Then run the workflow manually
```

### Option 2: Manual Verification
1. Check current branch: `git branch`
2. Ensure you're on the correct branch with updated files
3. Check commit history: `git log --oneline -5`
4. Verify file contents: `cat .github/workflows/team-setup.yml | head -20`

### Option 3: Branch Issues
If you're on a different branch:
```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Verify team-setup.yml exists and has v3.0 markers
grep -n "v3.0" .github/workflows/team-setup.yml
```

## 🎯 Expected v3.0 Behavior

### Issues Creation
- **OLD**: "Limiting to first 50 test issues"
- **NEW v3.0**: "NO LIMITS - Will process all items in batch range"
- **NEW v3.0**: "CRITICAL: No 50-issue or 30-issue limits in this version"

### Project Linking
- **OLD**: "Limiting to first 30 issues for project addition"
- **NEW v3.0**: All issues from CSV should be linked to projects

### Wiki Setup
- **OLD**: Python indentation errors with multiline strings
- **NEW v3.0**: All Python moved to separate script files (no inline multiline Python)

## 📊 Data Verification

Run the verification script to check your data:
```bash
python scripts/verify_environment.py
```

This will show:
- Total issues in CSV files
- Expected batch processing
- Estimated processing time

## 🔍 Log Analysis

### Version Confirmation
Look for these markers in GitHub Actions logs:
- Workflow title: "Team Development Setup v3.0 (CONSOLIDATED)"
- Script versions: "create_projects.py v3.0", "create_issues_batch.py v3.0"
- No limit confirmations: "NO hardcoded limits in this version"

### Error Patterns
If you still see old errors, the old code is running:
- Check workflow file names in Actions history
- Verify no old workflows are cached
- Confirm you're running from the correct repository/branch

## 🚀 Quick Fix Commands

```bash
# 1. Clean everything
python scripts/cleanup_force_refresh.py

# 2. Verify setup
python scripts/verify_environment.py

# 3. Check workflow file
cat .github/workflows/team-setup.yml | grep -A 5 -B 5 "v3.0"

# 4. List all workflow files
ls -la .github/workflows/

# 5. Check git status
git status
git log --oneline -3
```

## 🎛️ Environment Variables

Ensure these are set in GitHub repository secrets:
- `TEAM_SETUP_TOKEN`: Your GitHub Personal Access Token
  - Scopes needed: `repo`, `project`

## 📈 Success Indicators

When v3.0 is working correctly:
1. ✅ Workflow name shows "v3.0 (CONSOLIDATED)"
2. ✅ All script outputs show "v3.0" version
3. ✅ No "50 issue limit" warnings
4. ✅ No "30 issue limit" warnings
5. ✅ Wiki setup completes without Python errors
6. ✅ All CSV issues are created and linked to projects

## 🆘 Still Having Issues?

If problems persist after following this guide:

1. **Double-check branch**: Ensure you're on the branch with v3.0 code
2. **Clear Actions cache**: GitHub may cache old workflows
3. **Manual verification**: Run scripts locally to verify they work
4. **Repository settings**: Check if repository has required permissions

### Local Testing
Test the scripts locally:
```bash
# Set environment variables
export GITHUB_REPOSITORY="your-username/your-repo"
export TEAM_SETUP_TOKEN="your-token"

# Test environment verification
python scripts/verify_environment.py

# Test project creation (be careful - this creates real projects)
# python scripts/create_projects.py
```

## 📝 Version History

- **v1.0**: Initial multi-workflow system with rate limiting issues
- **v2.0**: Batch processing system, but still had hardcoded limits
- **v3.0**: Single consolidated workflow, no hardcoded limits, enhanced diagnostics

---

**Key Point**: If you see old error messages, you're not running v3.0 code. Follow the diagnostic steps above to identify why the old code is still executing.