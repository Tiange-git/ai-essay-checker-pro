import os
import logging
from docx import Document
from PIL import Image
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests

# 配置日志
logger = logging.getLogger(__name__)

class FileProcessor:
    """文件处理器，用于处理Word文档和图片"""
    
    def process_word(self, file_path):
        """处理Word文档，提取文本内容"""
        try:
            logger.info(f'开始处理Word文档: {file_path}')
            
            # 打开Word文档
            doc = Document(file_path)
            
            # 提取所有段落文本
            content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content.append(paragraph.text)
            
            # 合并文本
            full_content = '\n'.join(content)
            
            logger.info(f'Word文档处理完成，提取到 {len(full_content)} 个字符')
            return full_content
            
        except Exception as e:
            logger.error(f'处理Word文档失败: {str(e)}')
            raise
    
    def process_image(self, file_path):
        """处理图片，提取文本内容（讯飞OCR接口）"""
        try:
            logger.info(f'开始处理图片: {file_path}')
            
            # 验证图片文件
            with Image.open(file_path) as img:
                img.verify()
            
            logger.info(f'图片验证成功: {file_path}')
            
            # ==================== 讯飞OCR API 实现（参考官方demo.py） ====================
            
            # 讯飞OCR API配置 - 从环境变量读取
            APPID = os.getenv('OCR_APPID')
            API_KEY = os.getenv('OCR_API_KEY')
            API_SECRET = os.getenv('OCR_API_SECRET')
            OCR_URL = os.getenv('OCR_URL')
            
            # 验证OCR配置
            if not all([APPID, API_KEY, API_SECRET, OCR_URL]):
                raise ValueError('讯飞OCR API配置不完整，请检查环境变量')
            
            # 1. 读取图片并做base64编码
            with open(file_path, 'rb') as fp:
                image_data = fp.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 2. 生成签名（严格按照官方demo.py方式）
            def generate_signature_demo(api_key, api_secret, request_url):
                """严格按照官方demo.py生成签名"""
                # 解析URL（参考demo.py的parse_url方法）
                stidx = request_url.index("://")
                host = request_url[stidx + 3:]
                edidx = host.index("/")
                path = host[edidx:]
                host = host[:edidx]
                
                # 生成RFC1123格式的时间戳（参考demo.py）
                now = datetime.now()
                date = format_date_time(mktime(now.timetuple()))
                
                # 构建签名原始字符串
                signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"
                
                # HMAC-SHA256签名
                signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), 
                                        digestmod=hashlib.sha256).digest()
                signature = base64.b64encode(signature_sha).decode('utf-8')
                
                # 构建authorization（参考demo.py的assemble_ws_auth_url）
                authorization_origin = f'api_key="{api_key}",algorithm="hmac-sha256",headers="host date request-line",signature="{signature}"'
                authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
                
                return authorization, date, host
            
            # 生成签名
            authorization, date, host = generate_signature_demo(API_KEY, API_SECRET, OCR_URL)
            
            # 3. 构建请求URL（参考demo.py：鉴权参数放入URL查询参数）
            auth_url = OCR_URL + "?" + urlencode({
                "host": host,
                "date": date,
                "authorization": authorization
            })
            
            # 4. 构建请求头（参考demo.py：使用小写header名）
            headers = {
                'content-type': "application/json",  # 注意：小写
                'host': host,                        # 注意：host在header中
                'appid': APPID                       # 注意：不是X-Appid
            }
            
            # 5. 构建请求体（参考demo.py：使用parameter和payload结构）
            data = {
                "header": {
                    "app_id": APPID,  # 注意：使用app_id
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
                        "image": image_base64,
                        "status": 3
                    }
                }
            }
            
            # 6. 发送请求（使用auth_url，参考demo.py的get_result函数）
            logger.info(f'开始调用讯飞OCR API，请求URL: {auth_url}')
            logger.info(f'请求头: {headers}')
            logger.info(f'图片base64长度: {len(image_base64)} 字符')
            
            # 发送POST请求（参考demo.py：使用data=json.dumps()，增加超时时间）
            response = requests.post(auth_url, data=json.dumps(data), headers=headers, timeout=60)

            # 7. 解析响应（参考demo.py的get_result函数）
            logger.info(f'响应状态码: {response.status_code}')
            logger.info(f'响应内容: {response.text}')
            
            # 解析JSON响应
            re = response.content.decode('utf8')
            str_result = json.loads(re)
            logger.info(f'格式化响应: {json.dumps(str_result, ensure_ascii=False, indent=2)}')
            
            # 提取OCR结果（参考demo.py的解析逻辑）
            content = None
            if str_result.__contains__('header') and str_result['header']['code'] == 0:
                # 从payload中获取Base64编码的识别结果
                renew_text = str_result['payload']['recognizeDocumentRes']['text']
                # 对结果进行Base64解码
                decoded_result = str(base64.b64decode(renew_text), 'utf-8')
                logger.info(f'Base64解码后的识别结果: {decoded_result}')
                
                # 解析JSON格式的识别结果
                ocr_result = json.loads(decoded_result)
                
                # 提取全文文本
                content = ocr_result.get('whole_text', '')
                logger.info(f'OCR识别成功，提取到 {len(content)} 个字符：{content[:50]}...')
            else:
                logger.error(f'OCR调用失败，错误码: {str_result.get("header", {}).get("code")}, 错误信息: {str_result.get("header", {}).get("message")}')
            
            return content
            
        except Exception as e:
            logger.error(f'处理图片/OCR调用异常: {str(e)}', exc_info=True)
            return None


