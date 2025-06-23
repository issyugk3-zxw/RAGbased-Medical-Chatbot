<template>
  <div class="sidebar-container glass-card">
    <div class="sidebar-menu">
      <div 
        v-for="(item, index) in menuItems"
        :key="index"
        class="tooltip-wrapper"
      >
        <el-tooltip
          
          :content="item.label"
          placement="right"
          effect="light"
          :offset="12"
          
        >
          <el-button
            class="menu-item"
            circle
            :class="{ active: index === activeIndex }"
            @click.stop="handleItemClick(index, item.key)" 
          >
            <el-icon>
              <component :is="item.icon"></component>
            </el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
    
    <div class="sidebar-footer">
      <div class="tooltip-wrapper">
        <el-tooltip content="设置" placement="right" effect="light" :offset="12">
          <el-button class="menu-item" circle @click.stop="showSettings">
            <el-icon><Setting /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  ChatDotRound, User, 
  Setting, QuestionFilled // QuestionFilled 可能不再需要，但暂时保留以防万一
} from '@element-plus/icons-vue'

// 定义菜单项
const menuItems = [
  { key: 'chatbot', label: '智能对话', icon: ChatDotRound },
  { key: 'self', label: '个人信息', icon: User }
]

// 当前激活的菜单项
const activeIndex = ref(0) // 默认激活第一项（智能对话）

// 点击菜单项
const handleItemClick = (index: number, key: string) => {
  activeIndex.value = index
  emit('navigate', key)
}

// 定义事件
const emit = defineEmits<{
  (e: 'navigate', key: string): void
}>()

// 显示设置
const showSettings = () => {
  console.log('打开设置')
  // 这里可以添加设置面板的逻辑
}

// 帮助函数已移除

</script>

<style scoped>
.sidebar-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px 0;
  box-sizing: border-box;
}

.glass-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.tooltip-wrapper {
  display: flex;
  justify-content: center;
  width: 100%; /* 确保wrapper占据全部宽度以居中 */
}

.sidebar-menu, .sidebar-footer {
  display: flex;
  flex-direction: column;
  align-items: center; /* 让wrapper在容器中居中 */
  gap: 15px;
  width: 100%; /* 确保容器本身也占据宽度 */
}

/* .menu-item-wrapper {
  margin-bottom: 10px;
  width: 100%;
  display: flex;
  justify-content: center;
  cursor: pointer;
} */

.menu-item {
  width: 48px !important;
  height: 48px !important;
  border-radius: 50% !important;
  font-size: 20px;
  padding: 0 !important;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  color: var(--text-color-primary);
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  box-sizing: border-box !important;
  transition: all var(--transition-speed) cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: pointer;
  z-index: 5;
}

.menu-item:hover {
  transform: translateY(-2px);
  background: rgba(var(--primary-color-rgb), 0.1);
  color: var(--primary-color);
  border-color: rgba(var(--primary-color-rgb), 0.2);
  box-shadow: 0 5px 15px rgba(var(--primary-color-rgb), 0.1);
}

.menu-item.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.sidebar-footer {
  margin-top: auto;
}

/* 深度选择器处理内部元素 */
:deep(.el-button.menu-item .el-icon) {
  margin: 0;
  font-size: inherit;
}

/* hover特效 - 恢复 */
.menu-item:not(.active)::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  padding: 2px;
  background: linear-gradient(
    135deg, 
    rgba(var(--primary-color-rgb), 0.5),
    rgba(var(--primary-color-rgb), 0)
  );
  mask: linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);
  -webkit-mask: linear-gradient(#fff 0 0) content-box,
              linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask-composite: xor;
  opacity: 0;
  transition: opacity var(--transition-speed) ease;
}

.menu-item:hover::after {
  opacity: 1;
}
</style> 