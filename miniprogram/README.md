# AI英语作文批改微信小程序

本项目是将 [ai-essay-checker-pro](https://github.com/your-repo/ai-essay-checker-pro) 的Web版本转换为微信小程序版本。

## 功能特性

- 文本输入批改
- Word文档上传批改
- 图片上传批改
- 语法错误检测
- 智能评分反馈
- 历史记录管理
- 错误对比查看

## 项目结构

```
miniprogram/
├── app.js              # 小程序入口文件
├── app.json            # 小程序配置
├── app.wxss            # 全局样式
├── pages/
│   ├── index/          # 首页（批改入口）
│   ├── result/         # 结果展示页
│   └── history/        # 历史记录页
├── services/
│   └── api.js          # API服务层
├── cloudfunctions/     # 云函数
│   ├── checkEssay/     # 作文批改云函数
│   ├── uploadFile/     # 文件上传云函数
│   └── getHistory/     # 获取历史记录云函数
├── images/             # 图片资源
└── sitemap.json        # sitemap配置
```

## 快速开始

### 1. 安装微信开发者工具

下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)

### 2. 导入项目

1. 打开微信开发者工具
2. 点击"+"号创建新项目
3. 选择"导入项目"
4. 选择本项目的 `miniprogram` 目录
5. 填写你的小程序AppID（没有可使用测试号）
6. 点击"确定"导入项目

### 3. 配置云开发环境

1. 在微信开发者工具中，点击右上角的"云开发"按钮
2. 按照提示创建云开发环境
3. 复制环境ID并填入 `miniprogram/project.config.json` 的 `cloudfunctionRoot` 对应的环境配置

### 4. 配置讯飞API

在云函数的环境变量中配置讯飞API密钥：

1. 打开微信开发者工具的"云开发"控制台
2. 进入"云函数"页面
3. 点击"checkEssay"云函数
4. 在"配置"中添加环境变量：
   - `XUNFEI_APPID`: 你的讯飞应用ID
   - `XUNFEI_API_KEY`: 你的讯飞API Key
   - `XUNFEI_API_SECRET`: 你的讯飞API Secret

### 5. 部署云函数

1. 在微信开发者工具中，右键点击 `cloudfunctions` 文件夹
2. 选择"上传并部署：云端安装依赖"
3. 等待部署完成

### 6. 配置数据库集合

在云开发控制台的"数据库"中创建以下集合：

- `history`: 存储批改历史记录

## 使用说明

### 文本批改

1. 在首页选择"文本输入"标签
2. 输入或粘贴你的英语作文
3. 点击"开始批改"按钮
4. 查看批改结果

### 文件批改

1. 在首页选择"Word文档"或"图片上传"标签
2. 点击上传区域选择文件
3. 点击"开始批改"按钮
4. 查看批改结果

### 历史记录

1. 点击底部导航栏的"历史"按钮
2. 查看历史批改记录
3. 点击记录可查看详情
4. 支持筛选和删除历史记录

## 目录结构说明

### 页面说明

- **index**: 首页，提供三种输入方式（文本、Word、图片）
- **result**: 批改结果展示页面，显示详细的批改反馈
- **history**: 历史记录页面，管理历史批改记录

### 服务层说明

- **services/api.js**: 封装所有API请求，支持云函数和自有服务器两种模式

### 云函数说明

- **checkEssay**: 调用讯飞API进行作文批改
- **uploadFile**: 处理文件上传和OCR识别
- **getHistory**: 获取用户的批改历史记录

## 常见问题

### Q: 如何切换云函数和自有服务器模式？

在 `services/api.js` 中，将 `API_BASE_URL` 替换为你的服务器地址即可。

### Q: 讯飞API调用失败怎么办？

1. 检查讯飞API密钥是否正确配置
2. 检查云函数环境变量是否设置
3. 查看云函数日志排查问题

### Q: 图片上传失败怎么办？

1. 确保图片大小不超过限制（默认5MB）
2. 确保图片格式支持（png、jpg、jpeg）

## 许可证

MIT License
