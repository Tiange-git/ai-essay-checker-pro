#!/usr/bin/python
# -*- coding: UTF-8 -*-
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests
import os

class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


class universalOcr(object):
    def __init__(self):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret
        self.url = 'http://api.xf-yun.com/v1/private/hh_ocr_recognize_doc'


    def parse_url(self,requset_url):
        stidx = requset_url.index("://")
        host = requset_url[stidx + 3:]
        schema = requset_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise AssembleHeaderException("invalid request url:" + requset_url)
        path = host[edidx:]
        host = host[:edidx]
        u = Url(host, path, schema)
        return u

    def get_body(self, file_path):
        # 将payload中数据替换成实际能力内容，参考不同能力接口文档请求数据中payload
        file = open(file_path, 'rb')
        buf = file.read()
        body = {
            "header": {
                "app_id": self.appid,
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
                    "image": str(base64.b64encode(buf), 'utf-8'),
                    "status": 3
                }
            }
        }
        # print(body)
        return body


# build websocket auth request url
def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = universalOcr.parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    # date = "Mon, 22 Aug 2022 03:26:45 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    print("signature:",signature_sha)
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    print("authorization:",authorization)
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)



def get_result():
    request_url = assemble_ws_auth_url(universalOcr.url, "POST", universalOcr.apikey, universalOcr.apisecret)
    headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'appid': universalOcr.appid}
    print(request_url)
    body = universalOcr.get_body(file_path=file_path)
    response = requests.post(request_url, data=json.dumps(body), headers=headers)
    print(response)
    re = response.content.decode('utf8')
    str_result = json.loads(re)
    print("\nresponse-content:", re)
    if str_result.__contains__('header') and str_result['header']['code'] == 0:
        renew_text = str_result['payload']['recognizeDocumentRes']['text']
        print("\ntext解析结果：", str(base64.b64decode(renew_text), 'utf-8'))


if __name__ == "__main__":
    # 从环境变量读取配置
    from dotenv import load_dotenv
    load_dotenv()
    
    appid = os.getenv('OCR_APPID')
    apisecret = os.getenv('OCR_API_SECRET')
    apikey = os.getenv('OCR_API_KEY')
    file_path = "1.jpg"  # 使用用户指定的图片

    print("=== 讯飞官方demo.py测试 ===")
    print(f"APPID: {appid}")
    print(f"APIKey: {apikey}")
    print(f"APISecret: {apisecret}")
    
    universalOcr = universalOcr()
    get_result()
