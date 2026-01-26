#!/usr/bin/env python3
"""
完全按照讯飞官方文档实现签名算法
官方文档要求：
- authorization参数必须放在请求头中
- headers参数固定为"host date request-line"
- 签名原始字符串格式：host: {host}\ndate: {date}\n{request-line}
"""

import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def generate_official_signature():
    """按照官方文档生成签名"""
    print("=== 官方签名算法实现 ===")
    
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    APPID = os.getenv('OCR_APPID')
    
    print(f"API_KEY: {API_KEY}")
    print(f"APPID: {APPID}")
    
    # 解析URL
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    
    # 生成时间戳（必须使用GMT时间）
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    
    # 生成request-line（必须包含HTTP版本）
    request_line = f"POST {parsed_url.path} HTTP/1.1"
    
    # 签名原始字符串（严格按照官方格式）
    signature_origin = f"host: {host}\ndate: {date}\n{request_line}"
    
    print(f"签名原始字符串:\n{signature_origin}")
    print(f"原始字符串长度: {len(signature_origin)}")
    
    # HMAC-SHA256签名
    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'), 
        signature_origin.encode('utf-8'), 
        digestmod=hashlib.sha256
    ).digest()
    
    # Base64编码签名
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    # 生成authorization原始字符串
    authorization_origin = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    
    # Base64编码authorization
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    print(f"签名结果: {signature}")
    print(f"签名长度: {len(signature)}")
    print(f"authorization原始字符串: {authorization_origin}")
    print(f"authorization编码后: {authorization}")
    print(f"authorization长度: {len(authorization)}")
    
    return date, authorization, host, APPID

def test_official_api():
    """使用官方算法测试API调用"""
    print("\n=== 测试官方算法API调用 ===")
    
    date, authorization, host, APPID = generate_official_signature()
    OCR_URL = os.getenv('OCR_URL')
    
    # 构建请求头（authorization必须放在Header中）
    headers = {
        'Content-Type': 'application/json',
        'Host': host,
        'Date': date,
        'Authorization': authorization,
        'X-Appid': APPID
    }
    
    print(f"请求头:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"  {key}: {value[:50]}...")
        else:
            print(f"  {key}: {value}")
    
    # 构建请求体
    data = {
        "header": {
            "app_id": APPID,
            "status": 3
        },
        "parameter": {
            "hh_ocr_recognize_doc": {
                "recognizeDocumentRes": {
                    "encoding": "utf8",
                    "compress": "raw", 
                    "format": "json"
                }
            }
        },
        "payload": {
            "image": {
                "encoding": "png",
                "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC",
                "status": 3
            }
        }
    }
    
    print(f"请求体大小: {len(str(data))} bytes")
    
    try:
        # 发送请求
        response = requests.post(OCR_URL, headers=headers, json=data, timeout=10)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ API调用成功！")
        else:
            print("❌ API调用失败")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_official_api()