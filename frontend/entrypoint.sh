#!/bin/sh

echo "=== Starting nginx with Railway configuration ==="
echo "PORT environment variable: ${PORT:-not set}"

# 使用 envsubst 处理 nginx 配置中的环境变量
echo "Processing nginx configuration with environment variables..."
envsubst '${PORT}' < /etc/nginx/conf.d/default.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/conf.d/default.conf

echo "Nginx configuration:"
cat /etc/nginx/conf.d/default.conf

echo "=== Starting nginx ==="
# 启动 nginx
exec nginx -g 'daemon off;'
