# 前端 Dockerfile - Railway deployment
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建生产版本
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN node node_modules/vite/bin/vite.js build

# 生产阶段 - 使用Nginx
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制启动脚本
COPY entrypoint.sh /entrypoint.sh

# 设置脚本执行权限
RUN chmod +x /entrypoint.sh

# 暴露端口
EXPOSE 80

# 设置环境变量默认值
ENV BACKEND_URL=http://localhost:5000

# 使用启动脚本
ENTRYPOINT ["/entrypoint.sh"]
