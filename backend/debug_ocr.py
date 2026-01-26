#!/usr/bin/env python3
"""
调试OCR API调用问题的脚本
"""

import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def debug_ocr_api():
    print("=== OCR API调试 ===")
    
    # 获取配置
    APPID = os.getenv('OCR_APPID')
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    print(f"APPID: {APPID}")
    print(f"API_KEY: {API_KEY[:10]}...")
    print(f"API_SECRET: {API_SECRET[:10]}...")
    print(f"OCR_URL: {OCR_URL}")
    
    # 验证配置
    if not all([APPID, API_KEY, API_SECRET, OCR_URL]):
        print("❌ 配置不完整")
        return
    
    print("✅ 配置完整")
    
    # 测试签名生成
    print("\n=== 测试签名生成 ===")
    
    def generate_signature(api_key, api_secret, url):
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
        request_line = f"POST {parsed_url.path} HTTP/1.1"
        signature_origin = f"host: {host}\ndate: {date}\n{request_line}"
        
        print(f"签名原始字符串: {signature_origin}")
        
        signature_sha = hmac.new(api_secret.encode('utf-8'), 
                               signature_origin.encode('utf-8'), 
                               digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        authorization_origin = f'api_key="{api_key}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        print(f"日期: {date}")
        print(f"签名: {signature[:50]}...")
        print(f"认证头长度: {len(authorization)}")
        
        return date, authorization, host
    
    date, authorization, host = generate_signature(API_KEY, API_SECRET, OCR_URL)
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json',
        'Host': host,
        'Date': date,
        'Authorization': authorization,
        'X-Appid': APPID
    }
    
    print("\n=== 请求头信息 ===")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {value}")
    
    # 测试简单的请求（不包含图片）
    print("\n=== 测试API连通性 ===")
    
    # 使用最小的测试数据
    test_image_base64 = base64.b64encode(b"test").decode('utf-8')
    
    data = {
        "header": {
            "app_id": APPID,
            "status": 3
        },
        "business": {
            "language": "en",
            "category": "document"
        },
        "data": {
            "image": test_image_base64
        }
    }
    
    print(f"请求体大小: {len(json.dumps(data))} 字符")
    
    try:
        # 发送测试请求
        response = requests.post(OCR_URL, headers=headers, json=data, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 401:
            print("❌ 认证失败 - 可能原因:")
            print("1. API密钥无效或过期")
            print("2. API服务未开通")
            print("3. 签名算法不匹配")
            print("4. 请求格式错误")
        elif response.status_code == 200:
            print("✅ API调用成功")
            result = response.json()
            print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"⚠️ 其他错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    debug_ocr_api()