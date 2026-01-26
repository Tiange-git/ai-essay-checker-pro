#!/usr/bin/env python3
"""
调试错误代码40303
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

def analyze_error_40303():
    """分析40303错误代码"""
    print("=== 分析错误代码40303 ===")
    
    # 根据讯飞API常见错误代码，40303通常表示：
    print("错误代码40303可能含义:")
    print("1. 图片格式不支持")
    print("2. 图片大小超出限制")
    print("3. 图片数据损坏")
    print("4. API服务未开通或权限不足")
    print("5. 图片编码方式错误")
    
    return True

def test_with_real_image():
    """使用真实图片数据测试"""
    print("\n=== 使用真实图片数据测试 ===")
    
    # 创建一个简单的测试图片（1x1像素的PNG）
    import io
    from PIL import Image
    
    # 创建1x1像素的测试图片
    img = Image.new('RGB', (1, 1), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_data = img_byte_arr.getvalue()
    
    print(f"测试图片大小: {len(img_data)} bytes")
    
    # 生成签名
    API_KEY = os.getenv('OCR_API_KEY')
    API_SECRET = os.getenv('OCR_API_SECRET')
    OCR_URL = os.getenv('OCR_URL')
    
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
    
    # 构建官方格式的请求体
    APPID = os.getenv('OCR_APPID')
    request_body = {
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
                "encoding": "png",  # 使用PNG编码
                "image": base64.b64encode(img_data).decode('utf-8'),
                "status": 3
            }
        }
    }
    
    print("请求体结构:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False)[:500] + "...")
    
    try:
        response = requests.post(full_url, headers=headers, json=request_body, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 使用真实图片测试成功!")
            return True
        else:
            print(f"❌ 测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def check_api_status():
    """检查API服务状态"""
    print("\n=== 检查API服务状态 ===")
    
    # 检查API密钥是否有效
    APPID = os.getenv('OCR_APPID')
    API_KEY = os.getenv('OCR_API_KEY')
    
    print(f"APPID: {APPID}")
    print(f"API_KEY: {API_KEY[:10]}...")
    
    # 错误代码40303通常表示服务未开通或权限问题
    print("\n建议检查:")
    print("1. 讯飞开放平台 - 确认OCR服务已开通")
    print("2. API密钥权限 - 确认密钥有OCR识别权限")
    print("3. 服务配额 - 确认有足够的调用次数")
    print("4. 图片要求 - 确认图片符合API要求")
    
    return True

def main():
    """主测试函数"""
    print("开始调试OCR API错误代码40303...")
    
    # 检查配置
    if not all([os.getenv('OCR_APPID'), os.getenv('OCR_API_KEY'), os.getenv('OCR_API_SECRET'), os.getenv('OCR_URL')]):
        print("❌ 配置不完整")
        return
    
    # 分析错误
    analyze_error_40303()
    
    # 使用真实图片测试
    success = test_with_real_image()
    
    if not success:
        # 检查API状态
        check_api_status()
        
        print("\n⚠️ 错误代码40303通常表示:")
        print("- API服务未开通或权限不足")
        print("- 需要联系讯飞技术支持开通OCR服务")
        print("- 或者API密钥没有OCR识别权限")

if __name__ == "__main__":
    main()