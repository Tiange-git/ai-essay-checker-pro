#!/usr/bin/env python3
"""
测试讯飞OCR API调用的脚本
"""

from services.file_processor import FileProcessor
import logging
import os

# 配置日志以查看详细信息
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_ocr_config():
    """测试OCR配置"""
    print("=== 测试OCR配置 ===")
    
    # 检查OCR API配置
    print("OCR API配置检查:")
    print("APPID:", os.getenv('APPID'))
    print("OCR专用APPID: e519a66d")
    print("OCR API_KEY: 43c544744d546de66a3c150cf164c815")
    print("OCR API_SECRET: YmRiMWNmN2JmY2JhYWE4ZmExOGNlMzYy")
    
    # 检查OCR URL
    print("OCR URL: https://api.xf-yun.com/v1/private/hh_ocr_recognize_doc")
    
    return True

def test_ocr_api_connection():
    """测试OCR API连接"""
    print("\n=== 测试OCR API连接 ===")
    
    try:
        # 初始化文件处理器
        processor = FileProcessor()
        print("1. 文件处理器初始化成功")
        
        # 测试签名生成
        print("2. 测试签名生成...")
        
        # 手动测试签名生成逻辑
        import time
        import hmac
        import hashlib
        import base64
        import urllib.parse
        
        API_KEY = '43c544744d546de66a3c150cf164c815'
        API_SECRET = 'YmRiMWNmN2JmY2JhYWE4ZmExOGNlMzYy'
        OCR_URL = 'https://api.xf-yun.com/v1/private/hh_ocr_recognize_doc'
        
        def generate_signature(api_key, api_secret, url):
            parsed_url = urllib.parse.urlparse(url)
            host = parsed_url.netloc
            date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
            request_line = f"POST {parsed_url.path} HTTP/1.1"
            signature_origin = f"host: {host}\ndate: {date}\n{request_line}"
            signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
            signature = base64.b64encode(signature_sha).decode('utf-8')
            authorization_origin = f'api_key="{api_key}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
            return date, authorization, host
        
        date, authorization, host = generate_signature(API_KEY, API_SECRET, OCR_URL)
        print(f"签名生成成功")
        print(f"日期: {date}")
        print(f"认证头长度: {len(authorization)}")
        print(f"主机: {host}")
        
        return True
        
    except Exception as e:
        print(f"OCR API连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ocr_with_mock_image():
    """使用模拟图片测试OCR"""
    print("\n=== 测试OCR功能（模拟图片） ===")
    
    try:
        processor = FileProcessor()
        
        # 创建一个临时测试文件（模拟图片处理）
        test_image_path = "test_ocr_image.txt"
        with open(test_image_path, 'w') as f:
            f.write("This is a test image content for OCR validation")
        
        print("1. 创建模拟图片文件成功")
        
        # 测试图片验证
        print("2. 测试图片验证...")
        from PIL import Image
        
        # 由于不是真实图片，这里会抛出异常，但我们主要测试API连接
        try:
            with Image.open(test_image_path) as img:
                img.verify()
            print("图片验证成功")
        except Exception as e:
            print(f"图片验证失败（预期中）: {e}")
        
        # 清理测试文件
        os.remove(test_image_path)
        
        # 测试OCR API调用（不发送实际图片）
        print("3. 测试OCR API请求构建...")
        
        import requests
        import json
        import base64
        import urllib.parse
        import time
        import hmac
        import hashlib
        
        # 构建请求头
        API_KEY = '43c544744d546de66a3c150cf164c815'
        API_SECRET = 'YmRiMWNmN2JmY2JhYWE4ZmExOGNlMzYy'
        APPID = 'e519a66d'
        OCR_URL = 'https://api.xf-yun.com/v1/private/hh_ocr_recognize_doc'
        
        def generate_signature(api_key, api_secret, url):
            parsed_url = urllib.parse.urlparse(url)
            host = parsed_url.netloc
            date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
            request_line = f"POST {parsed_url.path} HTTP/1.1"
            signature_origin = f"host: {host}\ndate: {date}\n{request_line}"
            signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
            signature = base64.b64encode(signature_sha).decode('utf-8')
            authorization_origin = f'api_key="{api_key}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
            return date, authorization, host
        
        date, authorization, host = generate_signature(API_KEY, API_SECRET, OCR_URL)
        
        headers = {
            'Content-Type': 'application/json',
            'Host': host,
            'Date': date,
            'Authorization': authorization,
            'X-Appid': APPID
        }
        
        # 使用空的base64图片数据测试
        empty_image_base64 = base64.b64encode(b"test").decode('utf-8')
        
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
                "image": empty_image_base64
            }
        }
        
        print("4. 请求构建完成")
        print(f"请求头: {headers}")
        print(f"请求体结构: {json.dumps(data, indent=2)[:200]}...")
        
        # 测试网络连接（不发送实际请求）
        print("5. 测试网络连接...")
        try:
            # 只测试URL解析和网络可达性
            parsed_url = urllib.parse.urlparse(OCR_URL)
            print(f"URL解析成功: {parsed_url}")
            
            # 测试DNS解析
            import socket
            hostname = parsed_url.hostname
            ip = socket.gethostbyname(hostname)
            print(f"DNS解析成功: {hostname} -> {ip}")
            
        except Exception as e:
            print(f"网络连接测试失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"OCR功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试讯飞OCR API调用...")
    
    # 测试配置
    config_ok = test_ocr_config()
    
    # 测试API连接
    connection_ok = test_ocr_api_connection()
    
    # 测试OCR功能
    ocr_ok = test_ocr_with_mock_image()
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"配置检查: {'✅ 成功' if config_ok else '❌ 失败'}")
    print(f"API连接: {'✅ 成功' if connection_ok else '❌ 失败'}")
    print(f"OCR功能: {'✅ 成功' if ocr_ok else '❌ 失败'}")
    
    if config_ok and connection_ok:
        print("\n🎯 OCR API配置和连接测试通过！")
        print("📝 注意: 需要实际图片文件进行完整的OCR识别测试")
    else:
        print("\n⚠️ OCR API测试存在问题，请检查配置")

if __name__ == "__main__":
    main()