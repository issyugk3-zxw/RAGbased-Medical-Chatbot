const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
  role: {
    type: String,
    required: true,
    enum: ['user', 'assistant'] 
  },
  content: {
    type: String,
    required: true
  },
  timestamp: {
    type: Number, // 使用数字类型存储时间戳以便排序
    required: true
  }
}, { _id: false }); // 不为子文档生成 _id

const sessionSchema = new mongoose.Schema({
  userid: {
    type: String, 
    required: true,
    index: true // 为 userid 添加索引以提高查询效率
  },
  sessionid: {
    type: String,
    required: true,
    unique: true,
    default: () => new mongoose.Types.ObjectId().toString() // 默认使用 ObjectId 作为唯一 ID
  },
  session_title: {
    type: String,
    required: true,
    default: '新会话'
  },
  history: [messageSchema], // 嵌套消息数组
  timestamp: { // 会话创建时间
    type: Number, 
    required: true,
    default: Date.now,
    index: true // 添加索引以提高排序效率
  }
});

// 添加复合索引，如果经常需要根据 userid 和 timestamp 查询/排序
sessionSchema.index({ userid: 1, timestamp: -1 }); 

// 在返回 JSON 时将 _id 映射为 sessionid，并移除 __v
sessionSchema.set('toJSON', {
  transform: (doc, ret) => {
    ret.sessionid = ret._id.toString(); // 将 _id 映射到 sessionid
    delete ret._id;
    delete ret.__v;
    // 可以选择性地移除 userid，如果前端不需要
    // delete ret.userid; 
    return ret;
  }
});


const Session = mongoose.model('Session', sessionSchema, 'sessions'); // 指定集合名称为 'sessions'

module.exports = Session; 