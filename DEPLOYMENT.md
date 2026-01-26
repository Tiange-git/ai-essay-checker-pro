# 前后端分离部署指南

本文档介绍如何将AI作文批改助手的前后端分离部署到Vercel（前端）和Railway（后端），实现完全免费上线。

## 部署架构

```
┌─────────────────┐         ┌─────────────────┐
│   Vercel        │         │   Railway       │
│   (前端)        │────────>│   (后端)        │
│   Vue 3         │  HTTPS  │   Flask API     │
│   免费          │         │   免费          │
└─────────────────┘         └─────────────────┘
```

## 前提条件

- GitHub账号
- Railway账号（免费）
- Vercel账号（免费）
- 本地安装Git

---

## 第一步：准备项目代码

### 1. 初始化Git仓库

```bash
cd e:\TRAE\112\ai-essay-checker-pro
git init
git add .
git commit -m "Initial commit for deployment"
```

### 2. 创建GitHub仓库

1. 访问 https://github.com/new
2. 创建新仓库：`ai-essay-checker-pro`
3. 不要初始化README、.gitignore或license
4. 点击"Create repository"

### 3. 推送代码到GitHub

```bash
git remote add origin https://github.com/yourusername/ai-essay-checker-pro.git
git branch -M main
git push -u origin main
```

---

## 第二步：部署后端到Railway

### 1. 注册Railway

1. 访问 https://railway.app
2. 点击"Start a Project"
3. 使用GitHub账号登录

### 2. 创建后端项目

#### 方法A：使用Railway CLI（推荐）

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
cd e:\TRAE\112\ai-essay-checker-pro
railway init
```

#### 方法B：使用Railway Web界面

1. 登录Railway控制台
2. 点击"New Project"
3. 选择"Deploy from GitHub repo"
4. 选择你的仓库
5. 选择`backend`目录作为根目录

### 3. 配置环境变量

在Railway控制台的"Variables"标签页中添加以下变量：

```bash
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-generated-secret-key

# 讯飞星火API配置
APPID=92c3f099
APISecret=MDVkMTY3ODY1NjYzMTQzYWQ5MWE5ZTgy
APIKey=a83fe4b80a46bdd89b367ab32b0af74e

# 讯飞OCR API配置
OCR_APPID=e519a66d
OCR_API_KEY=43c544744d546de66a3c150cf164c815
OCR_API_SECRET=YmRiMWNmN2JmY2JhYWE4ZmExOGNlMzYy
OCR_URL=https://api.xf-yun.com/v1/private/hh_ocr_recognize_doc

