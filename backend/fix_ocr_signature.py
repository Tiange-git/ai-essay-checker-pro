#!/usr/bin/env python3
"""
修复OCR API签名算法 - 根据官方文档修正
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

def generate_official_signature():
    """根据官方文档生成正确的签名"""
    print("=== 根据官方文档生成签名 ===")
    
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    # 解析URL
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    
    # 生成date参数（RFC1123格式）
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    
    # 构建request-line（官方示例中的格式）
    request_line = f"POST {parsed_url.path} HTTP/1.1"
    
    # 构建signature_origin（官方格式）
    signature_origin = f"host: {host}\ndate: {date}\n{request_line}"
    
    print("签名原始字符串:")
    print(signature_origin)
    print(f"原始字符串长度: {len(signature_origin)}")
    
    # 使用hmac-sha256算法签名
    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'), 
        signature_origin.encode('utf-8'), 
        digestmod=hashlib.sha256
    ).digest()
    
    # Base64编码
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    print(f"签名结果: {signature}")
    
    # 构建authorization_origin
    authorization_origin = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    
    # Base64编码authorization
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    print(f"认证头长度: {len(authorization)}")
    print(f"认证头前100字符: {authorization[:100]}")
    
    return date, authorization, host

def test_official_method():
    """测试官方签名方法"""
    print("\n=== 测试官方签名方法 ===")
    
    APPID = os.getenv('OCR_APPID')
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    # 生成签名
    date, authorization, host = generate_official_signature()
    
    # 构建URL参数（官方方式）
    query_params = {
        'host': host,
        'date': date,
        'authorization': authorization
    }
    
    # 构建完整的URL（官方示例方式）
    full_url = f"{OCR_URL}?{urllib.parse.urlencode(query_params)}"
    
    print(f"完整URL: {full_url[:200]}...")
    
    # 构建请求头（官方文档中的方式）
    headers = {
        'Content-Type': 'application/json',
        'X-Appid': APPID
    }
    
    # 构建请求体
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
        # 发送请求（使用官方URL参数方式）
        response = requests.post(full_url, headers=headers, json=data, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 官方签名方法成功!")
            result = response.json()
            print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 官方签名方法失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def compare_methods():
    """对比两种签名方法"""
    print("\n=== 方法对比 ===")
    
    # 当前方法（在Header中）
    print("1. 当前方法（Header方式）:")
    date, authorization, host = generate_official_signature()
    
    headers_current = {
        'Content-Type': 'application/json',
        'Host': host,
        'Date': date,
        'Authorization': authorization,
        'X-Appid': os.getenv('OCR_APPID')
    }
    print(f"   Header数量: {len(headers_current)}")
    
    # 官方方法（URL参数方式）
    print("2. 官方方法（URL参数方式）:")
    query_params = {
        'host': host,
        'date': date,
        'authorization': authorization
    }
    full_url = f"{os.getenv('OCR_URL')}?{urllib.parse.urlencode(query_params)}"
    
    headers_official = {
        'Content-Type': 'application/json',
        'X-Appid': os.getenv('OCR_APPID')
    }
    print(f"   Header数量: {len(headers_official)}")
    print(f"   URL参数数量: {len(query_params)}")
    
    return headers_current, headers_official, full_url

def main():
    """主测试函数"""
    print("开始修复OCR API签名算法...")
    
    # 检查配置
    if not all([os.getenv('OCR_APPID'), os.getenv('OCR_API_KEY'), os.getenv('OCR_API_SECRET'), os.getenv('OCR_URL')]):
        print("❌ 配置不完整")
        return
    
    # 对比方法
    headers_current, headers_official, full_url = compare_methods()
    
    # 测试官方方法
    success = test_official_method()
    
    if success:
        print("\n🎯 签名算法修复成功！")
        print("关键修复: 使用URL参数方式而不是Header方式")
    else:
        print("\n⚠️ 官方方法也失败，可能问题在:")
        print("1. API密钥无效")
        print("2. API服务未开通")
        print("3. 其他配置问题")

if __name__ == "__main__":
    main()