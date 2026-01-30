@echo off
echo ============================================
echo    Vercel部署诊断工具
echo ============================================
echo.

cd /d "%~dp0"

echo [1/6] 检查前端目录结构...
if exist "frontend\package.json" (
    echo    ✅ package.json 存在
) else (
    echo    ❌ package.json 不存在
    echo    提示: 确保在项目根目录运行此脚本
    pause
    exit /b 1
)

echo.
echo [2/6] 检查Vercel配置文件...
if exist "frontend\vercel.json" (
    echo    ✅ vercel.json 存在
    type frontend\vercel.json | findstr /C:"buildCommand" >nul
    if %errorlevel% equ 0 (
        echo    ✅ buildCommand 配置正确
    ) else (
        echo    ⚠️  buildCommand 可能需要配置
    )
) else (
    echo    ❌ vercel.json 不存在
)

echo.
echo [3/6] 检查环境变量配置...
if exist "frontend\.env.example" (
    echo    ✅ .env.example 存在
    echo.
    echo    当前环境变量配置（请在Vercel控制台手动配置）:
    type frontend\.env.example
    echo.
) else (
    echo    ⚠️  .env.example 不存在
)

echo.
echo [4/6] 检查Vite配置...
if exist "frontend\vite.config.js" (
    echo    ✅ vite.config.js 存在
    type frontend\vite.config.js | findstr /C:"base:" >nul
    if %errorlevel% equ 0 (
        echo    ✅ base 配置存在
    ) else (
        echo    ⚠️  建议检查 base 配置
    )
) else (
    echo    ❌ vite.config.js 不存在
)

echo.
echo [5/6] 检查API配置...
if exist "frontend\src\api\essayAPI.js" (
    echo    ✅ essayAPI.js 存在
    type frontend\src\api\essayAPI.js | findstr /C:"VITE_API_URL" >nul
    if %errorlevel% equ 0 (
        echo    ✅ 使用环境变量 VITE_API_URL
    ) else (
        echo    ⚠️  未使用 VITE_API_URL 环境变量
    )
) else (
    echo    ❌ essayAPI.js 不存在
)

echo.
echo [6/6] 构建测试（本地）...
echo    尝试本地构建...
cd frontend
npm run build > ..\build.log 2>&1
if %errorlevel% equ 0 (
    echo    ✅ 本地构建成功!
    if exist "dist\index.html" (
        echo    ✅ dist\index.html 生成
    )
) else (
    echo    ❌ 本地构建失败
    echo    查看 build.log 获取详细信息
)
cd ..

echo.
echo ============================================
echo    诊断完成
echo ============================================
echo.
echo 下一步操作:
echo 1. 确保 Vercel 控制台中已配置环境变量 VITE_API_URL
echo 2. 确保后端服务已在 Railway 部署并运行
echo 3. 在 Vercel 控制台查看部署日志
echo 4. 检查浏览器控制台错误信息
echo.
echo 提示: 查看 frontend\build.log 了解构建详情
echo.
pause
