#!/bin/bash
# Deploys analytics preview build to GitHub Pages

set -e

BRANCH="analytics-v1"
TARGET_DIR="dist-preview"
REPO_URL="https://github.com/Clawdributors/nsw-hunter-central-coast.git"

# Build the preview
npm run build -- --base=/nsw-hunter-central-coast-dev/ --outDir=$TARGET_DIR

# Configure Git
git config --global user.name "Clawdbot"

# Deploy to GH Pages
cd $TARGET_DIR

git init
git checkout -b $BRANCH
git add -A
git commit -m "Deploy analytics preview"
git push -f $REPO_URL $BRANCH:gh-pages

cd -
echo "Preview deployed to:"
echo "https://clawdributors.github.io/nsw-hunter-central-coast-dev/"

# Switch back to analytics branch
git checkout $BRANCH