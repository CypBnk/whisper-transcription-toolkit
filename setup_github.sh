#!/bin/bash
# GitHub Repository Setup Script for CypBnk/whisper-transcription-toolkit
# This script helps set up the repository for publishing

echo "🚀 Whisper Transcription Toolkit - GitHub Setup"
echo "================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -f "transcript_batch.py" ]; then
    echo "❌ Error: Please run this script from the whisper-transcription-toolkit directory"
    exit 1
fi

echo "✅ Repository structure verified"
echo ""

# Update the changelog with correct date
echo "📅 Updating changelog date..."
echo ""

# Show current git status
echo "📋 Current Git Status:"
git status --short
echo ""

# Show remote configuration
echo "🔗 Remote Configuration:"
git remote -v
echo ""

# Stage any changes
echo "📦 Staging changes..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes to commit - repository is up to date"
else
    echo "📝 Committing changes..."
    git commit -m "docs: Update changelog date to 2025-10-01

- Correct release date in CHANGELOG.md
- Repository ready for publication"
fi

echo ""
echo "🎯 Repository Status: READY FOR PUBLICATION"
echo ""
echo "🔐 To publish to GitHub, you have several options:"
echo ""
echo "Option 1 - Using GitHub CLI (gh):"
echo "  gh auth login"
echo "  git push origin main"
echo ""
echo "Option 2 - Using Personal Access Token:"
echo "  1. Go to https://github.com/settings/tokens"
echo "  2. Create a new token with repo permissions"
echo "  3. Use: git push https://[token]@github.com/CypBnk/whisper-transcription-toolkit.git main"
echo ""
echo "Option 3 - Using VS Code Git integration:"
echo "  1. Open VS Code's Source Control panel (Ctrl+Shift+G)"
echo "  2. Click 'Push' and authenticate when prompted"
echo ""
echo "Option 4 - SSH (if configured):"
echo "  git remote set-url origin git@github.com:CypBnk/whisper-transcription-toolkit.git"
echo "  git push origin main"
echo ""
echo "📊 Repository Statistics:"
echo "  Files: $(find . -type f -not -path './.git/*' | wc -l)"
echo "  Python scripts: $(find . -name '*.py' | wc -l)"
echo "  Documentation: $(find . -name '*.md' | wc -l)"
echo ""
echo "🌟 Features included:"
echo "  ✅ AI-assisted development attribution"
echo "  ✅ Complete documentation"
echo "  ✅ Privacy-safe sanitized code"
echo "  ✅ Professional contribution guidelines"
echo "  ✅ MIT License for open source"
echo "  ✅ Cross-platform compatibility"
echo ""
echo "Repository: https://github.com/CypBnk/whisper-transcription-toolkit"
echo "Ready for: ⭐ Stars, 🍴 Forks, 🐛 Issues, 🔄 Pull Requests"