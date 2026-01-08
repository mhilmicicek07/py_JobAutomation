@echo off
echo ========================================
echo Git Commit Script - Version 2.0.0
echo ========================================
echo.

cd /d "G:\Drive'ım\GITHUB REPOS\py_JobAutomation"

echo [1/5] Creating migration for API key encryption...
python manage.py makemigrations ai_bridge
echo.

echo [2/5] Running migrations...
python manage.py migrate
echo.

echo [3/5] Adding all changed files to git...
git add .
echo.

echo [4/5] Showing git status...
git status
echo.

echo [5/5] Creating commit...
git commit -m "feat: Major upgrade to v2.0.0 - Multi-provider AI, encryption, comprehensive tests

✨ Features:
- Added Gemini AI Provider support
- Added Groq AI Provider support
- Implemented API key encryption (Fernet)
- Added comprehensive test suite (55+ tests)
- Enhanced admin panel with colored badges and previews

🔧 Configuration:
- Added requirements.txt with all dependencies
- Added .gitignore for clean repo
- Added env.example for easy setup
- Added pytest configuration

📚 Documentation:
- Completely rewrote README.md
- Added CHANGELOG.md
- Added UPGRADE_NOTES.md
- Added IMPROVEMENTS_SUMMARY.md

🎨 UI/UX:
- Admin panel improvements (badges, previews, filters)
- Date hierarchy
- AI + Heuristic action options

🔐 Security:
- Automatic API key encryption on save
- Decryption on provider usage
- Django SECRET_KEY based encryption

📊 Testing:
- cv_manager tests (20+ cases)
- job_analyzer tests (15+ cases)
- ai_bridge tests (10+ cases)
- applicant_letters tests (10+ cases)
- pytest and coverage configuration

Breaking Changes:
- UserAISettings.api_key field increased to 512 chars (migration required)
- API keys will be auto-encrypted on first save after upgrade
"

echo.
echo ========================================
echo Commit completed!
echo ========================================
echo.
echo To push to GitHub, run:
echo git push origin main
echo.
pause
