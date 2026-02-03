import os
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import websocket
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

class XunfeiAPI:
    def __init__(self):
        # 从环境变量获取API配置
        self.appid = os.getenv('APPID')
        self.api_key = os.getenv('APIKey')
        self.api_secret = os.getenv('APISecret')
        
        if not all([self.appid, self.api_key, self.api_secret]):
            raise ValueError('讯飞星火API配置不完整')
        
        # API端点 - Spark X1.5模型
        self.host = 'spark-api.xf-yun.com'
        self.path = '/v4.0/chat'
        self.port = 443
    
    def _generate_signature(self):
        """生成WebSocket签名"""
        # 生成时间戳
        date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
        
        # 构建签名字符串
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        
        # 使用API密钥生成签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        # 对签名进行base64编码
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        # 构建认证头
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        return date, authorization
    
    def _build_ws_url(self):
        """构建WebSocket连接URL"""
        date, authorization = self._generate_signature()
        
        # 构建查询参数
        query = {
            'authorization': authorization,
            'date': date,
            'host': self.host
        }
        
        # 构建完整的WebSocket URL
        ws_url = f"wss://{self.host}:{self.port}{self.path}?{urllib.parse.urlencode(query)}"
        return ws_url
    
    def _send_message(self, ws, message):
        """发送消息到WebSocket"""
        ws.send(json.dumps(message))
    
    def _receive_message(self, ws, timeout=30):
        """从WebSocket接收消息"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                logger.debug('尝试接收WebSocket消息...')
                message = ws.recv()
                logger.info(f'接收到WebSocket消息，长度: {len(message)}')
                logger.debug(f'消息内容: {message[:1000]}...')
                
                # 尝试解析JSON
                try:
                    parsed_message = json.loads(message)
                    logger.info('JSON解析成功')
                    return parsed_message
                except json.JSONDecodeError as e:
                    logger.error(f'JSON解析错误: {str(e)}')
                    logger.error(f'原始消息: {message}')
                    # 即使JSON解析失败，也返回原始消息
                    return {'raw_message': message}
            except websocket.WebSocketTimeoutException:
                logger.debug('WebSocket接收超时，继续等待')
                continue
            except Exception as e:
                logger.error(f'接收消息时发生错误: {str(e)}')
                continue
        raise TimeoutError('WebSocket接收消息超时')
    
    def check_essay(self, content):
        """使用讯飞Spark Max API批改作文"""
        try:
            logger.info(f'开始调用讯飞Spark Max API批改作文，内容长度: {len(content)}')
            
            # 构建WebSocket URL
            ws_url = self._build_ws_url()
            logger.info(f'WebSocket URL: {ws_url}')
            
            # 连接WebSocket
            ws = websocket.create_connection(ws_url, timeout=10)
            logger.info('WebSocket连接成功')
            
            # 构建请求数据
            request_data = {
                "header": {
                    "app_id": self.appid,
                    "uid": "user123"
                },
                "parameter": {
                    "chat": {
                        "domain": "4.0Ultra",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                },
                "payload": {
                    "message": {
                        "text": [
                            {
                                "role": "user",
                                "content": f"请批改以下英语作文，要求：\n1. 指出所有语法错误，包括拼写、标点、时态、主谓一致等问题\n2. 对每个错误提供详细的修改建议和解释\n3. 以JSON格式返回详细错误列表，每个错误包含original（原始文本）、corrected（修改后文本）、error_type（错误类型）、explanation（解释）字段\n4. 提供修改后的完整文本\n5. 给出评分和改进建议\n\n作文内容：\n{content}"
                            }
                        ]
                    }
                }
            }
            
            # 发送请求
            self._send_message(ws, request_data)
            logger.info('请求发送成功')
            
            # 接收响应
            responses = []
            while True:
                response = self._receive_message(ws)
                responses.append(response)
                logger.debug(f'收到响应: {json.dumps(response, ensure_ascii=False)}')
                
                # 检查是否收到最终响应
                if response.get('header', {}).get('status') == 2:
                    logger.info('收到最终响应')
                    break
            
            # 关闭WebSocket连接
            ws.close()
            logger.info('WebSocket连接关闭')
            
            # 处理响应数据
            result = self._process_response(responses)
            logger.info(f'API调用完成，结果: {json.dumps(result, ensure_ascii=False)}')
            return result
            
        except Exception as e:
            logger.error(f'调用讯飞Spark Max API失败: {str(e)}')
            # 返回默认结果
            return {
                "feedback": "",
                "suggestions": ["增强论点的说服力", "改善句子结构多样性", "增加具体例子"],
                "grammar_errors": ["时态使用不当", "主谓一致问题", "拼写错误"],
                "detailed_errors": [],
                "corrected_text": ""
            }
    
    def _process_response(self, responses):
        """处理API响应数据"""
        # 打印响应列表长度和内容，用于调试
        logger.info(f'收到的响应数量: {len(responses)}')
        if responses:
            logger.info(f'第一个响应的结构: {json.dumps(responses[0], ensure_ascii=False)[:500]}...')
        
        # 提取所有文本响应
        text_responses = []
        for i, response in enumerate(responses):
            logger.info(f'处理第 {i+1} 个响应')
            # 检查响应结构
            payload = response.get('payload', {})
            logger.info(f'响应 {i+1} 的payload: {json.dumps(payload, ensure_ascii=False)[:300]}...')
            
            choices = payload.get('choices', {})
            logger.info(f'响应 {i+1} 的choices: {json.dumps(choices, ensure_ascii=False)[:300]}...')
            
            # 尝试不同的文本提取方式
            text = []
            if isinstance(choices, dict):
                # 标准结构
                text = choices.get('text', [])
            elif isinstance(choices, list):
                # 可能的列表结构
                text = choices
            
            logger.info(f'响应 {i+1} 中的文本数量: {len(text)}')
            
            for item in text:
                logger.info(f'文本项: {json.dumps(item, ensure_ascii=False)}')
                # 尝试不同的角色检查方式
                role = item.get('role', '')
                content = item.get('content', '')
                
                # 如果找到内容，无论角色如何，都添加到响应中
                if content:
                    text_responses.append(content)
                    logger.info(f'添加内容: "{content[:100]}..."')
        
        # 合并响应文本
        full_response = ''.join(text_responses)
        logger.info(f'合并后的响应文本长度: {len(full_response)}')
        logger.info(f'合并后的响应文本: "{full_response[:200]}..."')
        
        # 如果没有提取到内容，尝试从响应的其他部分提取
        if not full_response:
            logger.warning('没有从响应中提取到内容，尝试其他方式')
            for response in responses:
                # 尝试直接从payload中提取
                payload = response.get('payload', {})
                if isinstance(payload, str):
                    text_responses.append(payload)
                    logger.info(f'从payload中提取内容: "{payload[:100]}..."')
                
                # 尝试从message中提取
                message = payload.get('message', {})
                if isinstance(message, dict):
                    msg_text = message.get('text', [])
                    for item in msg_text:
                        if isinstance(item, dict):
                            content = item.get('content', '')
                            if content:
                                text_responses.append(content)
                                logger.info(f'从message中提取内容: "{content[:100]}..."')
                elif isinstance(message, list):
                    for item in message:
                        if isinstance(item, dict):
                            content = item.get('content', '')
                            if content:
                                text_responses.append(content)
                                logger.info(f'从message列表中提取内容: "{content[:100]}..."')
        
        # 重新合并响应文本
        full_response = ''.join(text_responses)
        logger.info(f'最终响应文本长度: {len(full_response)}')
        logger.info(f'最终响应文本: "{full_response[:200]}..."')
        
        # 尝试解析JSON格式的响应
        try:
            import json
            json_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', full_response)
            if json_block_match:
                json_str = json_block_match.group(1)
                logger.info(f'找到JSON块，长度: {len(json_str)}')
                logger.info(f'JSON内容前200字符: {json_str[:200]}...')
                
                json_content = json.loads(json_str)
                logger.info(f'成功解析JSON响应，类型: {type(json_content)}')
                logger.info(f'JSON键: {json_content.keys() if isinstance(json_content, dict) else "N/A"}')
                
                # 检查是否包含errors字段
                if isinstance(json_content, dict) and 'errors' in json_content:
                    result = {
                        'feedback': '',
                        'suggestions': json_content.get('improvement_suggestions', []),
                        'grammar_errors': [],
                        'detailed_errors': json_content.get('errors', []),
                        'corrected_text': json_content.get('corrected_text', '')
                    }
                    logger.info(f'从JSON中提取结果成功: errors={len(result["detailed_errors"])}, suggestions={len(result["suggestions"])}, corrected_text长度={len(result["corrected_text"])}')
                    return result
                else:
                    logger.warning(f'JSON中不包含errors字段，使用文本解析方式')
            else:
                logger.warning(f'未找到JSON块，使用文本解析方式')
        except Exception as e:
            logger.warning(f'JSON解析失败: {str(e)}，使用文本解析方式')
        
        # 构建结果（移除评分模块）
        result = {
            'feedback': full_response,
            'suggestions': self._extract_suggestions(full_response),
            'grammar_errors': self._extract_grammar_errors(full_response),
            'detailed_errors': self._extract_detailed_errors(full_response),
            'corrected_text': self._generate_corrected_text(full_response)
        }
        logger.info(f'使用文本解析方式提取结果: feedback长度={len(result["feedback"])}, suggestions={len(result["suggestions"])}, grammar_errors={len(result["grammar_errors"])}, detailed_errors={len(result["detailed_errors"])}, corrected_text长度={len(result["corrected_text"])}')
        return result
    

    
    def _extract_suggestions(self, response):
        """从响应中提取改进建议"""
        # 尝试从响应中提取改进建议
        import re
        suggestions_match = re.search(r'改进建议[:：]\s*([\s\S]*?)(?=详细错误分析|修改后的文本|$)', response)
        if suggestions_match:
            suggestions_text = suggestions_match.group(1)
            # 分割建议并清理
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
            return suggestions[:3]  # 最多返回3条建议
        # 返回默认建议
        return ['增强论点的说服力', '改善句子结构多样性', '增加具体例子']
    
    def _extract_grammar_errors(self, response):
        """从响应中提取语法错误"""
        # 尝试从响应中提取语法错误
        import re
        errors_match = re.search(r'语法错误[:：]\s*([\s\S]*?)(?=详细错误分析|修改后的文本|$)', response)
        if errors_match:
            errors_text = errors_match.group(1)
            # 分割错误并清理
            errors = [e.strip() for e in errors_text.split('\n') if e.strip()]
            return errors[:3]  # 最多返回3条错误
        # 返回默认错误
        return ['时态使用不当', '主谓一致问题']
    
    def _extract_detailed_errors(self, response):
        """从响应中提取详细的错误信息"""
        # 尝试从响应中提取详细错误信息
        import re
        import json
        
        logger.info(f'开始提取详细错误信息，响应长度: {len(response)}')
        
        # 尝试匹配JSON格式的详细错误信息
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                json_content = json.loads(json_match.group(1))
                # 检查JSON结构，处理不同格式
                if isinstance(json_content, list):
                    # 直接是错误列表
                    logger.info(f'成功从JSON中提取详细错误信息，数量: {len(json_content)}')
                    return json_content[:5]  # 最多返回5个详细错误
                elif isinstance(json_content, dict) and 'errors' in json_content:
                    # 包含errors字段的JSON
                    errors = json_content['errors']
                    if isinstance(errors, list):
                        logger.info(f'成功从JSON的errors字段中提取详细错误信息，数量: {len(errors)}')
                        return errors[:5]  # 最多返回5个详细错误
                elif isinstance(json_content, dict):
                    # 单个错误对象
                    logger.info('成功从JSON中提取单个错误信息')
                    return [json_content]
            except json.JSONDecodeError as e:
                logger.error(f'JSON解析错误: {str(e)}')
        
        # 尝试匹配非JSON格式的详细错误信息
        errors_match = re.search(r'详细错误分析[:：]\s*([\s\S]*?)(?=修改后的文本|$)', response)
        if errors_match:
            errors_text = errors_match.group(1)
            logger.info(f'成功匹配详细错误分析文本，长度: {len(errors_text)}')
            
            # 解析非JSON格式的错误信息
            error_items = []
            # 尝试按行解析错误信息
            lines = errors_text.strip().split('\n')
            current_error = {}
            
            for line in lines:
                line = line.strip()
                if '原始:' in line:
                    current_error['original'] = line.split('原始:', 1)[1].strip()
                elif '修改:' in line:
                    current_error['corrected'] = line.split('修改:', 1)[1].strip()
                elif '类型:' in line:
                    current_error['error_type'] = line.split('类型:', 1)[1].strip()
                elif '解释:' in line:
                    current_error['explanation'] = line.split('解释:', 1)[1].strip()
                    # 当收集到完整的错误信息时，添加到列表
                    if all(key in current_error for key in ['original', 'corrected', 'error_type', 'explanation']):
                        error_items.append(current_error.copy())
                        current_error = {}
            
            if error_items:
                logger.info(f'成功解析非JSON格式错误信息，数量: {len(error_items)}')
                return error_items[:5]
        
        # 尝试匹配其他格式的错误信息
        # 查找所有可能的错误对
        error_pairs = re.findall(r'(.*?)[→→](.*?)[\n\r]', response)
        if error_pairs:
            error_items = []
            for i, (original, corrected) in enumerate(error_pairs[:5]):
                error_items.append({
                    'original': original.strip(),
                    'corrected': corrected.strip(),
                    'error_type': '语法错误',
                    'explanation': '需要修改的语法问题'
                })
            logger.info(f'成功匹配错误对，数量: {len(error_items)}')
            return error_items
        
        # 如果没有找到任何错误信息，返回空列表
        logger.warning('未能从响应中提取详细错误信息')
        return []
    
    def _generate_corrected_text(self, response):
        """生成修改后的文本"""
        # 尝试从响应中提取修改后的文本
        import re
        
        logger.info('开始提取修改后的文本')
        
        # 尝试匹配修改后的文本（中文格式）
        # 匹配"修改后的文本"或"修改后的完整文本"
        corrected_match = re.search(r'修改后的(?:完整)?文本[:：]\s*([\s\S]*?)(?=\d+\.|详细错误分析|评分|改进建议|$)', response)
        if corrected_match:
            corrected_text = corrected_match.group(1).strip()
            if corrected_text:
                # 去除可能的Markdown格式标签
                corrected_text = re.sub(r'```json\s*([\s\S]*?)\s*```', '', corrected_text)
                corrected_text = re.sub(r'```\s*([\s\S]*?)\s*```', '', corrected_text)
                corrected_text = corrected_text.strip()
                if corrected_text:
                    logger.info(f'成功提取修改后的文本，长度: {len(corrected_text)}')
                    return corrected_text
        
        # 尝试匹配其他格式的修改后文本
        other_match = re.search(r'修正后[:：]\s*([\s\S]*?)(?=\n\n|评分|改进建议|$)', response)
        if other_match:
            corrected_text = other_match.group(1).strip()
            if corrected_text:
                # 去除可能的Markdown格式标签
                corrected_text = re.sub(r'```json\s*([\s\S]*?)\s*```', '', corrected_text)
                corrected_text = re.sub(r'```\s*([\s\S]*?)\s*```', '', corrected_text)
                corrected_text = corrected_text.strip()
                if corrected_text:
                    logger.info(f'成功提取其他格式的修改后文本，长度: {len(corrected_text)}')
                    return corrected_text
        
        # 尝试从JSON中提取corrected_text字段
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                import json
                json_content = json.loads(json_match.group(1))
                if isinstance(json_content, dict) and 'corrected_text' in json_content:
                    corrected_text = json_content['corrected_text']
                    if corrected_text:
                        logger.info(f'成功从JSON中提取corrected_text，长度: {len(corrected_text)}')
                        return corrected_text
            except json.JSONDecodeError:
                pass
        
        # 如果没有找到修改后的文本，返回空字符串
        logger.warning('未能从响应中提取修改后的文本')
        return ''  # 返回空字符串而不是响应的一部分

