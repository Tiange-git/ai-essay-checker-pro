// API服务层
const API_BASE_URL = 'https://your-backend-api.com/api'

const request = (options) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API_BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

const uploadFile = (filePath, formData) => {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: API_BASE_URL + '/upload-file',
      filePath: filePath,
      name: 'file',
      formData: formData,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(JSON.parse(res.data))
        } else {
          reject(new Error(`上传失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

export const checkEssay = (content) => {
  return request({
    url: '/check-essay',
    method: 'POST',
    data: { content }
  })
}

export const uploadFileToServer = (filePath) => {
  return uploadFile(filePath, {})
}

export const getHistory = (filter = 'all') => {
  return request({
    url: '/history',
    method: 'GET',
    data: { filter }
  })
}

export const getHistoryDetail = (historyId) => {
  return request({
    url: `/history/${historyId}`,
    method: 'GET'
  })
}

export const deleteHistoryItem = (historyId) => {
  return request({
    url: `/history/${historyId}`,
    method: 'DELETE'
  })
}

export const clearHistory = () => {
  return request({
    url: '/history',
    method: 'DELETE'
  })
}

export const cloudCheckEssay = (content) => {
  return new Promise((resolve, reject) => {
    wx.cloud.callFunction({
      name: 'checkEssay',
      data: { content },
      success: (res) => {
        resolve(res.result)
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

export const cloudUploadFile = (fileID) => {
  return new Promise((resolve, reject) => {
    wx.cloud.callFunction({
      name: 'uploadFile',
      data: { fileID },
      success: (res) => {
        resolve(res.result)
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

export const cloudGetHistory = (filter = 'all') => {
  return new Promise((resolve, reject) => {
    wx.cloud.callFunction({
      name: 'getHistory',
      data: { filter },
      success: (res) => {
        resolve(res.result)
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}
