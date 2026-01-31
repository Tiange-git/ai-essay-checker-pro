// 云函数入口文件
const cloud = require('wx-server-sdk')

cloud.init()

const env = cloud.DYNAMIC_CURRENT_ENV

// 讯飞API配置
const XUNFEI_APPID = process.env.XUNFEI_APPID || 'your-appid'
const XUNFEI_API_KEY = process.env.XUNFEI_API_KEY || 'your-api-key'
const XUNFEI_API_SECRET = process.env.XUNFEI_API_SECRET || 'your-api-secret'

// 生成讯飞API签名
function generateSignature(method, url, date) {
  const crypto = require('crypto')
  const stringToSign = method + '\n' + url + '\n' + date
  const signature = crypto
    .createHmac('sha256', XUNFEI_API_SECRET)
    .update(stringToSign)
    .digest('base64')
  return signature
}

// 调用讯飞API批改作文
async function checkEssayWithXunfei(content) {
  const https = require('https')
  const crypto = require('crypto')
  
  const date = new Date().toUTCString()
  const method = 'POST'
  const url = '/v3/aichat/chat'
  
  const signature = generateSignature(method, url, date)
  
  const headers = {
    'Date': date,
    'Authorization': `HMAC-SHA256 Credential=${XUNFEI_API_KEY}, SignedHeaders=date;host, Signature=${signature}`,
    'Content-Type': 'application/json',
    'Host': 'spark-api.xf-yun.com'
  }
  
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'spark-api.xf-yun.com',
      port: 443,
      path: '/v3/aichat/chat',
      method: 'POST',
      headers: headers
    }
    
    const req = https.request(options, (res) => {
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => {
        try {
          const result = JSON.parse(data)
          resolve(result)
        } catch (e) {
          reject(e)
        }
      })
    })
    
    req.on('error', reject)
    
    const body = JSON.stringify({
      header: {
        app_id: XUNFEI_APPID,
        uid: 'wx-miniprogram'
      },
      parameter: {
        chat: {
          domain: 'generalv3.5',
          temperature: 0.7,
          max_tokens: 2048
        }
      },
      payload: {
        message: {
          text: [
            { role: 'system', content: '你是一位专业的英语作文批改老师，请对学生提交的英语作文进行详细批改，包括语法错误检查、词汇使用建议、句式改进建议等。批改结果请以JSON格式返回，包含feedback（详细反馈）、suggestions（改进建议数组）、corrected_text（修改后的完整文本）和detailed_errors（错误详情数组，包含original、corrected、explanation和error_type字段）。' },
            { role: 'user', content: `请批改以下英语作文:\n\n${content}` }
          ]
        }
      }
    })
    
    req.write(body)
    req.end()
  })
}

// 云函数主入口
exports.main = async (event, context) => {
  const { content } = event
  
  if (!content) {
    return { success: false, error: '缺少作文内容' }
  }
  
  try {
    const result = await checkEssayWithXunfei(content)
    
    const db = cloud.database()
    await db.collection('history').add({
      data: {
        content: content,
        result: result,
        type: 'text',
        created_at: new Date()
      }
    })
    
    return {
      success: true,
      result: result
    }
  } catch (error) {
    console.error('批改失败:', error)
    return {
      success: false,
      error: error.message
    }
  }
}
