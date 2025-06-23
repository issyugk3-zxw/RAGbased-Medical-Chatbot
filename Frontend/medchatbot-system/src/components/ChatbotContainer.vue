<template>
  <div class="chatbot-container">
    <!-- 左侧消息列表 (20%) -->
    <div class="message-list-container glass-card">
      <div class="message-list-header">
        <h3>消息历史</h3>
        <el-button type="primary" class="new-chat-btn" @click="startNewChat">
          <el-icon><Plus /></el-icon>新会话
        </el-button>
      </div>
      <div class="message-list">
        <div 
          v-for="chat in chatHistory" 
          :key="chat.session_id" 
          class="chat-item" 
          :class="{ 'active': selectedChatId === chat.session_id }"
          @click="selectChat(chat.session_id)"
        >
          <div class="chat-info">
            <el-icon><ChatDotRound /></el-icon>
            <div class="chat-title">{{ chat.title }}</div>
            <div class="chat-date">{{ formatDate(chat.createdAt) }}</div>
          </div>
          <div class="chat-actions">
            <el-tooltip content="删除会话" placement="top">
              <el-button 
                type="danger" 
                circle 
                size="small" 
                @click.stop="deleteChat(chat.session_id)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </div>
    </div>
    

    <div class="chat-main-container">
      <!-- PixiCanvas -->
      <div class="pixi-container glass-card">
        <PixiCanvas />
      </div>
      
      <!-- 消息记录 -->
      <div class="messages-container glass-card">
        <div class="messages-wrapper" ref="messagesWrapper">
          <div 
            v-for="(message, index) in selectedChat?.messages" 
            :key="index" 
            class="message-bubble"
            :class="{ 'user-message': message.role === 'user', 'bot-message': message.role === 'assistant' }"
          >
            <div class="message-sender">
              <div class="avatar" :class="message.role">
                <el-icon v-if="message.role === 'user'"><User /></el-icon>
                <el-icon v-else><Service /></el-icon>
              </div>
              <div class="sender-name">{{ message.role === 'user' ? '您' : '医疗助手' }}</div>
            </div>
            <div class="message-content">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        
        <div class="message-input">
          <el-input
            v-model="userInput"
            placeholder="请输入您的问题..."
            :disabled="isWaitingForResponse"
            type="textarea"
            :rows="2"
            @keyup.enter.ctrl="sendMessage"
          />
          <div class="input-actions">
            <el-tooltip content="发送消息" placement="top">
              <el-button 
                type="primary" 
                circle 
                :disabled="!userInput.trim() || isWaitingForResponse" 
                @click="sendMessage"
              >
                <el-icon><Promotion /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右侧控制台 -->
    <div class="control-panel glass-card">
      <div class="panel-header">
        <h3>控制面板</h3>
      </div>
      
      <div class="panel-section">
        <h4>语音控制</h4>
        <div class="voice-controls">
          <el-button 
            :type="isRecording ? 'danger' : 'primary'"
            :icon="isRecording ? 'Microphone' : 'VideoPlay'"
            @click="toggleRecording"
            class="record-btn"
            :class="{ 'is-recording': isRecording }"
            round
          >
            {{ isRecording ? '停止录音' : '开始录音' }}
          </el-button>
          
          <div class="recording-indicator" v-if="isRecording">
            <span class="record-dot"></span>
            正在录音...
          </div>
        </div>
      </div>
      
      <div class="panel-section">
        <h4>会话设置</h4>
        <div class="setting-item">
          <span>自动播放语音回复</span>
          <el-switch v-model="settings.autoPlayVoice" />
        </div>
        <div class="setting-item" v-if="selectedChat?.knowledge?.from_kg?.['问诊'] === '是'">
          <el-button 
            type="success" 
            @click="downloadDiagnosisReport" 
            :loading="isDownloadingReport"
            style="width: 100%;" 
          >
            <el-icon><Download /></el-icon>
            下载诊断报告
          </el-button>
        </div>
      </div>

      <!-- KNOWLEDGE PANEL -->
      <div class="panel-section knowledge-panel" v-if="knowledgeIsNotEmpty">
        <h4>相关知识</h4>
        <div class="knowledge-display-area">
          <!-- ChromaDB Knowledge -->
          <div v-if="selectedChat?.knowledge?.from_chroma && selectedChat.knowledge.from_chroma.source_nodes && selectedChat.knowledge.from_chroma.source_nodes.length > 0">
            <h5>向量知识库检索:</h5>
            <ul class="knowledge-list">
              <li v-for="node in selectedChat.knowledge.from_chroma.source_nodes" :key="node.id" class="knowledge-item chroma-item">
                <p><strong>标题:</strong> {{ node.title }}</p>
                <p><strong>相关度:</strong> {{ node.score ? node.score.toFixed(4) : 'N/A' }}</p>
                <p><strong>内容:</strong> {{ node.answer }}</p>
              </li>
            </ul>
          </div>

          <!-- Knowledge Graph Knowledge -->
          <div v-if="selectedChat?.knowledge?.from_kg && Object.keys(selectedChat.knowledge.from_kg).length > 0 && selectedChat.knowledge.from_kg['问诊']">
            <h5>知识图谱推理:</h5>
            <div class="knowledge-item kg-item">
              <p><strong>类型:</strong> {{ selectedChat.knowledge.from_kg['问诊'] === '是' ? '问诊咨询' : '普通信息查询' }}</p>
              
              <div v-if="selectedChat.knowledge.from_kg['核心回应']">
                <h6>核心回应:</h6>
                <template v-if="selectedChat.knowledge.from_kg['问诊'] === '是'">
                  <p><strong>最可能的疾病诊断:</strong> {{ selectedChat.knowledge.from_kg['核心回应']['最可能的疾病诊断'] }}</p>
                  <p><strong>诊断理由:</strong> {{ selectedChat.knowledge.from_kg['核心回应']['诊断理由'] }}</p>
                  <p><strong>所属科室:</strong> {{ selectedChat.knowledge.from_kg['核心回应']['所属科室'] }}</p>
                </template>
                <template v-if="selectedChat.knowledge.from_kg['问诊'] === '否'">
                  <p><strong>信息总结:</strong> {{ selectedChat.knowledge.from_kg['核心回应']['信息总结'] }}</p>
                  <p><strong>相关科室:</strong> {{ selectedChat.knowledge.from_kg['核心回应']['相关科室'] }}</p>
                </template>
              </div>

              <div v-if="selectedChat.knowledge.from_kg['补充信息'] && Object.keys(selectedChat.knowledge.from_kg['补充信息']).length > 0">
                <h6>补充信息:</h6>
                <ul class="supplementary-info-list">
                  <li v-for="(value, key) in selectedChat.knowledge.from_kg['补充信息']" :key="key">
                    <strong>{{ key }}:</strong> 
                    <span v-if="Array.isArray(value)">{{ value.join(', ') }}</span>
                    <span v-else>{{ value }}</span>
                  </li>
                </ul>
              </div>
              
              <p v-if="selectedChat.knowledge.from_kg['专业建议与重要提醒']">
                <strong>专业建议与重要提醒:</strong> {{ selectedChat.knowledge.from_kg['专业建议与重要提醒'] }}
              </p>
            </div>
          </div>
        </div>
      </div>
      <!-- END KNOWLEDGE PANEL -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, inject, nextTick, type Ref, provide } from 'vue'
