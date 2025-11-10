#!/bin/bash
set -e
cd /Users/mohanganesh/AUVRA

# Initialize git if needed
if [ ! -d .git ]; then
  git init
  echo "Initialized new git repository"
else
  echo "git already initialized"
fi

# Ensure local user.name and user.email are set (only if missing)
if [ -z "$(git config user.name)" ]; then
  git config user.name "Mohan Ganesh"
  echo "Set git user.name to 'Mohan Ganesh'"
fi
if [ -z "$(git config user.email)" ]; then
  git config user.email "mohanganesh@example.com"
  echo "Set git user.email to 'mohanganesh@example.com'"
fi

# Write .gitignore (overwrite)
cat > .gitignore <<'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.env
.env.*
.venv/
pip-log.txt
pip-delete-this-directory.txt

# macOS
.DS_Store

# Node
node_modules/
npm-debug.log
yarn-error.log

# Expo / React Native
.expo/
.expo-shared/

# Build outputs
dist/
build/

# IDEs
.vscode/
.idea/

# PDF and generated docs
*.pdf
*.html

# Local env
.local.env

EOF

echo "Wrote .gitignore"

# Stage changes
git add .

echo "Staged files"

# Commit if there are staged changes
if git diff --cached --quiet; then
  echo "No changes to commit"
else
  git commit -m "chore: initial commit"
  echo "Committed changes"
fi

# Configure remote
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/mohanganesh3/AUVRA.git

echo "Added remote origin https://github.com/mohanganesh3/AUVRA.git"

# Set branch name to main
git branch -M main || true

echo "Set branch to main"

# Push to remote
set +e
git push -u origin main
PUSH_EXIT=$?
set -e

if [ $PUSH_EXIT -eq 0 ]; then
  echo "Pushed to origin/main successfully"
else
  echo "git push exited with code $PUSH_EXIT. Authentication may be required or remote may not exist."
  exit $PUSH_EXIT
fi
