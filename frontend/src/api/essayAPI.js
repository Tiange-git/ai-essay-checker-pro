import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const fileApiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
})

// 批改作文
export const checkEssay = async (content) => {
  try {
    const response = await apiClient.post('/check-essay', {
      content
    })
    return response.data
  } catch (error) {
    console.error('批改作文失败:', error)
    throw error
  }
}

// 文件上传
export const uploadFile = async (file) => {
  try {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', file)
    
    // 发送文件上传请求
    const response = await fileApiClient.post('/upload-file', formData)
    return response.data
  } catch (error) {
    console.error('文件上传失败:', error)
    throw error
  }
}

// 获取批改历史
export const getHistory = async (filter = 'all') => {
  try {
    const response = await apiClient.get('/history', {
      params: { filter }
    })
    return response.data
  } catch (error) {
    console.error('获取历史记录失败:', error)
    throw error
  }
}

// 获取历史记录详情
export const getHistoryDetail = async (historyId) => {
  try {
    const response = await apiClient.get(`/history/${historyId}`)
    return response.data
  } catch (error) {
    console.error('获取历史记录详情失败:', error)
    throw error
  }
}

// 删除历史记录
export const deleteHistory = async (historyId) => {
  try {
    const response = await apiClient.delete(`/history/${historyId}`)
    return response.data
  } catch (error) {
    console.error('删除历史记录失败:', error)
    throw error
  }
}

// 清空历史记录
export const clearHistory = async () => {
  try {
    const response = await apiClient.delete('/history')
    return response.data
  } catch (error) {
    console.error('清空历史记录失败:', error)
    throw error
  }
}
