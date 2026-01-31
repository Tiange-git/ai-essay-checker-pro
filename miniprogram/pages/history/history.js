// pages/history/history.js
const { getHistory, deleteHistoryItem, clearHistory } = require('../../services/api.js')

Page({
  data: {
    history: [],
    currentFilter: 'all',
    loading: false,
    clearing: false
  },

  onShow: function () {
    this.loadHistory()
  },

  loadHistory: async function () {
    this.setData({ loading: true })
    try {
      const res = await getHistory(this.data.currentFilter)
      if (res.success) {
        this.setData({ history: res.history })
      }
    } catch (error) {
      console.error('加载历史记录失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  changeFilter: function (e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({ currentFilter: filter })
    this.loadHistory()
  },

  selectItem: function (e) {
    const item = e.currentTarget.dataset.item
    wx.setStorageSync('lastResult', {
      result: item.result,
      content: item.content,
      timestamp: Date.now()
    })
    wx.navigateTo({
      url: `/pages/result/result?content=${encodeURIComponent(item.content)}`
    })
  },

  deleteItem: function (e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条历史记录吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            const result = await deleteHistoryItem(id)
            if (result.success) {
              this.loadHistory()
              wx.showToast({
                title: '删除成功',
                icon: 'success'
              })
            }
          } catch (error) {
            console.error('删除失败:', error)
            wx.showToast({
              title: '删除失败',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  clearHistory: function () {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空所有历史记录吗？此操作不可恢复。',
      success: async (res) => {
        if (res.confirm) {
          this.setData({ clearing: true })
          try {
            const result = await clearHistory()
            if (result.success) {
              this.setData({ history: [] })
              wx.showToast({
                title: '清空成功',
                icon: 'success'
              })
            }
          } catch (error) {
            console.error('清空失败:', error)
            wx.showToast({
              title: '清空失败',
              icon: 'none'
            })
          } finally {
            this.setData({ clearing: false })
          }
        }
      }
    })
  },

  formatTime: function (timeStr) {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now - date

    if (diff < 24 * 60 * 60 * 1000) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    if (diff < 2 * 24 * 60 * 60 * 1000) {
      return '昨天'
    }

    if (diff < 7 * 24 * 60 * 60 * 1000) {
      return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
    }

    return date.toLocaleDateString('zh-CN')
  },

  truncateContent: function (content) {
    if (!content) return ''
    if (content.length <= 100) return content
    return content.substring(0, 100) + '...'
  }
})
