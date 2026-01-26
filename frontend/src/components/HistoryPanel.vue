<template>
  <div class="history-modal" v-if="visible">
    <div class="modal-overlay" @click="$emit('close')"></div>
    <div class="modal-content">
      <div class="modal-header">
        <h2>批改历史</h2>
        <button class="close-btn" @click="$emit('close')" title="关闭">
          ×
        </button>
      </div>
      
      <div class="modal-body">
        <!-- 筛选器 -->
        <div class="filter-tabs">
          <button 
            v-for="filter in filters" 
            :key="filter.value"
            @click="changeFilter(filter.value)"
            :class="['filter-btn', { active: currentFilter === filter.value }]"
          >
            {{ filter.label }}
          </button>
        </div>
        
        <!-- 历史记录列表 -->
        <div class="history-list" v-if="history.length > 0">
          <div 
            v-for="item in history" 
            :key="item.id"
            class="history-item"
            :class="{ selected: selectedItem === item.id }"
            @click="selectItem(item)"
          >
            <div class="item-header">
              <div class="item-type">{{ getTypeText(item.type) }}</div>
              <div class="item-time">{{ formatTime(item.created_at) }}</div>
              <button 
                @click.stop="deleteItem(item.id)" 
                class="delete-btn"
                title="删除"
              >
                ×
              </button>
            </div>
            <div class="item-content">
              {{ truncateContent(item.content) }}
            </div>
            <div class="item-score" v-if="item.result && item.result.score">
              评分: {{ item.result.score }}
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">📝</div>
          <div class="empty-text">暂无历史记录</div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <div>加载中...</div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button 
          @click="clearHistory" 
          class="clear-btn"
          :disabled="history.length === 0"
        >
          清空历史
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { getHistory, deleteHistory, clearHistory } from '../api/essayAPI'

export default {
  name: 'HistoryPanel',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'select', 'delete', 'clear'],
  data() {
    return {
      history: [],
      loading: false,
      currentFilter: 'all',
      filters: [
        { label: '全部历史', value: 'all' },
        { label: '今天', value: 'today' },
        { label: '3天内', value: '3days' },
        { label: '一周内', value: 'week' }
      ],
      selectedItem: null
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.loadHistory()
      }
    }
  },
  methods: {
    async loadHistory() {
      this.loading = true
      try {
        const response = await getHistory(this.currentFilter)
        if (response.success) {
          this.history = response.history
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async changeFilter(filter) {
      this.currentFilter = filter
      await this.loadHistory()
    },
    
    selectItem(item) {
      this.selectedItem = item.id
      this.$emit('select', item)
      this.$emit('close')
    },
    
    async deleteItem(historyId) {
      if (confirm('确定要删除这条历史记录吗？')) {
        try {
          const response = await deleteHistory(historyId)
          if (response.success) {
            this.history = this.history.filter(item => item.id !== historyId)
            this.$emit('delete', historyId)
          }
        } catch (error) {
          console.error('删除历史记录失败:', error)
        }
      }
    },
    
    async clearHistory() {
      if (confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
        try {
          const response = await clearHistory()
          if (response.success) {
            this.history = []
            this.$emit('clear')
          }
        } catch (error) {
          console.error('清空历史记录失败:', error)
        }
      }
    },
    
    getTypeText(type) {
      const typeMap = {
        'text': '文本',
        'word': 'Word',
        'image': '图片'
      }
      return typeMap[type] || '未知'
    },
    
    formatTime(timeStr) {
      const date = new Date(timeStr)
      const now = new Date()
      const diff = now - date
      
      // 今天
      if (diff < 24 * 60 * 60 * 1000) {
        return date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      }
      
      // 昨天
      if (diff < 2 * 24 * 60 * 60 * 1000) {
        return '昨天'
      }
      
      // 一周内
      if (diff < 7 * 24 * 60 * 60 * 1000) {
        return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
      }
      
      // 更早
      return date.toLocaleDateString('zh-CN')
    },
    
    truncateContent(content) {
      if (!content) return ''
      if (content.length <= 50) return content
      return content.substring(0, 50) + '...'
    }
  }
}
</script>

<style scoped>
.history-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-content {
  position: relative;
  background: #2d2d2d;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  border: 1px solid #404040;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #404040;
}

.modal-header h2 {
  margin: 0;
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, #4a90e2, #6c5ce7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.close-btn {
  background: none;
  border: none;
  color: #b0b0b0;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: all 0.3s;
}

.close-btn:hover {
  color: #ffffff;
  background: #404040;
}

.modal-body {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #404040;
  text-align: right;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 1.5rem;
}

.filter-btn {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #404040;
  background: #1a1a1a;
  color: #b0b0b0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s;
}

.filter-btn.active {
  background: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.filter-btn:hover {
  background: #333333;
  color: #ffffff;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  background: #1a1a1a;
  border: 1px solid #404040;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  border-color: #4a90e2;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.2);
}

.history-item.selected {
  border-color: #4a90e2;
  background: rgba(74, 144, 226, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-type {
  background: #404040;
  color: #b0b0b0;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: bold;
}

.item-time {
  color: #888888;
  font-size: 12px;
}

.delete-btn {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  transition: background-color 0.3s;
}

.delete-btn:hover {
  background: rgba(220, 53, 69, 0.1);
}

.item-content {
  color: #ffffff;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 8px;
}

.item-score {
  color: #28a745;
  font-size: 12px;
  font-weight: bold;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #888888;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #888888;
  padding: 3rem 1rem;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.clear-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.clear-btn:disabled {
  background: #404040;
  color: #888888;
  cursor: not-allowed;
}

.clear-btn:hover:not(:disabled) {
  background: #c82333;
}

/* 滚动条样式 */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb {
  background: #404040;
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: #4a90e2;
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: #2d2d2d;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #404040;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #4a90e2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .filter-tabs {
    flex-direction: column;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 1rem;
  }
}
</style>