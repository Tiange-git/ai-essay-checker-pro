#!/usr/bin/env python3
"""
测试和对比讯飞OCR API签名算法
"""

import os
import time
import hmac
import hashlib
import base64
import urllib.parse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_current_signature():
    """测试当前签名算法"""
    print("=== 当前签名算法测试 ===")
    
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    # 当前算法
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    request_line = f"POST {parsed_url.path} HTTP/1.1"
    signature_origin = f"host: {host}\ndate: {date}\n{request_line}"
    
    print(f"签名原始字符串:\n{signature_origin}")
    print(f"原始字符串长度: {len(signature_origin)}")
    
    signature_sha = hmac.new(API_SECRET.encode('utf-8'), 
                           signature_origin.encode('utf-8'), 
                           digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    authorization_origin = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    print(f"签名结果: {signature}")
    print(f"认证头长度: {len(authorization)}")
    print(f"认证头前100字符: {authorization[:100]}")
    
    return date, authorization, host

def test_official_signature():
    """测试可能的官方签名算法变体"""
    print("\n=== 尝试官方签名算法变体 ===")
    
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    
    # 变体1: 可能不需要request-line
    signature_origin_v1 = f"host: {host}\ndate: {date}"
    print(f"变体1原始字符串:\n{signature_origin_v1}")
    
    signature_sha_v1 = hmac.new(API_SECRET.encode('utf-8'), 
                              signature_origin_v1.encode('utf-8'), 
                              digestmod=hashlib.sha256).digest()
    signature_v1 = base64.b64encode(signature_sha_v1).decode('utf-8')
    
    authorization_origin_v1 = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date",signature="{signature_v1}"'
    authorization_v1 = base64.b64encode(authorization_origin_v1.encode('utf-8')).decode('utf-8')
    
    print(f"变体1签名: {signature_v1}")
    print(f"变体1认证头长度: {len(authorization_v1)}")
    
    # 变体2: 可能headers顺序不同
    signature_origin_v2 = f"date: {date}\nhost: {host}\nPOST {parsed_url.path} HTTP/1.1"
    print(f"\n变体2原始字符串:\n{signature_origin_v2}")
    
    signature_sha_v2 = hmac.new(API_SECRET.encode('utf-8'), 
                              signature_origin_v2.encode('utf-8'), 
                              digestmod=hashlib.sha256).digest()
    signature_v2 = base64.b64encode(signature_sha_v2).decode('utf-8')
    
    authorization_origin_v2 = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="date host request-line",signature="{signature_v2}"'
    authorization_v2 = base64.b64encode(authorization_origin_v2.encode('utf-8')).decode('utf-8')
    
    print(f"变体2签名: {signature_v2}")
    print(f"变体2认证头长度: {len(authorization_v2)}")
    
    return [
        (signature_origin_v1, signature_v1, authorization_v1),
        (signature_origin_v2, signature_v2, authorization_v2)
    ]

def test_with_real_request():
    """使用不同签名算法测试实际请求"""
    print("\n=== 实际请求测试 ===")
    
    import requests
    import json
    
    APPID = os.getenv('OCR_APPID')
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    # 测试不同的签名算法
    algorithms = [
        ("当前算法", test_current_signature),
    ]
    
    # 添加变体算法
    variants = test_official_signature()
    for i, (origin, signature, auth) in enumerate(variants):
        algorithms.append((f"变体{i+1}", lambda: (time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()), auth, "api.xf-yun.com")))
    
    for name, algo_func in algorithms:
        print(f"\n--- 测试{name} ---")
        try:
            date, authorization, host = algo_func()
            
            headers = {
                'Content-Type': 'application/json',
                'Host': host,
                'Date': date,
                'Authorization': authorization,
                'X-Appid': APPID
            }
            
            # 简单测试数据
            test_image_base64 = base64.b64encode(b"test").decode('utf-8')
            data = {
                "header": {"app_id": APPID, "status": 3},
                "business": {"language": "en", "category": "document"},
                "data": {"image": test_image_base64}
            }
            
            response = requests.post(OCR_URL, headers=headers, json=data, timeout=10)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ {name} 成功!")
                return True
                
        except Exception as e:
            print(f"❌ {name} 失败: {e}")
    
    return False

def check_algorithm_details():
    """检查算法实现细节"""
    print("\n=== 算法细节检查 ===")
    
    API_SECRET = os.getenv('OCR_API_SECRET')
    test_string = "test signature string"
    
    # 检查HMAC实现
    hmac_result = hmac.new(API_SECRET.encode('utf-8'), 
                          test_string.encode('utf-8'), 
                          digestmod=hashlib.sha256).digest()
    
    print(f"HMAC结果长度: {len(hmac_result)} bytes")
    print(f"Base64编码长度: {len(base64.b64encode(hmac_result).decode('utf-8'))}")
    
    # 检查时间格式
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    print(f"时间格式: {date}")
    print(f"时间长度: {len(date)}")

if __name__ == "__main__":
    print("开始测试讯飞OCR API签名算法...")
    
    # 检查配置
    if not all([os.getenv('OCR_APPID'), os.getenv('OCR_API_KEY'), os.getenv('OCR_API_SECRET'), os.getenv('OCR_URL')]):
        print("❌ 配置不完整")
        exit(1)
    
    check_algorithm_details()
    test_current_signature()
    success = test_with_real_request()
    
    if not success:
        print("\n⚠️ 所有算法测试失败，建议:")
        print("1. 检查讯飞官方文档的签名算法")
        print("2. 确认API密钥是否有OCR权限")
        print("3. 联系讯飞技术支持")