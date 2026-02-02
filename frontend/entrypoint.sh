#!/bin/sh

# 如果设置了 PORT 环境变量，使用它来配置 nginx
if [ ! -z "$PORT" ]; then
    echo "Configuring nginx to listen on port $PORT"
    sed -i "s/listen 80;/listen $PORT;/g" /etc/nginx/conf.d/default.conf
fi

# 启动 nginx
exec nginx -g 'daemon off;'
