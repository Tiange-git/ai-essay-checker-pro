// pages/result/result.js
Page({
  data: {
    result: null,
    content: '',
    suggestions: [],
    parsedErrors: [],
    expandedErrors: {}
  },

  onLoad: function (options) {
    const content = decodeURIComponent(options.content || '')
    this.setData({ content })

    const lastResult = wx.getStorageSync('lastResult')
    if (lastResult) {
      this.setData({ result: lastResult.result })
      this.parseErrors(lastResult.result)
    }
  },

  parseErrors: function (result) {
    if (!result) return

    const errors = []
    let suggestions = []

    try {
      if (result.detailed_errors && Array.isArray(result.detailed_errors)) {
        errors.push(...result.detailed_errors)
      }

      if (result.feedback) {
        const jsonMatch = result.feedback.match(/```json\n([\s\S]*?)\n```/)
        if (jsonMatch && jsonMatch[1]) {
          const jsonData = JSON.parse(jsonMatch[1])
          if (jsonData.errors && Array.isArray(jsonData.errors)) {
            errors.push(...jsonData.errors)
          }
          if (jsonData.suggestions && Array.isArray(jsonData.suggestions)) {
            suggestions = jsonData.suggestions
          }
        }
      }

      if (errors.length > 0 && !result.corrected_text) {
        let correctedText = this.data.content
        errors.forEach(error => {
          const original = error.original_sentence || error.original
          const corrected = error.corrected_sentence || error.corrected
          if (original && corrected) {
            correctedText = correctedText.replace(new RegExp(original.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), corrected)
          }
        })
        result.corrected_text = correctedText
      }

    } catch (e) {
      console.error('解析错误信息失败:', e)
    }

    this.setData({
      suggestions,
      parsedErrors: errors
    })
  },

  toggleError: function (e) {
    const index = e.currentTarget.dataset.index
    const expandedErrors = this.data.expandedErrors
    expandedErrors[index] = !expandedErrors[index]
    this.setData({ expandedErrors })
  },

  copyResult: function () {
    const { result } = this.data
    if (!result) return

    let text = '作文批改结果:\n\n'
    if (result.feedback) {
      text += `详细反馈:\n${result.feedback}\n\n`
    }
    if (result.corrected_text) {
      text += `修改后的文本:\n${result.corrected_text}`
    }

    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({
          title: '已复制到剪贴板',
          icon: 'success'
        })
      }
    })
  },

  checkAgain: function () {
    wx.removeStorageSync('lastResult')
    wx.navigateBack()
  }
})