import { ElButton, ElIcon, ElInput, ElTooltip, ElSelect, ElOption, ElSwitch, ElMessage } from 'element-plus'
import { 
  ChatDotRound, User, Delete, Service, Plus, Promotion, 
  Microphone, VideoPlay, Download
} from '@element-plus/icons-vue'
import PixiCanvas from './PixiCanvas.vue'
import axios from 'axios'
import { v4 as uuidv4 } from 'uuid';
// 获取用户信息
const userStore = inject<any>('userStore')
const userid = localStorage.getItem("userid")
// Inject WebSocket related items from MedicalQA.vue
const ws = inject<Ref<WebSocket | null> | undefined>('websocket');
const sendWsMessage = inject<(message: object) => void>('sendWebsocketMessage');
const wsMessages = inject<Ref<any[]> | undefined>('websocketMessages');

// 录音状态
const isRecording = ref(false)
const canRecord = ref(true)
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
// 下载报告按钮状态
const isDownloadingReport = ref(false)

// 注入animateMouth方法
const childAnimateMouthFn = ref<((duration: number) => void) | null>(null)
const resetModelFn = ref<(() => void) | null>(null)
const currentAudio = ref<HTMLAudioElement | null>(null)

provide('registerMouthAnimate', (animateMouthFn: (duration: number) => void) => {
  childAnimateMouthFn.value = animateMouthFn;
});

