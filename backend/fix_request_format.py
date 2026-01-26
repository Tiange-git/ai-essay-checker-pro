#!/usr/bin/env python3
"""
修复OCR API请求体格式问题
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

def test_different_request_formats():
    """测试不同的请求体格式"""
    print("=== 测试不同的请求体格式 ===")
    
    APPID = os.getenv('OCR_APPID')
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
    # 生成签名
    parsed_url = urllib.parse.urlparse(OCR_URL)
    host = parsed_url.netloc
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    request_line = f"POST {parsed_url.path} HTTP/1.1"
    signature_origin = f"host: {host}\ndate: {date}\n{request_line}"
    
    signature_sha = hmac.new(API_SECRET.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    authorization_origin = f'api_key="{API_KEY}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    # 构建URL参数
    query_params = {'host': host, 'date': date, 'authorization': authorization}
    full_url = f"{OCR_URL}?{urllib.parse.urlencode(query_params)}"
    
    headers = {'Content-Type': 'application/json'}
    
    # 测试不同的请求体格式
    test_formats = [
        {
            'name': '格式1 - 简化结构',
            'data': {
                "image": base64.b64encode(b"test").decode('utf-8'),
                "language": "en"
            }
        },
        {
            'name': '格式2 - 平铺结构',
            'data': {
                "app_id": APPID,
                "image": base64.b64encode(b"test").decode('utf-8'),
                "language": "en",
                "category": "document"
            }
        },
        {
            'name': '格式3 - 官方示例结构',
            'data': {
                "header": {
                    "app_id": APPID,
                    "status": 3
                },
                "parameter": {
                    "hh_ocr_recognize_doc": {
                        "recognize_doc_res": {
                            "encoding": "utf8",
                            "compress": "raw",
                            "format": "json"
                        }
                    }
                },
                "payload": {
                    "input": {
                        "encoding": "utf8",
                        "status": 3,
                        "image": base64.b64encode(b"test").decode('utf-8')
                    }
                }
            }
        },
        {
            'name': '格式4 - 更简化的header结构',
            'data': {
                "header": {
                    "app_id": APPID
                },
                "parameter": {
                    "language": "en",
                    "category": "document"
                },
                "payload": {
                    "image": base64.b64encode(b"test").decode('utf-8')
                }
            }
        }
    ]
    
    for format_info in test_formats:
        print(f"\n--- 测试{format_info['name']} ---")
        print(f"请求体: {json.dumps(format_info['data'], indent=2)[:300]}...")
        
        try:
            response = requests.post(full_url, headers=headers, json=format_info['data'], timeout=10)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ 格式正确!")
                result = response.json()
                print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True, format_info['name']
            elif response.status_code == 400:
                # 分析错误信息
                error_info = response.json()
                print(f"❌ 格式错误: {error_info.get('header', {}).get('message', '未知错误')}")
            else:
                print(f"⚠️ 其他错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    return False, None

def check_api_documentation():
    """根据错误信息推测正确的格式"""
    print("\n=== 分析错误信息 ===")
    print("错误信息: '$.business' unknown field; '$.data' unknown field;")
    print("说明: API不接受 'business' 和 'data' 字段")
    print("\n推测正确的字段名可能是:")
    print("1. 'parameter' 替代 'business'")
    print("2. 'payload' 替代 'data'")
    print("3. 可能需要特定的子字段结构")

def main():
    """主测试函数"""
    print("开始修复OCR API请求体格式...")
    
    # 检查配置
    if not all([os.getenv('OCR_APPID'), os.getenv('OCR_API_KEY'), os.getenv('OCR_API_SECRET'), os.getenv('OCR_URL')]):
        print("❌ 配置不完整")
        return
    
    # 分析错误信息
    check_api_documentation()
    
    # 测试不同格式
    success, correct_format = test_different_request_formats()
    
    if success:
        print(f"\n🎯 请求体格式修复成功！正确格式: {correct_format}")
    else:
        print("\n⚠️ 需要查阅官方API文档获取正确的请求体格式")
        print("建议查看讯飞OCR API的完整接口文档")

if __name__ == "__main__":
    main()