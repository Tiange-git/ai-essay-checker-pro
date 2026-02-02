<template>
  <div class="essay-checker-container">
    <!-- 历史记录按钮 -->
    <button class="history-btn" @click="openHistory">
      📚 批改历史
    </button>
    
    <!-- 主内容区域 -->
    <div class="essay-checker">
        <div class="input-section">
          <h2>输入作文</h2>
          
          <!-- 输入方式选项卡 -->
          <div class="input-tabs">
            <button 
              @click="activeTab = 'text'"
              :class="['tab-btn', { active: activeTab === 'text' }]"
            >
              <span class="tab-icon">📝</span>
              <span class="tab-text">文本输入</span>
            </button>
            <button 
              @click="activeTab = 'word'"
              :class="['tab-btn', { active: activeTab === 'word' }]"
            >
              <span class="tab-icon">📄</span>
              <span class="tab-text">Word文档</span>
            </button>
            <button 
              @click="activeTab = 'image'"
              :class="['tab-btn', { active: activeTab === 'image' }]"
            >
              <span class="tab-icon">🖼️</span>
              <span class="tab-text">图片上传</span>
            </button>
          </div>
          
          <!-- 文本输入界面 -->
          <div v-show="activeTab === 'text'" class="tab-content animate-fade">
            <textarea
              v-model="essayContent"
              placeholder="请输入您的英语作文..."
              rows="10"
              class="essay-input"
            ></textarea>
            <div class="word-count">{{ essayContent.length }} 字</div>
          </div>
          
          <!-- Word文档上传界面 -->
          <div v-show="activeTab === 'word'" class="tab-content animate-fade">
            <div class="upload-area">
              <label class="upload-btn" :class="{ 'dragover': isDragover }"
                     @dragover.prevent="isDragover = true"
                     @dragleave.prevent="isDragover = false"
                     @drop.prevent="handleDrop">
                <input 
                  type="file" 
                  accept=".docx" 
                  @change="handleFileUpload"
                  :disabled="isLoading"
                  class="file-input"
                />
                <div class="upload-icon">📄</div>
                <div class="upload-text">点击或拖拽上传Word文档</div>
                <div class="upload-hint">支持.docx格式</div>
                <div v-if="uploadProgress > 0" class="upload-progress">
                  <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
                  <div class="progress-text">{{ uploadProgress }}%</div>
                </div>
              </label>
            </div>
          </div>
          
          <!-- 图片上传界面 -->
          <div v-show="activeTab === 'image'" class="tab-content animate-fade">
            <div class="upload-area">
              <label class="upload-btn" :class="{ 'dragover': isDragover }"
                     @dragover.prevent="isDragover = true"
                     @dragleave.prevent="isDragover = false"
                     @drop.prevent="handleDrop">
                <input 
                  type="file" 
                  accept="image/*"
                  @change="handleFileUpload"
                  :disabled="isLoading"
                  class="file-input"
                />
                <div class="upload-icon">🖼️</div>
                <div class="upload-text">点击或拖拽上传图片</div>
                <div class="upload-hint">支持.png、.jpg、.jpeg、.gif格式</div>
                <div v-if="uploadProgress > 0" class="upload-progress">
                  <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
                  <div class="progress-text">{{ uploadProgress }}%</div>
                </div>
              </label>
            </div>
          </div>
          
          <!-- 文件预览 -->
          <div v-if="selectedFile" class="file-preview animate-slide">
            <div class="preview-info">
              <span class="file-name">{{ selectedFile.name }}</span>
              <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
              <button @click="clearFile" class="clear-btn">清除</button>
            </div>
          </div>
          
          <button 
            @click="checkEssay"
            :disabled="isLoading || (!essayContent.trim() && !selectedFile)"
            class="check-btn"
            :class="{ 'loading': isLoading }"
          >
            <span v-if="isLoading" class="loading-spinner"></span>
            {{ isLoading ? '批改中...' : '开始批改' }}
          </button>
        </div>
        
        <div v-if="result" class="result-section animate-fade">
          <h2>批改结果</h2>
          
          <div class="feedback animate-fade">
            <h3>详细反馈</h3>
            <div class="feedback-content">
              <template v-if="result.feedback">
                <template v-if="result.feedback.includes('```json')">
                  <p>作文批改完成，已检测到语法错误并提供修改建议。</p>
                </template>
                <template v-else>
                  <p>{{ result.feedback }}</p>
                </template>
              </template>
              <p v-else>暂无详细反馈</p>
            </div>
          </div>
          
          <div v-if="result.suggestions && result.suggestions.length > 0" class="suggestions animate-fade">
            <h3>改进建议</h3>
            <ul>
              <li v-for="(suggestion, index) in result.suggestions" :key="index" 
                  class="animate-slide" 
                  :style="{ animationDelay: index * 0.1 + 's' }"
                  :data-type="getSuggestionType(suggestion)">
                <template v-if="!suggestion.includes('评分：') && !suggestion.includes('改进建议：')">
                  {{ suggestion }}
                </template>
              </li>
            </ul>
          </div>
          
          <!-- 错误对比板块 -->
          <div v-if="parsedErrors && parsedErrors.length > 0" class="error-comparison animate-fade">
            <h3>错误对比</h3>
            <div class="error-comparison-list">
              <div v-for="(error, index) in parsedErrors" :key="index" 
                   class="error-comparison-item animate-slide" :style="{ animationDelay: index * 0.15 + 's' }">
                <div class="error-header" @click="toggleError(index)">
                  <span class="error-type">{{ error.error_type }}</span>
                  <div class="error-header-right">
                    <span class="error-index">#{{ index + 1 }}</span>
                    <span class="toggle-icon">{{ expandedErrors[index] ? '▼' : '▶' }}</span>
                  </div>
                </div>
                <div v-if="expandedErrors[index]" class="error-content animate-fade">
                  <div class="error-comparison-row">
                    <div class="error-comparison-original">
                      <span class="label">错误:</span>
                      <span class="text original">{{ error.original }}</span>
                    </div>
                    <div class="error-comparison-corrected">
                      <span class="label">修改:</span>
                      <span class="text corrected">{{ error.corrected }}</span>
                    </div>
                  </div>
                  <div class="error-explanation">
                    <span class="label">解释:</span>
                    <span class="text">{{ error.explanation }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 修改后的完整文本 -->
          <div class="corrected-full-text animate-fade">
            <h3>修改后的完整文本</h3>
            <div class="content-box">
              <p>{{ result.corrected_text || '暂无修改后的文本' }}</p>
            </div>
          </div>
          
          <!-- 上传文件提取的内容 -->
          <div v-if="uploadedContent" class="uploaded-content animate-fade">
            <h3>提取的内容</h3>
            <div class="content-box">
              <p>{{ uploadedContent }}</p>
            </div>
          </div>
        </div>
      </div>
    
    <!-- 历史记录面板 -->
    <HistoryPanel
      :visible="showHistory"
      @close="closeHistory"
      @select="onHistorySelect"
      @delete="onHistoryItemDeleted"
      @clear="onHistoryCleared"
    ></HistoryPanel>
  </div>
</template>

<script>
import { ref } from 'vue'
import { checkEssay as apiCheckEssay, uploadFile as apiUploadFile } from '../api/essayAPI'
import HistoryPanel from './HistoryPanel.vue'

export default {
  name: 'EssayChecker',
  components: {
    HistoryPanel
  },
  setup() {
    const essayContent = ref('')
    const result = ref(null)
    const isLoading = ref(false)
    const selectedFile = ref(null)
    const uploadedContent = ref('')
    const activeTab = ref('text') // 默认选中文本输入
    const expandedErrors = ref({}) // 错误分析展开/折叠状态
    const isDragover = ref(false) // 拖拽上传状态
    const uploadProgress = ref(0) // 上传进度
    const selectedHistoryId = ref(null) // 当前选中的历史记录ID
    const parsedErrors = ref([]) // 解析后的错误信息
    const showHistory = ref(false) // 是否显示历史记录面板
    
    const checkEssay = async () => {
      if (!essayContent.value.trim() && !selectedFile.value) {
        alert('请输入作文内容或上传文件')
        return
      }
      
      isLoading.value = true
      uploadProgress.value = 0
      expandedErrors.value = {} // 重置错误展开状态
      
      try {
        if (selectedFile.value) {
          // 模拟上传进度
          uploadProgress.value = 30
          // 处理文件上传
          const res = await apiUploadFile(selectedFile.value)
          uploadProgress.value = 100
          result.value = res.result
          uploadedContent.value = res.content
        } else {
          // 处理文本输入
          const res = await apiCheckEssay(essayContent.value)
          result.value = res.result
          uploadedContent.value = ''
        }
        
        // 解析错误信息
        parseErrorsFromFeedback()
        
        // 重置历史记录选中状态
        selectedHistoryId.value = null
      } catch (error) {
        console.error('批改失败:', error)
        
        // 显示详细的错误信息
        let errorMessage = '批改失败，请稍后重试'
        
        if (error.response) {
          // 服务器响应了错误状态码
          const status = error.response.status
          const data = error.response.data
          
          if (status === 400) {
            errorMessage = data.error || '请求参数错误，请检查输入内容'
          } else if (status === 500) {
            errorMessage = data.error || '服务器内部错误，请稍后重试'
          } else if (status === 404) {
            errorMessage = 'API接口不存在'
          } else {
            errorMessage = `请求失败 (${status}): ${data.error || '未知错误'}`
          }
        } else if (error.request) {
          // 请求已发送但没有收到响应
          errorMessage = '网络连接失败，请检查网络或稍后重试'
        } else {
          // 请求配置出错
          errorMessage = `请求配置错误: ${error.message}`
        }
        
        alert(errorMessage)
      } finally {
        isLoading.value = false
        uploadProgress.value = 0
      }
    }
    
    // 从API响应中解析错误信息
    const parseErrorsFromFeedback = () => {
      if (!result.value) {
        parsedErrors.value = []
        return
      }
      
      try {
        // 优先检查是否有直接的detailed_errors字段
        if (result.value.detailed_errors && Array.isArray(result.value.detailed_errors)) {
          parsedErrors.value = result.value.detailed_errors
          return
        }
        
        // 如果没有直接的错误信息，尝试从feedback字段中提取JSON数据
        if (result.value.feedback) {
          const feedbackText = result.value.feedback
          
          // 查找JSON代码块
          const jsonMatch = feedbackText.match(/```json\n([\s\S]*?)\n```/)
          if (jsonMatch && jsonMatch[1]) {
            const jsonData = JSON.parse(jsonMatch[1])
            
            // 检查是否有errors字段
            if (jsonData.errors && Array.isArray(jsonData.errors)) {
              parsedErrors.value = jsonData.errors
              
              // 如果corrected_text为空，使用解析出来的corrected_text
              if (!result.value.corrected_text && jsonData.corrected_text) {
                result.value.corrected_text = jsonData.corrected_text
              }
              return
            }
          }
        }
        
        // 如果没有找到JSON代码块，尝试从错误信息中构建修改后的文本
        if (parsedErrors.value.length > 0 && !result.value.corrected_text) {
          // 使用原始文本作为基础，然后应用错误修正
          // 优先使用uploadedContent（图片OCR提取的文本），其次使用essayContent
          const originalText = uploadedContent.value || essayContent.value
          if (originalText) {
            let correctedText = originalText
            
            // 对每个错误应用修正，支持多种字段名
            parsedErrors.value.forEach(error => {
              // 尝试不同的字段名组合
              const original = error.original_sentence || error.original || error.Original
              const corrected = error.corrected_sentence || error.corrected || error.Corrected
              
              if (original && corrected) {
                // 使用正则表达式进行更精确的替换，避免部分匹配
                const escapedOriginal = original.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
                correctedText = correctedText.replace(new RegExp(escapedOriginal, 'g'), corrected)
              }
            })
            
            result.value.corrected_text = correctedText
          }
        }
        
        // 最后，如果还是没有corrected_text，显示原始文本
        if (!result.value.corrected_text) {
          result.value.corrected_text = essayContent.value || uploadedContent.value || '暂无修改后的文本'
        }
        
        // 如果没有找到任何错误信息，设置为空数组
        parsedErrors.value = []
      } catch (error) {
        console.error('解析错误信息失败:', error)
        parsedErrors.value = []
      }
    }
    
    const handleFileUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        // 清空文本输入，避免冲突
        essayContent.value = ''
      }
      isDragover.value = false
    }
    
    const handleDrop = (event) => {
      isDragover.value = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        const file = files[0]
        if ((activeTab.value === 'word' && file.name.endsWith('.docx')) || 
            (activeTab.value === 'image' && file.type.startsWith('image/'))) {
          selectedFile.value = file
          essayContent.value = ''
        } else {
          alert('请上传正确格式的文件')
        }
      }
    }
    
    const clearFile = () => {
      selectedFile.value = null
      uploadedContent.value = ''
      uploadProgress.value = 0
    }
    
    const toggleError = (index) => {
      expandedErrors.value[index] = !expandedErrors.value[index]
    }
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const onHistorySelect = (historyItem) => {
      selectedHistoryId.value = historyItem.id
      essayContent.value = historyItem.content
      result.value = historyItem.result
      uploadedContent.value = ''
      selectedFile.value = null
      activeTab.value = 'text'
      
      // 解析历史记录中的错误信息
      parseErrorsFromFeedback()
    }
    
    const onHistoryItemDeleted = (historyId) => {
      if (selectedHistoryId.value === historyId) {
        selectedHistoryId.value = null
        essayContent.value = ''
        result.value = null
      }
    }
    
    const onHistoryCleared = () => {
      selectedHistoryId.value = null
      essayContent.value = ''
      result.value = null
    }
    
    const openHistory = () => {
      showHistory.value = true
    }
    
    const closeHistory = () => {
      showHistory.value = false
    }
    
    const getSuggestionType = (suggestion) => {
      const text = suggestion.toLowerCase()
      if (text.includes('评分') || text.includes('score')) return 'score'
      if (text.includes('语法') || text.includes('grammar')) return 'grammar'
      if (text.includes('词汇') || text.includes('vocabulary')) return 'vocabulary'
      if (text.includes('结构') || text.includes('structure')) return 'structure'
      if (text.includes('表达') || text.includes('expression')) return 'expression'
      return 'general'
    }
    
    return {
      essayContent,
      result,
      isLoading,
      selectedFile,
      uploadedContent,
      activeTab,
      expandedErrors,
      isDragover,
      uploadProgress,
      selectedHistoryId,
      parsedErrors,
      showHistory,
      checkEssay,
      handleFileUpload,
      handleDrop,
      clearFile,
      toggleError,
      formatFileSize,
      onHistorySelect,
      onHistoryItemDeleted,
      onHistoryCleared,
      openHistory,
      closeHistory,
      getSuggestionType
    }
  }
}
</script>

