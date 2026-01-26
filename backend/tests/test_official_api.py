#!/usr/bin/env python3
"""
严格按照讯飞官方文档实现OCR API调用
官方文档：https://www.xfyun.cn/doc/words/universal-character-recognition/API.html
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

def generate_signature_wsp():
    """
    生成讯飞WebAPI签名（带动态时间戳）
    官方文档要求：
    - 签名原始字符串：host: {host}\ndate: {date}\nPOST {path} HTTP/1.1
    - HMAC-SHA256算法
    - Base64编码签名结果
    """
    print("=== 生成讯飞官方签名 ===")
    
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    # 解析URL获取host和path
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # 生成RFC1123格式的时间戳
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    
    print(f"host: {host}")
    print(f"path: {path}")
    print(f"date: {date}")
    
    # 构建签名原始字符串
    signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"
    
    print(f"\n签名原始字符串:\n{signature_origin}")
    
    # 使用HMAC-SHA256算法签名
    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    # Base64编码
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    print(f"签名结果: {signature}")
    
    # 构建authorization参数
    authorization_origin = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    print(f"\nauthorization原始字符串: {authorization_origin}")
    print(f"authorization编码后: {authorization}")
    
    return authorization, date, host

def test_official_api():
    """严格按照官方文档测试API调用"""
    print("\n" + "="*60)
    print("=== 严格按照讯飞官方文档测试API调用 ===")
    print("="*60)
    
    # 1. 生成签名
    authorization, date, host = generate_signature_wsp()
    
    # 2. 获取其他配置
    APPID = os.getenv('OCR_APPID')
    OCR_URL = os.getenv('OCR_URL')
    
    print(f"\n=== API配置 ===")
    print(f"APPID: {APPID}")
    print(f"API URL: {OCR_URL}")
    
    # 3. 构建请求头（官方文档要求）
    print(f"\n=== 构建请求头 ===")
    headers = {
        'Content-Type': 'application/json',
        'Host': host,
        'Date': date,
        'Authorization': authorization,
        'X-Appid': APPID
    }
    
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"{key}: {value[:60]}...")
        else:
            print(f"{key}: {value}")
    
    # 4. 构建请求体（官方文档要求）
    print(f"\n=== 构建请求体 ===")
    # 使用一个简单的测试图片
    test_image = base64.b64encode(b"test image data").decode('utf-8')
    
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
    
    print(f"请求体大小: {len(str(data))} 字符")
    print(f"图片数据大小: {len(test_image)} 字符")
    
    # 5. 发送API请求
    print(f"\n=== 发送API请求 ===")
    print(f"请求URL: {OCR_URL}")
    print(f"请求方法: POST")
    print(f"超时时间: 10秒")
    
    try:
        start_time = time.time()
        response = requests.post(OCR_URL, headers=headers, json=data, timeout=10)
        end_time = time.time()
        
        print(f"\n=== API响应 ===")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        # 解析响应
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n✅ API调用成功!")
                print(f"响应数据: {result}")
                
                # 解析识别结果
                if 'payload' in result:
                    text_data = result['payload'].get('recognizeDocumentRes', {}).get('text', '')
                    if text_data:
                        decoded_text = base64.b64decode(text_data).decode('utf-8')
                        print(f"\n识别文本: {decoded_text}")
                
                return True
            except Exception as e:
                print(f"❌ 响应解析失败: {e}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            error_info = response.json() if response.text else {}
            print(f"错误信息: {error_info}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
        return False

def debug_signature():
    """详细调试签名生成过程"""
    print("\n" + "="*60)
    print("=== 详细调试签名生成过程 ===")
    print("="*60)
    
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    print(f"原始配置:")
    print(f"  API_KEY: {API_KEY}")
    print(f"  API_SECRET: {API_SECRET}")
    print(f"  OCR_URL: {OCR_URL}")
    
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    path = parsed_url.path
    
    print(f"\n解析结果:")
    print(f"  host: {host}")
    print(f"  path: {path}")
    
    # 生成时间戳
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    print(f"  date: {date}")
    
    # 构建签名原始字符串
    signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"
    print(f"\n签名原始字符串:")
    print(f"  {signature_origin}")
    print(f"  长度: {len(signature_origin)}")
    
    # HMAC-SHA256签名
    print(f"\nHMAC-SHA256签名:")
    signature_sha = hmac.new(
        API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    print(f"  摘要长度: {len(signature_sha)} bytes")
    print(f"  摘要内容(HEX): {signature_sha.hex()}")
    
    # Base64编码
    signature = base64.b64encode(signature_sha).decode('utf-8')
    print(f"  Base64编码: {signature}")
    print(f"  编码长度: {len(signature)}")
    
    # 构建authorization
    print(f"\n构建authorization:")
    authorization_origin = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    print(f"  原始字符串: {authorization_origin}")
    
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    print(f"  Base64编码: {authorization}")
    print(f"  编码长度: {len(authorization)}")
    
    return authorization, date, host

if __name__ == "__main__":
    print("讯飞OCR API官方文档测试")
    print("官方文档: https://www.xfyun.cn/doc/words/universal-character-recognition/API.html")
    print()
    
    # 调试签名生成
    debug_signature()
    
    # 测试API调用
    success = test_official_api()
    
    if success:
        print("\n🎉  OCR API调用成功!")
    else:
        print("\n❌ OCR API调用失败，请检查:")
        print("1. API密钥是否正确")
        print("2. OCR服务是否已开通")
        print("3. 请求参数是否符合官方文档要求")
        print("4. 网络连接是否正常")