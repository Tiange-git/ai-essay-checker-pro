#!/bin/bash

echo "=========================================="
echo "  AI作文批改助手 - 快速部署脚本"
echo "=========================================="
echo ""

# 检查是否安装了必要的工具
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 未安装，请先安装 $1"
        exit 1
    else
        echo "✅ $1 已安装"
    fi
}

echo "检查必要工具..."
check_tool git
check_tool node
check_tool npm
echo ""

# 询问用户是否已经创建了GitHub仓库
read -p "是否已经创建了GitHub仓库？(y/n): " has_repo

if [ "$has_repo" != "y" ]; then
    echo ""
    echo "请先在GitHub创建仓库："
    echo "1. 访问 https://github.com/new"
    echo "2. 创建新仓库：ai-essay-checker-pro"
    echo "3. 不要初始化README、.gitignore或license"
    echo "4. 点击'Create repository'"
    echo ""
    read -p "创建完成后按回车继续..."
fi

# 初始化Git仓库
echo ""
echo "初始化Git仓库..."
git init
git add .
git commit -m "Initial commit for deployment"
echo "✅ Git仓库初始化完成"

# 推送到GitHub
read -p "请输入你的GitHub仓库URL (例如: https://github.com/username/ai-essay-checker-pro.git): " repo_url
git remote add origin $repo_url
git branch -M main
git push -u origin main
echo "✅ 代码已推送到GitHub"
echo ""

# 部署后端到Railway
echo "=========================================="
echo "  第一步：部署后端到Railway"
echo "=========================================="
echo ""
echo "请按照以下步骤操作："
echo ""
echo "1. 访问 https://railway.app 并登录"
echo "2. 点击 'New Project' -> 'Deploy from GitHub repo'"
echo "3. 选择你的仓库"
echo "4. 选择 'backend' 目录作为根目录"
echo "5. 点击 'Deploy'"
echo ""
echo "部署完成后，在Railway控制台配置以下环境变量："
echo ""
echo "FLASK_ENV=production"
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "APPID=92c3f099"
echo "APISecret=MDVkMTY3ODY1NjYzMTQzYWQ5MWE5ZTgy"
echo "APIKey=a83fe4b80a46bdd89b367ab32b0af74e"
echo "OCR_APPID=e519a66d"
echo "OCR_API_KEY=43c544744d546de66a3c150cf164c815"
echo "OCR_API_SECRET=YmRiMWNmN2JmY2JhYWE4ZmExOGNlMzYy"
echo "OCR_URL=https://api.xf-yun.com/v1/private/hh_ocr_recognize_doc"
echo "FRONTEND_URL=*"
echo ""
read -p "后端部署完成后，请输入后端URL (例如: https://ai-essay-checker-backend.up.railway.app): " backend_url
echo ""

# 部署前端到Vercel
echo "=========================================="
echo "  第二步：部署前端到Vercel"
echo "=========================================="
echo ""
echo "请按照以下步骤操作："
echo ""
echo "1. 访问 https://vercel.com 并登录"
echo "2. 点击 'Add New Project' -> 'Import Git Repository'"
echo "3. 选择你的仓库"
echo "4. 选择 'frontend' 目录作为根目录"
echo "5. 框架预设选择 'Vite'"
echo "6. 点击 'Deploy'"
echo ""
echo "部署完成后，在Vercel控制台配置环境变量："
echo ""
echo "VITE_API_URL=$backend_url"
echo ""
read -p "前端部署完成后，请输入前端URL (例如: https://ai-essay-checker-frontend.vercel.app): " frontend_url
echo ""

# 更新CORS配置
echo "=========================================="
echo "  第三步：更新CORS配置"
echo "=========================================="
echo ""
echo "请在Railway控制台更新FRONTEND_URL变量："
echo ""
echo "FRONTEND_URL=$frontend_url"
echo ""
echo "然后点击 'Redeploy' 重新部署后端"
echo ""

# 完成
echo "=========================================="
echo "  🎉 部署完成！"
echo "=========================================="
echo ""
echo "你的应用已成功部署："
echo ""
echo "前端地址: $frontend_url"
echo "后端地址: $backend_url"
echo ""
echo "现在可以访问前端地址测试应用了！"
echo ""
echo "如有问题，请查看 DEPLOYMENT.md 文档"
echo ""