# CORS配置（稍后配置前端URL）
FRONTEND_URL=*
```

**生成SECRET_KEY：**
```bash
openssl rand -hex 32
```

### 4. 部署后端

```bash
# 使用CLI
cd backend
railway up
```

或在Railway控制台点击"Deploy"按钮。

### 5. 获取后端URL

部署完成后，在Railway控制台找到你的后端URL，格式类似：
```
https://ai-essay-checker-backend.up.railway.app
```

记录这个URL，稍后配置前端时需要用到。

### 6. 测试后端

```bash
# 测试健康检查
curl https://your-backend-url.railway.app/health
```

应该返回：
```json
{"status": "ok", "message": "服务运行正常"}
```

---

## 第三步：部署前端到Vercel

### 1. 注册Vercel

1. 访问 https://vercel.com
2. 点击"Sign Up"
3. 使用GitHub账号登录

### 2. 创建前端项目

#### 方法A：使用Vercel CLI（推荐）

```bash
# 安装Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署前端
cd frontend
vercel
```

#### 方法B：使用Vercel Web界面

1. 登录Vercel控制台
2. 点击"Add New Project"
3. 导入你的GitHub仓库
4. 选择`frontend`目录作为根目录
5. 框架预设选择"Vite"

### 3. 配置环境变量

在Vercel控制台的"Settings > Environment Variables"中添加：

```bash
VITE_API_URL=https://your-backend-url.railway.app
```

**重要：** 将`your-backend-url.railway.app`替换为你在第二步中获取的实际后端URL。

### 4. 部署前端

```bash
# 使用CLI
cd frontend
vercel --prod
```

或在Vercel控制台点击"Deploy"按钮。

### 5. 获取前端URL

部署完成后，Vercel会提供一个URL，格式类似：
```
https://ai-essay-checker-frontend.vercel.app
```

---

## 第四步：配置CORS（跨域访问）

### 1. 更新后端CORS配置

回到Railway控制台，修改`FRONTEND_URL`变量：

```bash
FRONTEND_URL=https://your-frontend-url.vercel.app
```

**重要：** 将`your-frontend-url.vercel.app`替换为你在第三步中获取的实际前端URL。

### 2. 重新部署后端

```bash
cd backend
railway up
```

或在Railway控制台点击"Redeploy"按钮。

---

## 第五步：测试完整功能

### 1. 访问前端

打开浏览器，访问你的前端URL：
```
https://ai-essay-checker-frontend.vercel.app
```

### 2. 测试功能

1. **测试文本批改**
   - 输入一段英文作文
   - 点击"开始批改"
   - 查看批改结果

2. **测试文件上传**
   - 上传Word文档
   - 点击"开始批改"
   - 查看批改结果

3. **测试历史记录**
   - 查看批改历史
   - 测试删除功能

### 3. 检查网络请求

打开浏览器开发者工具（F12），查看Network标签：
- 确保API请求发送到正确的后端URL
- 确保没有CORS错误
- 确保响应数据正确

---

## 第六步：配置自定义域名（可选）

### 1. 购买域名

在阿里云、腾讯云等平台购买域名（约50-100元/年）。

### 2. 配置前端域名

1. 在Vercel控制台，进入"Settings > Domains"
2. 添加你的域名（如：`essay.yourdomain.com`）
3. 按照Vercel的指引配置DNS记录

### 3. 配置后端域名（可选）

如果需要为后端配置独立域名：

1. 在Railway控制台，进入"Settings > Domains"
2. 添加你的域名（如：`api.yourdomain.com`）
3. 按照Railway的指引配置DNS记录

### 4. 更新环境变量

更新Vercel的`VITE_API_URL`和Railway的`FRONTEND_URL`为新的自定义域名。

---

## 监控和维护

### 查看日志

#### 后端日志（Railway）
```bash
railway logs
```

或在Railway控制台的"Logs"标签页查看。

#### 前端日志（Vercel）
在Vercel控制台的"Logs"标签页查看。

### 更新部署

#### 更新后端
```bash
git add .
git commit -m "Update backend"
git push
cd backend
railway up
```

#### 更新前端
```bash
git add .
git commit -m "Update frontend"
git push
cd frontend
vercel --prod
```

### 自动部署

配置GitHub集成后，每次推送到main分支会自动触发部署。

---

## 故障排查

### 问题1：前端无法连接后端

**症状：** 浏览器控制台显示CORS错误或网络错误

**解决方案：**
1. 检查Vercel的`VITE_API_URL`是否正确
2. 检查Railway的`FRONTEND_URL`是否正确
3. 确保后端服务正常运行
4. 检查Railway日志查看错误信息

### 问题2：后端部署失败

**症状：** Railway显示部署错误

**解决方案：**
1. 检查Dockerfile是否正确
2. 检查requirements.txt是否包含所有依赖
3. 查看Railway日志获取详细错误信息
4. 确保环境变量配置正确

### 问题3：讯飞API调用失败

**症状：** 批改功能不工作

**解决方案：**
1. 检查API密钥是否正确
2. 检查网络连接
3. 查看后端日志获取详细错误信息
4. 确认API额度是否充足

### 问题4：文件上传失败

**症状：** 上传文件时出错

**解决方案：**
1. 检查文件大小是否超过限制（16MB）
2. 检查文件格式是否支持
3. 查看后端日志获取详细错误信息
4. 确保uploads目录存在且有写权限

---

## 成本估算

| 服务 | 免费额度 | 实际成本 |
|------|----------|----------|
| Vercel（前端） | 无限带宽 | ¥0/月 |
| Railway（后端） | $5/月额度 | ¥0-30/月（超出后） |
| 域名（可选） | - | ¥50-100/年 |
| **总计** | - | **¥0-30/月** |

**注意：**
- Railway的免费额度通常足够小型项目使用
- 如果流量较大，可能需要升级付费计划
- 域名是可选的，可以使用平台提供的免费域名

---

## 性能优化建议

### 前端优化

1. **启用CDN**
   - Vercel自动提供全球CDN
   - 静态资源自动缓存

2. **代码分割**
   - Vite自动进行代码分割
   - 按需加载组件

3. **图片优化**
   - 使用WebP格式
   - 压缩图片大小

### 后端优化

1. **使用缓存**
   - 考虑使用Redis缓存API响应
   - 减少重复计算

2. **数据库优化**
   - 如果使用数据库，添加索引
   - 优化查询语句

3. **负载均衡**
   - Railway自动提供负载均衡
   - 可以增加实例数量

---

## 安全建议

1. **保护API密钥**
   - 不要在代码中硬编码密钥
   - 使用环境变量管理敏感信息
   - 定期轮换密钥

2. **启用HTTPS**
   - Vercel和Railway自动提供HTTPS
   - 强制使用HTTPS

3. **限制访问频率**
   - 添加速率限制
   - 防止API滥用

4. **输入验证**
   - 验证所有用户输入
   - 防止注入攻击

---

## 备份策略

### 代码备份
- 代码存储在GitHub
- 自动版本控制

### 数据备份
- Railway提供自动备份
- 可以定期导出数据

### 环境变量备份
- 保存.env文件到安全位置
- 使用密码管理器存储密钥

---

## 扩展功能

### 添加数据库

如果需要持久化存储：

1. 在Railway添加PostgreSQL服务
2. 修改后端代码连接数据库
3. 创建数据模型和迁移

### 添加用户认证

1. 添加JWT认证
2. 实现用户注册/登录
3. 保护API端点

### 添加支付功能

1. 集成支付网关（如Stripe）
2. 实现订阅计划
3. 管理用户订阅

---

## 总结

通过本指南，你已经成功将AI作文批改助手的前后端分离部署到Vercel和Railway，实现了：

✅ 完全免费部署
✅ 自动HTTPS
✅ 全球CDN加速
✅ 自动扩展
✅ 简单维护

如有任何问题，请参考故障排查部分或查看平台文档。

---

## 相关链接

- [Vercel文档](https://vercel.com/docs)
- [Railway文档](https://docs.railway.app)
- [Vue 3文档](https://vuejs.org)
- [Flask文档](https://flask.palletsprojects.com)
- [讯飞星火API文档](https://www.xfyun.cn/doc/spark/)