provide('registerResetModel', (resetFn: () => void) => {
  resetModelFn.value = resetFn;
});

const toggleRecording = async () => {
  if (isRecording.value) {
    // 停止录音
    stopRecording()
  } else {
    // 开始录音
    if (canRecord.value) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        startRecording(stream)
      } catch (err) {
        ElMessage.error('无法访问麦克风，请检查权限设置')
        console.error('录音错误:', err)
      }
    }
  }
}

const startRecording = (stream: MediaStream) => {
  audioChunks = []
  mediaRecorder = new MediaRecorder(stream)
  
  mediaRecorder.ondataavailable = (event: BlobEvent) => {
    if (event.data.size > 0) {
      audioChunks.push(event.data)
    }
  }
  
  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/mpeg' })
    await sendAudioToServer(audioBlob)
    stream.getTracks().forEach(track => track.stop())
    if (userInput.value && userInput.value.trim()) {
      sendMessage()
    }
  }
  
  mediaRecorder.start()
  isRecording.value = true
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    isRecording.value = false
  }
}

const sendAudioToServer = async (audioBlob: Blob) => {
  try {
    canRecord.value = false // 发送期间禁止录音
    
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.mp3')
    formData.append('audio', userStore.userid.value)
    const response = await axios.post('/agentapi/audio/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    userInput.value = response.data.query
    userInputSense.value = response.data.emotion_stats
    ElMessage.success('语音已成功处理')
    
  } catch (error) {
    ElMessage.error('语音处理失败')
    console.error('发送音频错误:', error)
  } finally {
    canRecord.value = true 
  }
}


const userInput = ref('')
const userInputSense = ref(null)
const isWaitingForResponse = ref(false)
const isNewSession = ref(false)

const settings = ref({
  autoPlayVoice: true,
})

const knowledgeIsNotEmpty = computed(() => {
  const currentChat = selectedChat.value;
  if (!currentChat || !currentChat.knowledge) {
    return false;
  }
  
  const { from_chroma, from_kg } = currentChat.knowledge;

  const chromaNotEmpty = from_chroma && 
                         from_chroma.source_nodes && 
                         Array.isArray(from_chroma.source_nodes) &&
                         from_chroma.source_nodes.length > 0;
                         
  const kgNotEmpty = from_kg && 
                     typeof from_kg === 'object' &&
                     Object.keys(from_kg).length > 0 &&
                     (from_kg['问诊'] === '是' || from_kg['问诊'] === '否');
  
  return chromaNotEmpty || kgNotEmpty;
});

const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}


const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}


const chatHistory = ref<Array<{
  session_id: string,
  title: string,
  createdAt: number,
  messages: Array<{
    role: string,
    content: string,
    timestamp: number
  }>,
  knowledge:{
    from_chroma: any,
    from_kg:any,
  }
}>>([])

// 当前选中的聊天
const selectedChatId = ref('')
const selectedChat = computed(() => {
  isNewSession.value = false
  return chatHistory.value.find(chat => chat.session_id === selectedChatId.value)
})

// 消息滚动引用
const messagesWrapper = ref<HTMLElement | null>(null)

// 选择聊天
const selectChat = (chatId: string) => {
  selectedChatId.value = chatId
}

// 删除聊天
const deleteChat = async (chatId: string) => {
  try {
    console.log(chatId)
    await axios.post(`/sessionapi/delete`, {
       userid:localStorage.getItem("userid"),
        sessionid: chatId,
       
    })
    
    // 删除成功后更新本地数据
    const index = chatHistory.value.findIndex(chat => chat.session_id === chatId)
    if (index !== -1) {
      chatHistory.value.splice(index, 1)
      if (selectedChatId.value === chatId && chatHistory.value.length > 0) {
        selectedChatId.value = chatHistory.value[0].session_id
      }
    }
    
    ElMessage.success('会话已删除')
  } catch (error) {
    ElMessage.error('删除会话失败')
    console.error('删除会话错误:', error)
  }
}

