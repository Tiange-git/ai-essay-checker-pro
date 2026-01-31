// pages/index/index.js
const app = getApp()
const { checkEssay, uploadFileToServer } = require('../../services/api.js')

Page({
  data: {
    activeTab: 'text',
    essayContent: '',
    selectedFilePath: '',
    selectedFileName: '',
    previewImage: '',
    isLoading: false,
    essayCount: 0
  },

  onLoad: function (options) {
  },

  switchTab: function (e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({
      activeTab: tab,
      selectedFilePath: '',
      selectedFileName: '',
      previewImage: ''
    })
  },

  onInputChange: function (e) {
    const content = e.detail.value
    this.setData({
      essayContent: content,
      essayCount: content.length
    })
  },

  chooseWordFile: function () {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      success: (res) => {
        const file = res.tempFiles[0]
        if (file.name.endsWith('.docx')) {
          this.setData({
            selectedFilePath: file.path,
            selectedFileName: file.name
          })
        } else {
          wx.showToast({
            title: '请上传.docx文件',
            icon: 'none'
          })
        }
      }
    })
  },

  chooseImage: function () {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath
        const fileName = tempFilePath.split('/').pop()
        this.setData({
          selectedFilePath: tempFilePath,
          selectedFileName: fileName,
          previewImage: tempFilePath
        })
      }
    })
  },

  checkEssay: async function () {
    const { essayContent, selectedFilePath } = this.data

    if (!essayContent.trim() && !selectedFilePath) {
      wx.showToast({
        title: '请输入作文或上传文件',
        icon: 'none'
      })
      return
    }

    this.setData({ isLoading: true })

    try {
      let result, content

      if (selectedFilePath) {
        const res = await uploadFileToServer(selectedFilePath)
        result = res.result
        content = res.content
      } else {
        const res = await checkEssay(essayContent)
        result = res.result
        content = essayContent
      }

      wx.setStorageSync('lastResult', {
        result,
        content,
        timestamp: Date.now()
      })

      wx.navigateTo({
        url: `/pages/result/result?content=${encodeURIComponent(content)}`
      })

    } catch (error) {
      console.error('批改失败:', error)
      wx.showToast({
        title: '批改失败，请重试',
        icon: 'none'
      })
    } finally {
      this.setData({ isLoading: false })
    }
  },

  goToHistory: function () {
    wx.switchTab({
      url: '/pages/history/history'
    })
  }
})
