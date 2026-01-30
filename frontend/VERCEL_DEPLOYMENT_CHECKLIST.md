# Vercel部署检查清单

## ✅ 部署前检查

### 1. 本地构建测试
```bash
cd frontend
npm install
npm run build
```
确保本地构建成功，没有错误。

### 2. 检查输出目录
构建完成后，应该看到 `frontend/dist` 目录，包含：
- `index.html`
- `assets/` 目录
- 静态资源文件

### 3. 本地预览（可选）
```bash
npm run preview
```
在浏览器中访问 `http://localhost:4173` 测试构建后的版本。

---

## 🚀 Vercel部署步骤

### 步骤1：推送代码到GitHub
```bash
cd e:\TRAE\112\ai-essay-checker-pro
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 步骤2：登录Vercel
1. 访问 https://vercel.com
2. 使用GitHub账号登录
3. 点击 "Add New Project"

### 步骤3：导入项目
1. 选择 "Import Git Repository"
2. 选择你的仓库 `ai-essay-checker-pro`
3. 点击 "Import"

### 步骤4：配置项目
- **Root Directory**: `frontend` （重要！）
- **Framework Preset**: `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 步骤5：配置环境变量
在 "Environment Variables" 部分添加：

| Key | Value | Environment |
|-----|-------|-------------|
| `VITE_API_URL` | `https://你的后端-url.railway.app` | Production, Preview, Development |

**重要：** 将 `你的后端-url.railway.app` 替换为实际的Railway后端URL。

### 步骤6：部署
点击 "Deploy" 按钮等待部署完成。

---

## 🔧 常见问题排查

### 问题1：白屏/页面打不开

**可能原因：**
- ❌ 资源路径错误
- ❌ 环境变量未配置
- ❌ 构建失败

**解决方案：**
1. 检查浏览器控制台（F12）的错误信息
2. 确认 `VITE_API_URL` 已配置
3. 查看Vercel部署日志

### 问题2：API请求失败

**可能原因：**
- ❌ 后端URL错误
- ❌ CORS配置问题
- ❌ 后端服务未运行

**解决方案：**
1. 确认后端服务正常运行
2. 检查后端的CORS配置
3. 验证 `VITE_API_URL` 环境变量

### 问题3：构建失败

**可能原因：**
- ❌ 依赖安装失败
- ❌ 构建脚本错误
- ❌ 语法错误

**解决方案：**
1. 查看Vercel构建日志
2. 本地运行 `npm run build` 复现问题
3. 检查 package.json 脚本配置

### 问题4：静态资源加载失败

**可能原因：**
- ❌ base路径配置错误
- ❌ 资源路径引用错误

**解决方案：**
1. 确保 `vite.config.js` 中 `base: './'`
2. 使用相对路径引用资源

---

## 📋 部署检查清单

### 部署前
- [ ] 本地构建成功 (`npm run build`)
- [ ] 所有环境变量已配置
- [ ] 后端服务已部署并运行
- [ ] CORS配置正确（后端允许前端域名）

### 部署后
- [ ] Vercel部署成功（无错误）
- [ ] 页面能正常打开
- [ ] API请求能正常工作
- [ ] 没有控制台错误

---

## 🛠️ 调试技巧

### 1. 查看Vercel部署日志
在Vercel控制台，选择项目 → "Deployments" → 选择最新部署 → 查看 "Logs"

### 2. 检查浏览器控制台
- 打开开发者工具（F12）
- 查看 "Console" 标签的错误信息
- 查看 "Network" 标签的请求状态

### 3. 测试API连通性
在浏览器中直接访问：
```
https://你的后端-url.railway.app/health
```
应该返回 JSON 响应。

### 4. 检查环境变量
在Vercel控制台 → "Settings" → "Environment Variables"
确认所有变量都已正确配置。

---

## 📞 获取帮助

如果以上步骤都不能解决问题：

1. **收集信息：**
   - Vercel部署日志（完整输出）
   - 浏览器控制台错误信息
   - 后端服务日志

2. **检查资源：**
   - [Vercel文档](https://vercel.com/docs)
   - [Vite文档](https://vitejs.dev)
   - [Vue 3文档](https://vuejs.org)

3. **常见错误搜索：**
   - "Vercel deployment failed Vue"
   - "Vercel white screen Vue"
   - "Vercel environment variables VITE_"

