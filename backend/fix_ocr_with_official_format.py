#!/usr/bin/env python3
"""
根据官方文档修复OCR API请求体格式
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
    """生成官方签名"""
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
    
    return date, authorization, host

def build_official_request_body(image_data):
    """根据官方文档构建请求体"""
    APPID = os.getenv('OCR_APPID')
    
    # 构建符合官方文档的请求体
    request_body = {
        "header": {
            "app_id": APPID,
            "status": 3  # 一次传完
        },
        "parameter": {
            "hh_ocr_recognize_doc": {
                "recognizeDocumentRes": {  # 注意：这里是recognizeDocumentRes不是recognize_doc_res
                    "encoding": "utf8",
                    "compress": "raw", 
                    "format": "json"
                }
            }
        },
        "payload": {
            "image": {
                "encoding": "jpg",  # 图片编码方式
                "image": base64.b64encode(image_data).decode('utf-8'),  # Base64编码的图片数据
                "status": 3  # 一次传完
            }
        }
    }
    
    return request_body

def test_official_format():
    """测试官方格式"""
    print("=== 测试官方请求体格式 ===")
    
    APPID = os.getenv('OCR_APPID')
    OCR_URL = os.getenv('OCR_URL')
    
    # 生成签名
    date, authorization, host = generate_official_signature()
    
    # 构建URL参数
    query_params = {'host': host, 'date': date, 'authorization': authorization}
    full_url = f"{OCR_URL}?{urllib.parse.urlencode(query_params)}"
    
    headers = {'Content-Type': 'application/json'}
    
    # 使用测试图片数据
    test_image_data = b"test_image_content"  # 简单的测试数据
    
    # 构建官方格式的请求体
    request_body = build_official_request_body(test_image_data)
    
    print("请求体结构:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(full_url, headers=headers, json=request_body, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 官方格式调用成功!")
            result = response.json()
            
            # 解析返回结果
            if result.get('header', {}).get('code') == 0:
                text_data = result.get('payload', {}).get('recognizeDocumentRes', {}).get('text', '')
                if text_data:
                    # Base64解码text字段
                    decoded_text = base64.b64decode(text_data).decode('utf-8')
                    print("解码后的文本数据:")
                    print(json.dumps(json.loads(decoded_text), indent=2, ensure_ascii=False))
            
            return True
        else:
            print(f"❌ 调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def update_file_processor():
    """更新file_processor.py中的OCR方法"""
    print("\n=== 更新file_processor.py ===")
    
    file_path = "services/file_processor.py"
    
    # 读取当前文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到OCR处理部分并替换
    old_ocr_section = '''            # 4. 构建正确的请求体（核心修改：按接口规范的层级结构）
            data = {
                "header": {
                    "app_id": APPID,  # 必须传入AppID
                    "status": 3
                },
                "business": {
                    "language": "en",  # 语言类型（英语）
                    "category": "document"  # 识别场景（document表示文档）
                },
                "data": {
                    "image": image_base64  # 图片base64放在data层级下（不再是顶级字段）
                }
            }'''
    
    new_ocr_section = '''            # 4. 构建正确的请求体（根据官方文档）
            data = {
                "header": {
                    "app_id": APPID,  # 必须传入AppID
                    "status": 3  # 一次传完
                },
                "parameter": {
                    "hh_ocr_recognize_doc": {
                        "recognizeDocumentRes": {  # 注意字段名
                            "encoding": "utf8",
                            "compress": "raw",
                            "format": "json"
                        }
                    }
                },
                "payload": {
                    "image": {
                        "encoding": "jpg",  # 图片编码方式
                        "image": image_base64,  # Base64编码的图片数据
                        "status": 3  # 一次传完
                    }
                }
            }'''
    
    # 替换内容
    if old_ocr_section in content:
        content = content.replace(old_ocr_section, new_ocr_section)
        
        # 写入更新后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ file_processor.py已更新")
        return True
    else:
        print("❌ 未找到需要替换的代码段")
        return False

def main():
    """主测试函数"""
    print("开始修复OCR API请求体格式...")
    
    # 检查配置
    if not all([os.getenv('OCR_APPID'), os.getenv('OCR_API_KEY'), os.getenv('OCR_API_SECRET'), os.getenv('OCR_URL')]):
        print("❌ 配置不完整")
        return
    
    # 测试官方格式
    success = test_official_format()
    
    if success:
        print("\n🎯 官方格式测试成功！")
        
        # 更新file_processor.py
        if update_file_processor():
            print("✅ 系统已修复完成，可以重新启动测试OCR功能")
        else:
            print("⚠️ 文件更新失败，需要手动修复")
    else:
        print("\n⚠️ 官方格式测试失败，可能API密钥或服务有问题")

if __name__ == "__main__":
    main()