// 开始新会话
const startNewChat = async () => {
  try {
    // 添加到本地会话列表
    const newSessionId = uuidv4()
    chatHistory.value.unshift({
      session_id: newSessionId,
      title: "问诊会话：" + Date.now(),
      createdAt: Date.now(),
      messages: [
        {
          role: 'assistant',
          content: '您好，我是您的医疗助手。请告诉我您有什么症状（如头痛、发热等）或者您想要了解的健康问题，我将尽力为您提供专业的建议和信息。',
          timestamp: Date.now()
        }
      ],
      knowledge: {
        from_chroma:{},
        from_kg:{}
      }
    })
    // 选择新会话
    selectedChatId.value = newSessionId
    isNewSession.value = true
    ElMessage.success('新会话已创建')
  } catch (error) {
    ElMessage.error('创建新会话失败')
    console.error('创建会话错误:', error)
  } finally {
    isWaitingForResponse.value = false
  }
}


// 发送消息 - Modified to use WebSocket as primary
const sendMessage = async () => {
  if (isWaitingForResponse.value) {
    ElMessage.error("正在等待回复，暂时不能发送")
    return;
  }

  // 停止当前音频播放
  if (currentAudio.value) {
    currentAudio.value.pause()
    currentAudio.value.currentTime = 0
    currentAudio.value = null
  }
  
  // 重置模型状态
  if (resetModelFn.value) {
    resetModelFn.value()
  }

  const currentChat = selectedChat.value;
  if (!currentChat) {
    ElMessage.error("没有选中的会话!");
    return;
  }

  const userMessagePayload = {
    role: 'user' as const,
    content: userInput.value,
    timestamp: Date.now()
  };

  currentChat.messages.push(userMessagePayload);
  await nextTick(); // Ensure UI updates before proceeding
  if (messagesWrapper.value) {
    messagesWrapper.value.scrollTop = messagesWrapper.value.scrollHeight;
  }
  
  
  
  isWaitingForResponse.value = true;

  if (sendWsMessage && ws && ws.value && ws.value.readyState === WebSocket.OPEN) {

    sendWsMessage({
      type: "user_message",       
      messages: currentChat.messages,
      current_sense: userInputSense.value,
      sessionid: currentChat.session_id,  
      userid: userid,
      title: currentChat.title           
    });
  } else {
    ElMessage.error('WebSocket 未连接，无法发送消息。');
    const msgIdx = currentChat.messages.findIndex(m => m.timestamp === userMessagePayload.timestamp && m.content === userMessagePayload.content);
    if (msgIdx > -1) currentChat.messages.splice(msgIdx, 1);
    isWaitingForResponse.value = false;
    return; 
  }
  userInput.value = '';
  userInputSense.value = null;

};

watch(wsMessages || ref([]), (newMsgArray) => {
  if (!wsMessages || !wsMessages.value) return; 

  const currentChat = selectedChat.value;
  if (!currentChat) return;

  wsMessages.value.forEach(wsMsgData => {
    if (wsMsgData._processedByChatbot) return; // 简单标记避免重复处理

    console.log("ChatbotContainer 正在处理新的 WebSocket 消息:", wsMsgData);

    if (wsMsgData.type === "connection_established") {
      ElMessage.info(wsMsgData.message || "WebSocket 连接已确认。");
      wsMsgData._processedByChatbot = true;
      return;
    }

    if (wsMsgData.type === "knowledge_update") {
      console.log("收到知识更新消息，知识:", wsMsgData.knowledge);
      currentChat.knowledge.from_chroma = wsMsgData.knowledge.knowledge_from_chroma
      currentChat.knowledge.from_kg = wsMsgData.knowledge.knowledge_from_graph
      wsMsgData._processedByChatbot = true;
      return;
    }

    // 处理语音消息
    if (wsMsgData.type === "voice") {
      console.log("收到语音消息，URL:", wsMsgData.voice_file_url);

      if (settings.value.autoPlayVoice && wsMsgData.voice_file_url) {
        const audio = new Audio(wsMsgData.voice_file_url);
        currentAudio.value = audio;  // 保存音频引用
        console.log("starting audio play")
        isWaitingForResponse.value = true
        audio.play().then(() => {
          console.log("starting animate mouth")
          if (childAnimateMouthFn.value) {
            childAnimateMouthFn.value(audio.duration * 1000); // 转换为毫秒
          }
        }).catch(err => {
          console.error("播放语音失败:", err);
          ElMessage.error("语音播放失败");
        });
      }
      
      wsMsgData._processedByChatbot = true;
      return;
    }
    
    // 处理文本消息
    if (wsMsgData.type === "text") {
      if (!wsMsgData.sender || typeof wsMsgData.text === 'undefined') {
        console.warn("收到的 WebSocket 文本消息格式不正确，已跳过:", wsMsgData);
        wsMsgData._processedByChatbot = true;
        return;
      }
      
      const role = 'assistant' 
      if (role === 'assistant') {
        const messageToAdd = {
            role: role,
            content: wsMsgData.text,
            timestamp: wsMsgData.timestamp 
        };

        const messageExists = currentChat.messages.some(
            msg => msg.content === messageToAdd.content && 
                  msg.role === messageToAdd.role && 
                  Math.abs(msg.timestamp - messageToAdd.timestamp) < 2000 
        );

        if (!messageExists) {
            currentChat.messages.push(messageToAdd);
            isWaitingForResponse.value = false; 
            nextTick(() => {
              if (messagesWrapper.value) {
                messagesWrapper.value.scrollTop = messagesWrapper.value.scrollHeight;
              }
            });
        } else {
            console.log("WebSocket 消息 (助手) 已显示或非常相似，已跳过:", messageToAdd);
        }
        wsMsgData._processedByChatbot = true;
      }
      return;
    }

    console.warn("收到未知类型的WebSocket消息:", wsMsgData);
    wsMsgData._processedByChatbot = true;
  });

}, { deep: true }); 


