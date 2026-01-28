# 后端 Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口（Railway会自动设置PORT环境变量）
EXPOSE 5000

# 启动命令（使用Railway的PORT环境变量，优化配置适应免费实例）
CMD ["sh", "-c", "gunicorn -w 1 -b 0.0.0.0:${PORT:-5000} --timeout 300 --access-logfile - --error-logfile - --worker-class sync --max-requests 1000 --max-requests-jitter 50 app:app"]