<style scoped>
/* 色彩方案 */
:root {
  --primary-color: #1a1a1a;
  --secondary-color: #2d2d2d;
  --accent-color: #4a90e2;
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
  --text-muted: #888888;
  --border-color: #404040;
  --success-color: #28a745;
  --error-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  --hover-color: #333333;
  --card-bg: #2d2d2d;
  --input-bg: #1a1a1a;
}

.essay-checker-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
}

/* 全局样式重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 动画效果 */
.animate-fade {
  animation: fadeIn 0.5s ease-in-out;
}

.animate-slide {
  animation: slideIn 0.5s ease-out;
}

.animate-scale {
  animation: scaleIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 历史记录按钮 */
.history-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
  transition: all 0.3s ease;
  z-index: 1000;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

.history-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
  background: linear-gradient(135deg, #ff5252, #ff7b47);
}

/* 主容器 */
.essay-checker {
  background-color: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 标题样式 */
.input-section h2,
.result-section h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  text-align: center;
  background: linear-gradient(135deg, var(--accent-color), #6c5ce7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 输入方式选项卡 - 模块化设计 */
.input-tabs {
  display: flex;
  gap: 0.5rem;
  background: var(--card-bg);
  border-radius: 12px;
  padding: 0.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
}

.tab-btn {
  flex: 1;
  padding: 1rem 1.5rem;
  border: none;
  background: linear-gradient(135deg, var(--input-bg), #2a2a2a);
  color: var(--text-secondary);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.tab-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.tab-btn:hover::before {
  left: 100%;
}

.tab-btn.active {
  background: linear-gradient(135deg, var(--accent-color), #6c5ce7);
  color: white;
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.4);
  transform: translateY(-2px);
}

.tab-btn:hover {
  background: linear-gradient(135deg, #3a3a3a, #2a2a2a);
  color: var(--text-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transform: translateY(-1px);
}

.tab-btn.active:hover {
  background: linear-gradient(135deg, #3a7bd5, #5a4fcf);
  transform: translateY(-2px);
}

/* 选项卡图标和文本样式 */
.tab-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.tab-icon {
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.tab-btn.active .tab-icon {
  transform: scale(1.1);
}

.tab-btn:hover .tab-icon {
  transform: scale(1.05);
}

.tab-text {
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.tab-btn.active .tab-text {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 响应式设计 - 移动端适配 */
@media (max-width: 768px) {
  .input-tabs {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .tab-btn {
    flex-direction: row;
    justify-content: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
  }
  
  .tab-icon {
    font-size: 1.25rem;
  }
  
  .tab-text {
    font-size: 0.85rem;
  }
}

/* 文本输入框 */
.essay-input {
  width: 100%;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  transition: all 0.3s;
  background-color: var(--input-bg);
  color: var(--text-primary);
}

.essay-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.word-count {
  text-align: right;
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

/* 上传区域 */
.upload-area {
  margin-bottom: 1.5rem;
}

.upload-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  background-color: var(--input-bg);
}

.upload-btn:hover,
.upload-btn.dragover {
  border-color: var(--accent-color);
  background-color: var(--hover-color);
}

.file-input {
  opacity: 0;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.upload-hint {
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* 上传进度 */
.upload-progress {
  width: 100%;
  max-width: 200px;
  margin-top: 1rem;
}

.progress-bar {
  height: 4px;
  background-color: var(--accent-color);
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-text {
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

/* 文件预览 */
.file-preview {
  margin-bottom: 1.5rem;
}

.preview-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background-color: var(--input-bg);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.file-name {
  font-weight: 500;
  color: var(--text-primary);
}

.file-size {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.clear-btn {
  background: var(--error-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.3s;
}

.clear-btn:hover {
  background: #c82333;
}

/* 批改按钮 */
.check-btn {
  width: 100%;
  padding: 1.25rem 2rem;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.25rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
  margin-top: 1rem;
}

.check-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.6);
  background: linear-gradient(135deg, #43A047, #3d8b40);
}

.check-btn:disabled {
  background: linear-gradient(135deg, #9E9E9E, #757575);
  cursor: not-allowed;
  opacity: 0.7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.check-btn.loading {
  background: linear-gradient(135deg, #9E9E9E, #757575);
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 结果区域 */
.result-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.result-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.feedback-content,
.suggestions ul,
.content-box {
  background-color: var(--input-bg);
  padding: 1rem;
  border-radius: 6px;
  line-height: 1.6;
  border: 1px solid var(--border-color);
}

.suggestions ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.suggestions li {
  padding: 1rem 1.25rem 1rem 4rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.05), rgba(74, 144, 226, 0.02));
  border-radius: 8px;
  margin-bottom: 0.75rem;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-left: 4px solid transparent;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  font-size: 0.95rem;
  line-height: 1.5;
}

.suggestions li:hover {
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.12), rgba(74, 144, 226, 0.08));
  border-left: 4px solid var(--accent-color);
  transform: translateX(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestions li:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.suggestions li::before {
  position: absolute;
  left: 1.25rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  opacity: 0.9;
  transition: all 0.3s ease;
}

.suggestions li:hover::before {
  transform: translateY(-50%) scale(1.1);
  opacity: 1;
}

/* 根据内容类型设置不同的图标和颜色 */
.suggestions li:nth-child(1)::before {
  content: '⭐';
  color: #ffd700;
}

.suggestions li:nth-child(2)::before {
  content: '📊';
  color: #4a90e2;
}

.suggestions li:nth-child(3)::before {
  content: '🔧';
  color: #ff6b6b;
}

.suggestions li:nth-child(4)::before {
  content: '📈';
  color: #51cf66;
}

.suggestions li:nth-child(5)::before {
  content: '🎯';
  color: #ff8e53;
}

.suggestions li:nth-child(6)::before {
  content: '💬';
  color: #9c88ff;
}

.suggestions li:nth-child(7)::before {
  content: '📝';
  color: #fbc531;
}

.suggestions li:nth-child(8)::before {
  content: '🔍';
  color: #00a8ff;
}

/* 默认图标 */
.suggestions li::before {
  content: '💡';
  color: var(--accent-color);
}

/* 根据内容关键词设置不同的背景色 */
.suggestions li[data-type="score"] {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 215, 0, 0.05));
  border-left: 4px solid #ffd700;
}

.suggestions li[data-type="grammar"] {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
  border-left: 4px solid #ff6b6b;
}

.suggestions li[data-type="vocabulary"] {
  background: linear-gradient(135deg, rgba(81, 207, 102, 0.1), rgba(81, 207, 102, 0.05));
  border-left: 4px solid #51cf66;
}

.suggestions li[data-type="structure"] {
  background: linear-gradient(135deg, rgba(156, 136, 255, 0.1), rgba(156, 136, 255, 0.05));
  border-left: 4px solid #9c88ff;
}

.suggestions li[data-type="expression"] {
  background: linear-gradient(135deg, rgba(251, 197, 49, 0.1), rgba(251, 197, 49, 0.05));
  border-left: 4px solid #fbc531;
}

.suggestions li[data-type="general"] {
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.1), rgba(74, 144, 226, 0.05));
  border-left: 4px solid var(--accent-color);
}

/* 评分项的特殊样式 */


.suggestions li:contains("语法") {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
  border-left: 3px solid #ff6b6b;
}

.suggestions li:contains("改进") {
  background: linear-gradient(135deg, rgba(81, 207, 102, 0.1), rgba(81, 207, 102, 0.05));
  border-left: 3px solid #51cf66;
}

/* 错误对比 */
.error-comparison-item {
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin-bottom: 0.5rem;
  overflow: hidden;
  background-color: var(--input-bg);
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: var(--hover-color);
  cursor: pointer;
  transition: background-color 0.3s;
}

.error-header:hover {
  background-color: var(--border-color);
}

.error-type {
  font-weight: 500;
  color: var(--error-color);
}

.error-header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-index {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.toggle-icon {
  color: var(--text-muted);
}

.error-content {
  padding: 1rem;
  background-color: var(--card-bg);
}

.error-comparison-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.05), rgba(81, 207, 102, 0.05));
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  position: relative;
}

.error-comparison-row::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 100%;
  background: linear-gradient(to bottom, transparent, var(--border-color), transparent);
}

.error-comparison-original,
.error-comparison-corrected {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.error-comparison-original:hover {
  background: rgba(255, 107, 107, 0.05);
  transform: translateY(-2px);
}

.error-comparison-corrected:hover {
  background: rgba(81, 207, 102, 0.05);
  transform: translateY(-2px);
}

.label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label::before {
  font-size: 1rem;
}

.error-comparison-original .label::before {
  content: '❌';
}

.error-comparison-corrected .label::before {
  content: '✅';
}

.text.original {
  color: #ff6b6b;
  text-decoration: line-through;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
  padding: 0.75rem 0.75rem 0.75rem 3rem;
  border-radius: 6px;
  border-left: 4px solid #ff6b6b;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.2);
  position: relative;
  overflow: hidden;
  min-height: 3rem;
  display: flex;
  align-items: center;
}

.text.original::before {
  content: '❌';
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  opacity: 0.8;
  z-index: 1;
}

.text.corrected {
  color: #51cf66;
  background: linear-gradient(135deg, rgba(81, 207, 102, 0.1), rgba(81, 207, 102, 0.05));
  padding: 0.75rem 0.75rem 0.75rem 3rem;
  border-radius: 6px;
  border-left: 4px solid #51cf66;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(81, 207, 102, 0.2);
  position: relative;
  overflow: hidden;
  min-height: 3rem;
  display: flex;
  align-items: center;
}

.text.corrected::before {
  content: '✅';
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  opacity: 0.8;
  z-index: 1;
}

.error-explanation {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
  padding: 1rem 1rem 1rem 3rem;
  border-radius: 8px;
  border-left: 4px solid #ffc107;
  margin-top: 1rem;
  position: relative;
  overflow: hidden;
  min-height: 3rem;
}

.error-explanation::before {
  content: '💡';
  position: absolute;
  left: 1rem;
  top: 1rem;
  font-size: 1rem;
  opacity: 0.8;
  z-index: 1;
}

.error-explanation .label {
  color: #ffc107;
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.error-explanation .text {
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.6;
  font-weight: 500;
  word-wrap: break-word;
  padding-left: 0;
  margin-left: 0;
}

/* 确保文本内容不会被图标遮挡 */
.text {
  position: relative;
  z-index: 2;
}

/* 调整对比区域的间距和布局 */
.error-comparison-original,
.error-comparison-corrected {
  min-height: 4rem;
}

.error-comparison-row {
  min-height: 6rem;
}

/* 错误对比项的整体动画效果 */
.error-comparison-item {
  transition: all 0.3s ease;
}

.error-comparison-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

/* 错误标题的视觉增强 */
.error-type {
  font-weight: 700;
  color: #ff6b6b;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), transparent);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  border: 1px solid rgba(255, 107, 107, 0.3);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.error-index {
  background: var(--accent-color);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 2rem;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .essay-checker-container {
    padding: 10px;
  }
  
  .history-btn {
    top: 10px;
    right: 10px;
    padding: 10px 16px;
    font-size: 12px;
  }
  
  .essay-checker {
    padding: 1rem;
  }
  
  .input-tabs {
    flex-direction: column;
  }
  
  .error-comparison-row {
    grid-template-columns: 1fr;
  }
}
</style>