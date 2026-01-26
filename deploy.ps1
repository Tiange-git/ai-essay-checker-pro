# Deployment Script (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AI Essay Checker - Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check required tools
function Check-Tool {
    param($name, $command)
    
    $result = Get-Command $command -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host "[OK] $name is installed" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[ERROR] $name is not installed" -ForegroundColor Red
        return $false
    }
}

Write-Host "Checking required tools..." -ForegroundColor Yellow
$gitInstalled = Check-Tool "Git" "git"
$nodeInstalled = Check-Tool "Node.js" "node"
$npmInstalled = Check-Tool "npm" "npm"

if (-not $gitInstalled -or -not $nodeInstalled -or -not $npmInstalled) {
    Write-Host ""
    Write-Host "Please install missing tools first" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Ask if GitHub repo exists
$hasRepo = Read-Host "Have you created a GitHub repository? (y/n)"

if ($hasRepo -ne "y") {
    Write-Host ""
    Write-Host "Please create a GitHub repository first:" -ForegroundColor Yellow
    Write-Host "1. Visit https://github.com/new"
    Write-Host "2. Create new repository: ai-essay-checker-pro"
    Write-Host "3. Do NOT initialize README, .gitignore or license"
    Write-Host "4. Click 'Create repository'"
    Write-Host ""
    Read-Host "Press Enter after creating the repository..."
}

# Initialize Git repository
Write-Host ""
Write-Host "Initializing Git repository..." -ForegroundColor Yellow
git init
git add .
git commit -m "Initial commit for deployment"
Write-Host "[OK] Git repository initialized" -ForegroundColor Green

# Push to GitHub
Write-Host ""
$repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/ai-essay-checker-pro.git)"
git remote add origin $repoUrl
git branch -M main
git push -u origin main
Write-Host "[OK] Code pushed to GitHub" -ForegroundColor Green
Write-Host ""

# Deploy backend to Railway
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Step 1: Deploy Backend to Railway" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Visit https://railway.app and login"
Write-Host "2. Click 'New Project' -> 'Deploy from GitHub repo'"
Write-Host "3. Select your repository"
Write-Host "4. Select 'backend' directory as root directory"
Write-Host "5. Click 'Deploy'"
Write-Host ""
Write-Host "After deployment, configure these environment variables in Railway:" -ForegroundColor Yellow
Write-Host ""
Write-Host "FLASK_ENV=production"
Write-Host "SECRET_KEY=generate-a-random-key"
Write-Host "APPID=92c3f099"
Write-Host "APISecret=MDVkMTY3ODY1NjYzMTQzYWQ5MWE5ZTgy"
Write-Host "APIKey=a83fe4b80a46bdd89b367ab32b0af74e"
Write-Host "OCR_APPID=e519a66d"
Write-Host "OCR_API_KEY=43c544744d546de66a3c150cf164c815"
Write-Host "OCR_API_SECRET=YmRiMWNmN2JmY2JhYWE4ZmExOGNlMzYy"
Write-Host "OCR_URL=https://api.xf-yun.com/v1/private/hh_ocr_recognize_doc"
Write-Host "FRONTEND_URL=*"
Write-Host ""
$backendUrl = Read-Host "After backend deployment, enter backend URL (e.g., https://ai-essay-checker-backend.up.railway.app)"
Write-Host ""

# Deploy frontend to Vercel
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Step 2: Deploy Frontend to Vercel" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Visit https://vercel.com and login"
Write-Host "2. Click 'Add New Project' -> 'Import Git Repository'"
Write-Host "3. Select your repository"
Write-Host "4. Select 'frontend' directory as root directory"
Write-Host "5. Framework preset: 'Vite'"
Write-Host "6. Click 'Deploy'"
Write-Host ""
Write-Host "After deployment, configure this environment variable in Vercel:" -ForegroundColor Yellow
Write-Host ""
Write-Host "VITE_API_URL=$backendUrl"
Write-Host ""
$frontendUrl = Read-Host "After frontend deployment, enter frontend URL (e.g., https://ai-essay-checker-frontend.vercel.app)"
Write-Host ""

# Update CORS configuration
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Step 3: Update CORS Configuration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please update FRONTEND_URL variable in Railway:" -ForegroundColor Yellow
Write-Host ""
Write-Host "FRONTEND_URL=$frontendUrl"
Write-Host ""
Write-Host "Then click 'Redeploy' to redeploy backend"
Write-Host ""

# Done
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your application has been deployed:" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Cyan
Write-Host "Backend URL: $backendUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now visit the frontend URL to test the application!" -ForegroundColor Green
Write-Host ""
Write-Host "For issues, please check DEPLOYMENT.md" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
