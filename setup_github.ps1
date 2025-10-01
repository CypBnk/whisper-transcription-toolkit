# GitHub Repository Setup Script for CypBnk/whisper-transcription-toolkit
# PowerShell version for Windows

Write-Host "🚀 Whisper Transcription Toolkit - GitHub Setup" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "README.md") -or -not (Test-Path "transcript_batch.py")) {
    Write-Host "❌ Error: Please run this script from the whisper-transcription-toolkit directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Repository structure verified" -ForegroundColor Green
Write-Host ""

# Show current git status
Write-Host "📋 Current Git Status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Show remote configuration
Write-Host "🔗 Remote Configuration:" -ForegroundColor Yellow
git remote -v
Write-Host ""

# Stage any changes
Write-Host "📦 Staging changes..." -ForegroundColor Yellow
git add .

# Check if there are changes to commit
$hasChanges = git diff --staged --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "📝 Committing changes..." -ForegroundColor Yellow
    git commit -m "docs: Update changelog date to 2025-10-01

- Correct release date in CHANGELOG.md
- Repository ready for publication"
} else {
    Write-Host "✅ No changes to commit - repository is up to date" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 Repository Status: READY FOR PUBLICATION" -ForegroundColor Green -BackgroundColor Black
Write-Host ""
Write-Host "🔐 To publish to GitHub, you have several options:" -ForegroundColor Cyan
Write-Host ""

Write-Host "Option 1 - Using GitHub CLI (gh):" -ForegroundColor White
Write-Host "  gh auth login" -ForegroundColor Gray
Write-Host "  git push origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 2 - Using Personal Access Token:" -ForegroundColor White
Write-Host "  1. Go to https://github.com/settings/tokens" -ForegroundColor Gray
Write-Host "  2. Create a new token with repo permissions" -ForegroundColor Gray
Write-Host "  3. Use: git push https://[token]@github.com/CypBnk/whisper-transcription-toolkit.git main" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 3 - Using VS Code Git integration:" -ForegroundColor White
Write-Host "  1. Open VS Code's Source Control panel (Ctrl+Shift+G)" -ForegroundColor Gray
Write-Host "  2. Click 'Push' and authenticate when prompted" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 4 - SSH (if configured):" -ForegroundColor White
Write-Host "  git remote set-url origin git@github.com:CypBnk/whisper-transcription-toolkit.git" -ForegroundColor Gray
Write-Host "  git push origin main" -ForegroundColor Gray
Write-Host ""

# Repository statistics
$totalFiles = (Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch "\.git" }).Count
$pythonFiles = (Get-ChildItem -Recurse -Filter "*.py").Count
$docFiles = (Get-ChildItem -Recurse -Filter "*.md").Count

Write-Host "📊 Repository Statistics:" -ForegroundColor Yellow
Write-Host "  Files: $totalFiles" -ForegroundColor Gray
Write-Host "  Python scripts: $pythonFiles" -ForegroundColor Gray
Write-Host "  Documentation: $docFiles" -ForegroundColor Gray
Write-Host ""

Write-Host "🌟 Features included:" -ForegroundColor Yellow
Write-Host "  ✅ AI-assisted development attribution" -ForegroundColor Green
Write-Host "  ✅ Complete documentation" -ForegroundColor Green
Write-Host "  ✅ Privacy-safe sanitized code" -ForegroundColor Green
Write-Host "  ✅ Professional contribution guidelines" -ForegroundColor Green
Write-Host "  ✅ MIT License for open source" -ForegroundColor Green
Write-Host "  ✅ Cross-platform compatibility" -ForegroundColor Green
Write-Host ""

Write-Host "Repository: https://github.com/CypBnk/whisper-transcription-toolkit" -ForegroundColor Cyan
Write-Host "Ready for: ⭐ Stars, 🍴 Forks, 🐛 Issues, 🔄 Pull Requests" -ForegroundColor Magenta