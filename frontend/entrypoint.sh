#!/bin/sh

echo "=== Starting nginx with Railway configuration ==="
echo "PORT environment variable: ${PORT:-not set (using 80)}"

# 如果设置了 PORT 环境变量，修改 nginx 配置
if [ ! -z "$PORT" ]; then
    echo "Updating nginx to listen on port $PORT"
    sed -i "s/listen 80 default_server;/listen $PORT default_server;/g" /etc/nginx/conf.d/default.conf
    sed -i "s/listen \[::\]:80 default_server;/listen [::]:$PORT default_server;/g" /etc/nginx/conf.d/default.conf
fi

echo "=== Starting nginx ==="
# 启动 nginx
exec nginx -g 'daemon off;'
