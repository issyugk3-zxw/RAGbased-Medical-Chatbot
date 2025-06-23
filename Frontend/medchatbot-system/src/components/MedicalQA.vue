<template>
  <div class="medical-qa-container">
    <Sidebar @navigate="navigateTo" class="sidebar-section" />
    <div class="content-section glass-panel">
      <keep-alive>
        <component :is="activeComponent" />
      </keep-alive>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  shallowRef,
  markRaw,
  inject,
  provide,
  onMounted,
  onUnmounted,
  watch
} from 'vue';
import type { Ref } from 'vue'; 
import Sidebar from './Sidebar.vue'
import SelfContainer from './SelfContainer.vue'
import ChatbotContainer from './ChatbotContainer.vue'


interface UserStore {
  userid: Ref<string>;
  isLoggedIn: Ref<boolean>;
  self_info: Ref<object>;
  health_info: Ref<object>;
  setUser: (id: string) => void;
  clearUser: () => void;
  setSelfInfo: (info: any) => void;
  getSelfInfo: () => object;
  setHealthInfo: (info: any) => void;
  getHealthInfo: () => object;
}

const userStore = inject('userStore') as UserStore | undefined;


const components = {
  self: markRaw(SelfContainer),
  chatbot: markRaw(ChatbotContainer)
}


const activeComponent = shallowRef(components.chatbot)


const navigateTo = (componentKey: string) => {
  console.log(`尝试导航到: ${componentKey}`);
  if (componentKey === 'self' || componentKey === 'chatbot') {
    const targetComponent = components[componentKey as keyof typeof components];
    if (targetComponent) {
      activeComponent.value = targetComponent;
      console.log(`成功切换 activeComponent 为:`, activeComponent.value);
    } else {
      console.error(`未找到组件映射: ${componentKey}`);
    }
  } else {
    console.error(`无效的组件键: ${componentKey}`);
  }
};


const websocket = ref<WebSocket | null>(null);
const websocketMessages = ref<any[]>([]); 
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectInterval = 5000; // 5 seconds

const setupWebSocket = () => {
  const userId = localStorage.getItem('userid');
  const wsUrl = `ws://localhost:8086/ws/chat/${userId}/`;
  console.log(`正在尝试连接 WebSocket: ${wsUrl}`);
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('WebSocket 连接已建立.');
    websocket.value = ws;
    reconnectAttempts = 0; 

  };

  ws.onmessage = (event) => {
    console.log('收到 WebSocket 消息:', event.data);
    try {
      const message = JSON.parse(event.data as string);
      websocketMessages.value.push(message); 
    } catch (e) {
      console.error('解析 WebSocket 消息失败:', e);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);

  };

  ws.onclose = (event) => {
    console.log('WebSocket 连接已关闭:', event);
    websocket.value = null;
    if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      console.log(`WebSocket 连接意外关闭。将在 ${reconnectInterval / 1000} 秒后尝试重新连接 (尝试次数 ${reconnectAttempts}/${maxReconnectAttempts})...`);
      setTimeout(setupWebSocket, reconnectInterval);
    } else if (reconnectAttempts >= maxReconnectAttempts) {
      console.error('已达到最大 WebSocket 重新连接尝试次数。');
    }
  };
};

console.log(userStore)
if (userStore && userStore.userid) {
    
      setupWebSocket();
    
} else {
   console.warn('userStore or userStore.userid not available on mount. WebSocket setup might be delayed or fail.');
}

onUnmounted(() => {
  if (websocket.value) {
    websocket.value.onclose = null; 
    websocket.value.close();
    console.log('WebSocket connection closed on component unmount.');
  }
});


provide<Ref<WebSocket | null>>('websocket', websocket);
provide('sendWebsocketMessage', (message: object) => {
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    websocket.value.send(JSON.stringify(message));
  } else {
    console.error('WebSocket 未连接或未准备好发送消息。');

  }
});
provide<Ref<any[]>>('websocketMessages', websocketMessages);
</script>

<style scoped>
html, body {
  width: 100%;
  height: 100%;
  padding: 0 ;

  margin: 0;
}
.medical-qa-container {
  display: flex;
  height: 100%;
  width: 100%;
  background-color: var(--bg-color-main);
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.03) 0%, transparent 20%),
    radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.03) 0%, transparent 20%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.01) 0%, transparent 100%);
  box-sizing: border-box;
  padding: 15px;
  overflow: hidden;
}

.sidebar-section {
  width: 80px;
  height: 100%;
  margin-right: 15px;
  flex-shrink: 0;
  z-index: 10;
}

.content-section {
  flex: 1;
  height: 100%;
  overflow: hidden;
  border-radius: var(--border-radius);
  box-sizing: border-box;
  padding: 0;
  position: relative;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.content-section::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: var(--border-radius);
  box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.05);
  pointer-events: none;
}
</style> 