watch(() => selectedChat.value?.messages.length, async () => {
  await nextTick(); 
  if (messagesWrapper.value) {
    messagesWrapper.value.scrollTop = messagesWrapper.value.scrollHeight;
  }
}, { deep: true }); 

const fetchSessions = async () => {
  try {
    isWaitingForResponse.value = true
    
    const response = await axios.get('/sessionapi/all', {
      params: { userid: localStorage.getItem("userid") }
    })
    
    const sessions_data = response.data
    console.log(response.data)
    if (sessions_data.length > 0){
      const sessions = sessions_data.sort((a: any, b: any) => b.timestamp - a.timestamp)
      chatHistory.value = sessions.map((session: any) => ({
        session_id: session.session_id,
        title: session.title,
        createdAt: session.timestamp,
        messages: session.messages || [],
        knowledge: {
          from_chroma: session.knowledge.knowledge_from_chroma,
          from_kg: session.knowledge.knowledge_from_graph

        }
      }))
    }
    else{
      chatHistory.value = []
    }
    
    if (chatHistory.value.length > 0) {
      selectedChatId.value = chatHistory.value[0].session_id
    } else {
      await startNewChat()
    }
  } catch (error) {
    ElMessage.error('获取会话列表失败')
    console.error('获取会话错误:', error)
  } finally {
    isWaitingForResponse.value = false
  }
}

const downloadDiagnosisReport = async () => {
  if (!selectedChat.value || !selectedChat.value.session_id) {
    ElMessage.error('未选择会话或会话ID无效');
    return;
  }

  if (!userid) { 
    ElMessage.error('用户ID无效');
    return;
  }

  isDownloadingReport.value = true;
  try {
    const response = await axios.get(`/agentapi/download-pdf`, {
      params: {
        userid: localStorage.getItem("userid"),
        sessionid: selectedChat.value.session_id
      },
      responseType: 'blob'
    });

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    const contentDisposition = response.headers['content-disposition'];
    let filename = '诊断报告.pdf'; 
    if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+?)"?(;|$)/i);
        if (filenameMatch && filenameMatch[1]) {
            filename = decodeURIComponent(filenameMatch[1]);
        }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    ElMessage.success('诊断报告已开始下载');

  } catch (error) {
    console.error('下载诊断报告失败:', error);
    ElMessage.error('下载诊断报告失败，请稍后再试');
  } finally {
    isDownloadingReport.value = false;
  }
};

onMounted(() => {
  fetchSessions()
})
</script>

<style scoped>
.chatbot-container {
  display: flex;
  height: 100%;
  gap: 15px;
}

.glass-card {
  background: var(--bg-color-glass);
  border-radius: var(--border-radius);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: var(--glass-border);
  box-shadow: var(--box-shadow);
}

