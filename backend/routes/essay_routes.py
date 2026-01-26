from flask import Blueprint, request, jsonify
from services.xunfei_api import XunfeiAPI
from services.file_processor import FileProcessor
from services.history_service import HistoryService
import logging
import os
from werkzeug.utils import secure_filename

# 创建蓝图
essay_routes = Blueprint('essay_routes', __name__)

# 配置日志
logger = logging.getLogger(__name__)

# 初始化讯飞API服务
xunfei_api = XunfeiAPI()
# 初始化文件处理器
file_processor = FileProcessor()
# 初始化历史记录服务
history_service = HistoryService()

# 允许的文件类型
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOC_EXTENSIONS = {'docx'}

# 检查文件扩展名是否允许
def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# 批改作文接口
@essay_routes.route('/check-essay', methods=['POST'])
def check_essay():
    try:
        # 获取请求数据
        data = request.json
        if not data or 'content' not in data:
            return jsonify({'error': '缺少作文内容'}), 400
        
        essay_content = data['content']
        
        # 调用讯飞API进行批改
        result = xunfei_api.check_essay(essay_content)
        
        # 保存到历史记录
        history_service.add_history(essay_content, result, 'text')
        
        return jsonify({'success': True, 'result': result}), 200
        
    except Exception as e:
        logger.error(f'批改作文失败: {str(e)}')
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

# 文件上传接口
@essay_routes.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        # 检查是否有文件被上传
        if 'file' not in request.files:
            return jsonify({'error': '没有文件被上传'}), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 检查文件类型
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        # 根据文件类型处理
        if allowed_file(filename, ALLOWED_DOC_EXTENSIONS):
            # 处理Word文档
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            
            # 解析Word文档
            content = file_processor.process_word(file_path)
            
            # 调用讯飞API进行批改
            result = xunfei_api.check_essay(content)
            
            # 保存到历史记录
            history_service.add_history(content, result, 'word')
            
            # 删除临时文件
            os.remove(file_path)
            
            return jsonify({'success': True, 'result': result, 'content': content}), 200
            
        elif allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS):
            # 处理图片（预留OCR接口）
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            
            # 调用OCR处理（预留接口）
            content = file_processor.process_image(file_path)
            
            # 如果OCR成功，调用讯飞API进行批改
            if content:
                result = xunfei_api.check_essay(content)
                # 保存到历史记录
                history_service.add_history(content, result, 'image')
            else:
                result = {'error': 'OCR处理失败，请手动输入作文内容'}
            
            # 删除临时文件
            os.remove(file_path)
            
            return jsonify({'success': True, 'result': result, 'content': content}), 200
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
        
    except Exception as e:
        logger.error(f'文件上传失败: {str(e)}')
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

# 获取批改历史接口
@essay_routes.route('/history', methods=['GET'])
def get_history():
    try:
        # 获取筛选参数
        filter_type = request.args.get('filter', 'all')
        
        # 验证筛选参数
        valid_filters = ['all', 'today', '3days', 'week']
        if filter_type not in valid_filters:
            filter_type = 'all'
        
        # 获取历史记录
        history = history_service.get_history(filter_type)
        
        return jsonify({
            'success': True, 
            'history': history,
            'filter': filter_type,
            'count': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f'获取历史记录失败: {str(e)}')
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

# 获取单个历史记录详情接口
@essay_routes.route('/history/<int:history_id>', methods=['GET'])
def get_history_detail(history_id):
    try:
        history_item = history_service.get_history_by_id(history_id)
        
        if history_item:
            return jsonify({'success': True, 'history': history_item}), 200
        else:
            return jsonify({'error': '历史记录不存在'}), 404
            
    except Exception as e:
        logger.error(f'获取历史记录详情失败: {str(e)}')
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

# 删除历史记录接口
@essay_routes.route('/history/<int:history_id>', methods=['DELETE'])
def delete_history(history_id):
    try:
        success = history_service.delete_history(history_id)
        
        if success:
            return jsonify({'success': True, 'message': '历史记录已删除'}), 200
        else:
            return jsonify({'error': '历史记录不存在'}), 404
            
    except Exception as e:
        logger.error(f'删除历史记录失败: {str(e)}')
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

# 清空历史记录接口
@essay_routes.route('/history', methods=['DELETE'])
def clear_history():
    try:
        success = history_service.clear_history()
        
        if success:
            return jsonify({'success': True, 'message': '所有历史记录已清空'}), 200
        else:
            return jsonify({'error': '清空历史记录失败'}), 500
            
    except Exception as e:
        logger.error(f'清空历史记录失败: {str(e)}')
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500
