#!/usr/bin/env python3
"""
严格按照讯飞官方示例实现OCR API认证
官方示例URL参数认证方式：
http://api.xf-yun.com/v1/private/hh_ocr_recognize_doc?host=api.xf-yun.com&date=...&authorization=...
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

def generate_signature_url_params():
    """
    生成URL参数格式的签名（官方示例方式）
    """
    print("=== 生成URL参数格式签名 ===")
    
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    # 解析URL
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # 生成时间戳
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    
    # 构建签名原始字符串
    signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"
    
    print(f"签名原始字符串:\n{signature_origin}")
    
    # HMAC-SHA256签名
    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    # Base64编码
    signature = base64.b64encode(signature_sha).decode('utf-8')
    print(f"签名结果: {signature}")
    
    # 构建authorization原始字符串
    authorization_origin = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    
    # Base64编码authorization
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    print(f"authorization: {authorization}")
    
    return authorization, date, host

def test_url_params_auth():
    """使用URL参数方式测试API调用（官方示例方式）"""
    print("\n" + "="*70)
    print("=== 测试URL参数认证方式（官方示例方式）===")
    print("="*70)
    
    # 生成签名
    authorization, date, host = generate_signature_url_params()
    
    # 获取APPID
    APPID = os.getenv('OCR_APPID')
    OCR_URL = os.getenv('OCR_URL')
    
    # 构建URL参数（官方示例方式）
    query_params = {
        'host': host,
        'date': date,
        'authorization': authorization
    }
    
    # 构建完整的URL
    full_url = f"{OCR_URL}?{urllib.parse.urlencode(query_params)}"
    
    print(f"\n=== 构建请求URL ===")
    print(f"完整URL: {full_url}")
    
    # 构建请求头（简化）
    headers = {
        'Content-Type': 'application/json',
        'X-Appid': APPID
    }
    
    print(f"\n=== 请求头 ===")
    for key, value in headers.items():
        print(f"{key}: {value}")
    
    # 构建请求体
    test_image = base64.b64encode(b"test image data for OCR").decode('utf-8')
    
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
                "encoding": "jpg",
                "image": test_image,
                "status": 3
            }
        }
    }
    
    print(f"\n=== 发送API请求 ===")
    print(f"请求URL: {full_url}")
    print(f"请求方法: POST")
    print(f"超时时间: 10秒")
    
    try:
        start_time = time.time()
        response = requests.post(full_url, headers=headers, json=data, timeout=10)
        end_time = time.time()
        
        print(f"\n=== API响应 ===")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ URL参数认证方式成功!")
            return True
        else:
            print(f"❌ URL参数认证方式失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def compare_auth_methods():
    """对比两种认证方式"""
    print("\n" + "="*70)
    print("=== 对比两种认证方式 ===")
    print("="*70)
    
    authorization, date, host = generate_signature_url_params()
    APPID = os.getenv('OCR_APPID')
    OCR_URL = os.getenv('OCR_URL')
    
    # 方式1：URL参数方式（官方示例）
    print("\n方式1: URL参数方式")
    query_params = {
        'host': host,
        'date': date,
        'authorization': authorization
    }
    url1 = f"{OCR_URL}?{urllib.parse.urlencode(query_params)}"
    print(f"  URL: {url1}")
    print(f"  Header: {{'Content-Type': 'application/json', 'X-Appid': '{APPID}'}}")
    
    # 方式2：Header方式
    print("\n方式2: Header方式")
    headers2 = {
        'Content-Type': 'application/json',
        'Host': host,
        'Date': date,
        'Authorization': authorization,
        'X-Appid': APPID
    }
    print(f"  URL: {OCR_URL}")
    print(f"  Header: {headers2}")
    
    return url1, headers2

if __name__ == "__main__":
    print("讯飞OCR API认证方式测试")
    print("官方示例: URL参数认证方式")
    print()
    
    # 对比两种方式
    compare_auth_methods()
    
    # 测试URL参数方式
    success = test_url_params_auth()
    
    if success:
        print("\n🎉 官方认证方式测试成功!")
    else:
        print("\n❌ 官方认证方式测试失败")
        print("可能原因:")
        print("1. API密钥无效")
        print("2. OCR服务未开通")
        print("3. 请求参数格式问题")