/* 左侧消息列表 */
.message-list-container {
  width: 20%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.message-list-header {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-list-header h3 {
  margin: 0;
  font-weight: 500;
  color: var(--text-color-primary);
}

.new-chat-btn {
  font-size: 0.9em;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.chat-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: var(--border-radius);
  cursor: pointer;
  background-color: rgba(255, 255, 255, 0.3);
  transition: all var(--transition-speed) ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-item:hover {
  background-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.chat-item.active {
  background-color: rgba(0, 170, 255, 0.1);
  border-left: 3px solid var(--primary-color);
}

.chat-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 5px;
}

.chat-date {
  font-size: 0.8em;
  color: var(--text-color-secondary);
}

.chat-actions {
  opacity: 0;
  transition: opacity var(--transition-speed) ease;
}

.chat-item:hover .chat-actions {
  opacity: 1;
}

/* 中间聊天区域 */
.chat-main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
}

.pixi-container {
  height: 300px;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 15px;
  border-radius: 18px;
  animation: fadeIn 0.3s ease;
  position: relative;
}

.user-message {
  align-self: flex-end;
  background-color: rgba(0, 170, 255, 0.1);
  border-bottom-right-radius: 5px;
}

.bot-message {
  align-self: flex-start;
  background-color: rgba(255, 255, 255, 0.5);
  border-bottom-left-radius: 5px;
}

.message-sender {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 8px;
}

.avatar.user {
  background-color: var(--primary-color);
  color: white;
}

.avatar.assistant {
  background-color: var(--secondary-color);
  color: white;
}

.sender-name {
  font-size: 0.85em;
  font-weight: 500;
}

.message-content {
  line-height: 1.5;
  word-break: break-word;
}

.message-time {
  font-size: 0.75em;
  color: var(--text-color-secondary);
  text-align: right;
  margin-top: 5px;
}

.message-input {
  padding: 15px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 10px;
}

.message-input .el-input {
  flex: 1;
}

.input-actions {
  display: flex;
  align-items: flex-end;
}

/* 右侧控制面板 */
.control-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
}

.panel-header h3 {
  margin: 0;
  font-weight: 500;
  color: var(--text-color-primary);
}

.panel-section {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
}

.panel-section h4 {
  margin: 0 0 15px 0;
  font-weight: 500;
  color: var(--text-color-primary);
}

.voice-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.record-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.record-btn.is-recording {
  animation: pulse 2s infinite;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
}

.record-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  background-color: #f56c6c;
  border-radius: 50%;
  animation: blink 1s infinite;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

/* Knowledge Panel Styles */
.knowledge-panel {
  flex: 1; 
  min-height: 0; 
  display: flex; 
  flex-direction: column;
  border-bottom: none; /* Override default border for panel-section if it's the last one */
}

.knowledge-panel h4 {
  margin: 0 0 10px 0;
}

.knowledge-display-area {
  flex: 1; 
  overflow-y: auto;
  padding: 10px;
  border: 1px solid var(--border-color-light, #e0e0e0); 
  border-radius: var(--border-radius-small, 4px); 
  background-color: rgba(255, 255, 255, 0.05); 
}

.knowledge-display-area h5 {
  margin-top: 0; 
  margin-bottom: 8px;
  color: var(--text-color-primary);
  font-weight: 500;
  padding-bottom: 5px;
  border-bottom: 1px solid var(--border-color-light, #e0e0e0);
}
.knowledge-display-area h6 {
  margin-top: 12px;
  margin-bottom: 6px;
  color: var(--text-color-primary);
  font-weight: 500;
  font-size: 0.95em;
}

.knowledge-list, .supplementary-info-list {
  list-style-type: none;
  padding-left: 0; 
}

.knowledge-item {
  margin-bottom: 12px;
  padding: 10px;
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: var(--border-radius-small, 4px);
  font-size: 0.9em;
}

.chroma-item {
  border-left: 3px solid var(--el-color-success, #67C23A); 
}
.kg-item {
   border-left: 3px solid var(--el-color-warning, #E6A23C); 
}

.knowledge-item p {
  margin: 5px 0;
  line-height: 1.4;
  word-break: break-word; /* Ensure long words break */
}
.knowledge-item strong {
   color: var(--text-color-primary);
}

.supplementary-info-list li {
  margin-bottom: 5px;
  font-size: 0.9em;
}
/* END Knowledge Panel Styles */

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(245, 108, 108, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0); }
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.3; }
  100% { opacity: 1; }
}
</style> 