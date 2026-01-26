# 英语作文批改助手 (AI Essay Checker Pro)

一个基于讯飞星火API的智能英语作文批改系统，提供实时批改、语法错误检测、评分和改进建议等功能。

## 功能特性

- 📝 **智能批改**：利用讯飞星火API进行深度语义分析，提供准确的批改结果
- 🎯 **多维度反馈**：包括语法错误、逻辑问题、评分和改进建议
- 📱 **移动端友好**：响应式设计，支持微信小程序兼容性
- 🌐 **前后端分离**：Flask后端 + Vue 3前端，架构清晰
- 🔒 **安全可靠**：使用环境变量管理敏感信息，WebSocket加密通信
- 📄 **多输入方式**：支持文本输入、Word文档上传和图片上传（OCR接口预留）

## 技术栈

### 后端
- Python 3.14
- Flask 3.1.2
- Flask-CORS 4.0.0
- 讯飞星火API (WebSocket)
- python-dotenv
- websocket-client
- python-docx (Word文档解析)
- Pillow (图片处理)

### 前端
- Vue 3
- Vite 4.4.11
- Axios 1.6.2
- 响应式设计

## 项目结构

```
ai-essay-checker-pro/
├── backend/              # 后端代码
│   ├── app.py            # Flask应用入口
│   ├── requirements.txt  # Python依赖
│   ├── .env              # 环境变量配置
│   ├── uploads/          # 临时上传文件目录
│   ├── routes/           # API路由
│   │   └── essay_routes.py  # 作文批改路由
│   └── services/         # 服务层
│       ├── xunfei_api.py  # 讯飞API集成
│       └── file_processor.py  # 文件处理器（Word和图片）
├── frontend/             # 前端代码
│   ├── index.html        # HTML入口
│   ├── main.js           # Vue应用入口
│   ├── package.json      # npm依赖
│   ├── vite.config.js    # Vite配置
│   └── src/              # 源代码
│       ├── App.vue       # 根组件
│       ├── components/   # 组件
│       │   └── EssayChecker.vue  # 作文批改组件
│       └── api/          # API调用
│           └── essayAPI.js  # 作文API
└── README.md             # 项目文档
```

## 快速开始

### 1. 环境要求

- Python 3.7+
- Node.js 16+
- npm 8+

### 2. 安装依赖

#### 后端依赖

```bash
# 进入backend目录
cd backend

# 安装Python依赖
python -m pip install -r requirements.txt
```

#### 前端依赖

```bash
# 进入frontend目录
cd frontend

# 安装npm依赖
npm install
```

### 3. 配置环境变量

在 `backend/.env` 文件中配置讯飞星火API的相关信息：

```env
# 讯飞星火API配置
APPID=your_app_id
APISecret=your_api_secret
APIKey=your_api_key

# 服务器配置
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

### 4. 启动服务

#### 启动后端服务

```bash
# 在backend目录中运行
python app.py
```

后端服务将在 `http://localhost:5000` 上运行。

#### 启动前端服务

```bash
# 在frontend目录中运行
npm run dev
```

前端服务将在 `http://localhost:3000` 上运行。

### 5. 使用方法

#### 文本输入方式
1. 打开浏览器访问 `http://localhost:3000`
2. 在文本框中输入您的英语作文
3. 点击「开始批改」按钮
4. 等待系统分析并显示批改结果
5. 查看评分、语法错误和改进建议

#### Word文档上传方式
1. 打开浏览器访问 `http://localhost:3000`
2. 在「或上传文件」区域点击「上传Word文档」按钮
3. 选择要上传的Word文档（.docx格式）
4. 点击「开始批改」按钮
5. 等待系统解析文档并显示批改结果
6. 查看提取的内容和批改结果

#### 图片上传方式
1. 打开浏览器访问 `http://localhost:3000`
2. 在「或上传文件」区域点击「上传图片」按钮
3. 选择要上传的图片（支持png、jpg、jpeg、gif格式）
4. 点击「开始批改」按钮
5. 等待系统处理图片并显示批改结果（OCR接口预留）
6. 查看提取的内容和批改结果

## API文档

### 1. 批改作文

- **接口**：`POST /api/check-essay`
- **请求参数**：
  ```json
  {
    "content": "Your essay content here"
  }
  ```
- **响应示例**：
  ```json
  {
    "success": true,
    "result": {
      "feedback": "Detailed feedback here",
      "score": 85,
      "suggestions": ["Improve structure", "Add more examples"],
      "grammar_errors": ["Tense error", "Subject-verb agreement"]
    }
  }
  ```

### 2. 文件上传

- **接口**：`POST /api/upload-file`
- **请求参数**：FormData格式，包含名为"file"的文件字段
- **支持的文件类型**：
  - Word文档：.docx
  - 图片：.png, .jpg, .jpeg, .gif
- **响应示例**：
  ```json
  {
    "success": true,
    "result": {
      "feedback": "Detailed feedback here",
      "score": 85,
      "suggestions": ["Improve structure", "Add more examples"],
      "grammar_errors": ["Tense error", "Subject-verb agreement"]
    },
    "content": "Extracted content from file"
  }
  ```

### 3. 获取批改历史

- **接口**：`GET /api/history`
- **响应示例**：
  ```json
  {
    "success": true,
    "history": [
      {
        "id": 1,
        "content": "Test essay",
        "result": {"score": 85, "suggestions": [...]},
        "created_at": "2026-01-23 19:00:00"
      }
    ]
  }
  ```

### 4. 健康检查

- **接口**：`GET /health`
- **响应示例**：
  ```json
  {
    "status": "ok",
    "message": "服务运行正常"
  }
  ```

## 微信小程序兼容性

本项目的前端设计考虑了微信小程序的兼容性：

- 使用了响应式布局，适配不同屏幕尺寸
- 避免使用微信小程序不支持的Web API
- 采用轻量级设计，减少资源占用
- 支持触摸交互，优化移动端体验

## 部署建议

### 开发环境
- 使用本项目提供的开发服务器
- 确保环境变量配置正确

### 生产环境
- 使用Gunicorn或uWSGI作为WSGI服务器
- 配置Nginx作为反向代理
- 使用HTTPS加密传输
- 定期更新依赖，修复安全漏洞

## 故障排查

### 常见问题

1. **后端服务启动失败**
   - 检查Python版本是否符合要求
   - 检查依赖是否安装完整
   - 检查环境变量配置是否正确

2. **前端无法连接后端**
   - 检查后端服务是否运行
   - 检查CORS配置是否正确
   - 检查前端API地址是否配置正确

3. **讯飞API调用失败**
   - 检查API密钥是否正确
   - 检查网络连接是否正常
   - 查看日志获取详细错误信息

### 日志查看

后端日志会输出到控制台，包含详细的错误信息和API调用记录。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request，共同改进这个项目！

## 联系方式

如有问题，请通过以下方式联系：
- Email: 3168956195@qq.com
- GitHub: https://github.com/Tiange-git/ai-essay-checker-pro

---

**© 2026 英语作文批改助手**
