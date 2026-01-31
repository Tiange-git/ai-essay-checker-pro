// 云函数入口文件
const cloud = require('wx-server-sdk')

cloud.init()

const env = cloud.DYNAMIC_CURRENT_ENV

function getFilterDate(filter) {
  const now = new Date()
  switch (filter) {
    case 'today':
      return new Date(now.setHours(0, 0, 0, 0))
    case '3days':
      return new Date(now.setDate(now.getDate() - 3))
    case 'week':
      return new Date(now.setDate(now.getDate() - 7))
    default:
      return new Date(0)
  }
}

// 云函数主入口
exports.main = async (event, context) => {
  const { filter = 'all' } = event
  const wxContext = cloud.getWXContext()
  const openid = wxContext.OPENID
  
  try {
    const db = cloud.database()
    const _ = db.command
    
    const filterDate = getFilterDate(filter)
    
    let query = db.collection('history')
      .where({
        _openid: openid,
        created_at: _.gte(filterDate)
      })
      .orderBy('created_at', 'desc')
    
    const { data } = await query.get()
    
    return {
      success: true,
      history: data,
      filter: filter,
      count: data.length
    }
  } catch (error) {
    console.error('获取历史记录失败:', error)
    return {
      success: false,
      error: error.message
    }
  }
}
