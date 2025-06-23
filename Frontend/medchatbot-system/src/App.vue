<script setup lang="ts">

import 'element-plus/dist/index.css'
import { useUserStore } from './pinia/user';
import { provide } from 'vue';
const userStore = useUserStore();
provide('userStore', userStore);
</script>

<template>
  <router-view />
</template>

<style>
:root {
  /* 主题颜色 - 浅色系 */
  --primary-color: #00aaff; /* 天蓝色 */
  --primary-color-light: #66ccff;
  --primary-color-dark: #0088cc;
  --secondary-color: #a0b1c2; /* 灰色 */
  --accent-color: #87ceeb; /* 浅天蓝 */

  --bg-color-main: #f4f7fa; /* 非常浅的灰蓝色 */
  --bg-color-glass: rgba(255, 255, 255, 0.7); /* 白色玻璃 */
  --bg-color-card: #ffffff; /* 白色卡片 */
  --bg-color-input: #e9edf1;
  --bg-gradient: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%); /* 白色到爱丽丝蓝 */

  /* 文本颜色 - 浅色系 */
  --text-color-primary: #303133; /* 深灰色 */
  --text-color-secondary: #606266; /* 常规灰色 */
  --text-color-placeholder: #909399; /* 浅灰色 */
  --text-color-light: #ffffff; /* 用于深色背景元素 */
  --text-color-link: var(--primary-color);

  /* 边框和阴影 - 浅色系 */
  --border-radius: 12px;
  --border-color: rgba(0, 0, 0, 0.1);
  --box-shadow: 0 6px 24px rgba(0, 0, 0, 0.05);
  --box-shadow-hover: 0 8px 32px rgba(0, 0, 0, 0.08);
  --glass-border: 1px solid rgba(0, 0, 0, 0.08);

  /* 过渡效果 */
  --transition-speed: 0.3s;
}

html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  box-sizing: border-box; /* Apply globally */
  overflow: hidden; /* Prevent potential scrollbars on body */
}

html, body {
  font-family: 'Noto Sans SC', 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-color-main);
  color: var(--text-color-primary);
}

/* 滚动条美化 - 浅色 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* 全局动画类 (保持不变) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-speed) ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform var(--transition-speed) ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(-20px);
}

</style>
