import json
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HistoryService:
    def __init__(self, storage_file='history.json'):
        self.storage_file = os.path.join(os.path.dirname(__file__), '..', storage_file)
        self.history = self._load_history()
    
    def _load_history(self):
        """从文件加载历史记录"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据是列表格式
                    if isinstance(data, list):
                        return data
                    else:
                        return []
            else:
                return []
        except Exception as e:
            logger.error(f'加载历史记录失败: {str(e)}')
            return []
    
    def _save_history(self):
        """保存历史记录到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f'保存历史记录失败: {str(e)}')
    
    def add_history(self, content, result, input_type='text'):
        """添加历史记录"""
        try:
            history_item = {
                'id': len(self.history) + 1,
                'content': content,
                'result': result,
                'type': input_type,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.history.append(history_item)
            self._save_history()
            
            logger.info(f'历史记录已添加，ID: {history_item["id"]}')
            return history_item
        except Exception as e:
            logger.error(f'添加历史记录失败: {str(e)}')
            return None
    
    def get_history(self, filter_type='all'):
        """获取历史记录，支持按时间筛选"""
        try:
            now = datetime.now()
            filtered_history = []
            
            for item in self.history:
                created_at = datetime.strptime(item['created_at'], '%Y-%m-%d %H:%M:%S')
                time_diff = now - created_at
                
                if filter_type == 'today' and time_diff.days == 0:
                    filtered_history.append(item)
                elif filter_type == '3days' and time_diff.days <= 3:
                    filtered_history.append(item)
                elif filter_type == 'week' and time_diff.days <= 7:
                    filtered_history.append(item)
                elif filter_type == 'all':
                    filtered_history.append(item)
            
            # 按时间倒序排列
            filtered_history.sort(key=lambda x: x['created_at'], reverse=True)
            
            return filtered_history
        except Exception as e:
            logger.error(f'获取历史记录失败: {str(e)}')
            return []
    
    def get_history_by_id(self, history_id):
        """根据ID获取历史记录"""
        try:
            for item in self.history:
                if item['id'] == history_id:
                    return item
            return None
        except Exception as e:
            logger.error(f'根据ID获取历史记录失败: {str(e)}')
            return None
    
    def delete_history(self, history_id):
        """删除历史记录"""
        try:
            original_length = len(self.history)
            self.history = [item for item in self.history if item['id'] != history_id]
            
            if len(self.history) < original_length:
                self._save_history()
                logger.info(f'历史记录已删除，ID: {history_id}')
                return True
            else:
                return False
        except Exception as e:
            logger.error(f'删除历史记录失败: {str(e)}')
            return False
    
    def clear_history(self):
        """清空所有历史记录"""
        try:
            self.history = []
            self._save_history()
            logger.info('所有历史记录已清空')
            return True
        except Exception as e:
            logger.error(f'清空历史记录失败: {str(e)}')
            return False