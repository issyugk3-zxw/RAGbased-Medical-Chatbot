<template>
  <div class="canvas-container glass-card">
    <div class="canvas-wrapper">
      <canvas ref="myCanvas" class="live2d-canvas" />
      <div class="canvas-overlay">
        <div class="overlay-gradient"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, inject } from 'vue'
import * as PIXI from 'pixi.js'
import { Live2DModel } from 'pixi-live2d-display/cubism4'

// 初始化 Live2D 运行时
// @ts-ignore
declare global {
  interface Window {
    PIXI: typeof PIXI;
  }
}
window.PIXI = PIXI

const myCanvas = ref<HTMLCanvasElement | null>(null)
let app: PIXI.Application | null = null
const model = ref<any>(null)
let mouthAnimationInterval: number | null = null
let handAnimationInterval: number | null = null
const registerMouthAnimate = inject('registerMouthAnimate')
const registerResetModel = inject('registerResetModel')

// 添加鼠标位置跟踪
const mousePosition = ref({ x: 0, y: 0 })
const targetMousePosition = ref({ x: 0, y: 0 })

// 更新鼠标位置
const updateMousePosition = (event: MouseEvent) => {
  if (!myCanvas.value) return
  
  const rect = myCanvas.value.getBoundingClientRect()
  const x = (event.clientX - rect.left) / rect.width
  const y = (event.clientY - rect.top) / rect.height
  
  targetMousePosition.value = {
    x: (x - 0.5) * 2, // 转换为 -1 到 1 的范围
    y: (y - 0.5) * 2
  }
}


const init = async () => {
  if (!myCanvas.value) return

  // 创建 PIXI 应用
  app = new PIXI.Application({
    view: myCanvas.value,
    resizeTo: myCanvas.value,
    backgroundAlpha: 0,
    antialias: true,
  })

  try {
    // 加载模型
    model.value = await Live2DModel.from('/live2d/models/greeter/haru_greeter_t05.model3.json', {
      autoInteract: false
    })

    // 调整模型大小和位置
    model.value.scale.set(0.15)
    model.value.x = 130
    model.value.y = 10

    // 添加到舞台
    app.stage.addChild(model.value)
    console.log("live2d model added")
    
    console.log(model.value.internalModel.coreModel)
    const params = {
      "ParamArmLA": 1,
      "ParamArmLB": 3,
      "ParamArmRA": -0.2,
      "ParamArmRB": 0.1,
    }
    
    // 检查每个参数是否存在
    for (const [paramId, value] of Object.entries(params)) {
      model.value.internalModel.coreModel.setParameterValueById(paramId, value)
      console.log(model.value.internalModel.coreModel.getParameterValueById(paramId))
    }
    
    
    // 启动参数更新循环
    updateModelParameters()
    
  } catch (error) {
    console.error('模型加载失败:', error)
  }
}

// 修改手部动作控制
const animateHands = (duration: number) => {
  if (!model.value) return
  
  // 清除之前的手部动画
  if (handAnimationInterval) {
    clearInterval(handAnimationInterval)
  }
  
  const startTime = Date.now()
  const endTime = startTime + duration
  
  // 设置初始思考姿势
  try {
    // 尝试设置手部参数
    const params = {
      "ParamArmLA": 1,
      "ParamArmLB": 3,
      "ParamArmRA": -0.2,
      "ParamArmRB": 0.1,
    }
    
    // 检查每个参数是否存在
    for (const [paramId, value] of Object.entries(params)) {
      model.value.internalModel.coreModel.setParameterValueById(paramId, value)
    }
  } catch (error) {
    console.error('设置手部参数失败:', error)
  }
  
  handAnimationInterval = setInterval(() => {
    const currentTime = Date.now()
    if (currentTime >= endTime) {
      clearInterval(handAnimationInterval!)
      handAnimationInterval = null
      // 恢复默认姿势
      try {
        const params = {
          "ParamArmLA": 1,
          "ParamArmLB": 3,
          "ParamArmRA": -0.2,
          "ParamArmRB": 0.1,
        }
        for (const [paramId, value] of Object.entries(params)) {
          model.value.internalModel.coreModel.setParameterValueById(paramId, value)
        
        }
      } catch (error) {
        console.error('重置手部参数失败:', error)
      }
      return
    }
    
    // 生成随机的手部动作
    const time = (currentTime - startTime) / 1000
    try {
      const params = {
        "ParamArmLA": 2 + Math.sin(time * 2) * 3,
        "ParamArmLB": 0.5 + Math.cos(time * 1.5) * 1,
        "ParamArmRA": -2 + Math.sin(time * 2.2) * 1,
        "ParamArmRB": 0.5 + Math.cos(time * 1.7) * 1
      }
      
      for (const [paramId, value] of Object.entries(params)) {
         console.log(paramId, value)
         model.value.internalModel.coreModel.setParameterValueById(paramId, value)
       
      }
    } catch (error) {
      console.error('更新手部参数失败:', error)
    }
  }, 50)
}

// 修改原有的animateMouth函数，添加手部动作
const animateMouth = (duration: number) => {
  if (!model.value) return
  
  // 清除之前的动画
  if (mouthAnimationInterval) {
    clearInterval(mouthAnimationInterval)
  }
  
  const startTime = Date.now()
  const endTime = startTime + duration
  
  // 启动手部动作
  animateHands(duration)
  
  mouthAnimationInterval = setInterval(() => {
    const currentTime = Date.now()
    if (currentTime >= endTime) {
      clearInterval(mouthAnimationInterval!)
      mouthAnimationInterval = null
      // 停止时关闭嘴巴
      model.value.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", 0)
      return
    }
    
    // 生成0到1之间的随机值来模拟说话动作
    const mouthValue = Math.random() * 0.5 + 0.2 // 0.2到0.7之间的随机值
    model.value.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", mouthValue)
  }, 100) // 每100ms更新一次
}

// 重置模型状态的方法
const resetModelState = () => {
  // 停止所有动画
  if (mouthAnimationInterval) {
    clearInterval(mouthAnimationInterval)
    mouthAnimationInterval = null
  }
  if (handAnimationInterval) {
    clearInterval(handAnimationInterval)
    handAnimationInterval = null
  }
  
  // 重置模型参数到初始状态
  if (model.value) {
    model.value.internalModel.coreModel.setParameterValueById("ParamMouthOpenY", 0)
    // 重置手部参数
    const params = {
      "ParamArmLA": 1,
      "ParamArmLB": 3,
      "ParamArmRA": -0.2,
      "ParamArmRB": 0.1,
    }
    for (const [paramId, value] of Object.entries(params)) {
      model.value.internalModel.coreModel.setParameterValueById(paramId, value)
    }
  }
}

if (registerMouthAnimate){
  registerMouthAnimate(animateMouth)
}

// 生命周期钩子
onMounted(() => {
  init()
  // 添加鼠标移动事件监听
  // 注册重置方法
  if (registerResetModel) {
    registerResetModel(resetModelState)
  }
})

onBeforeUnmount(() => {
  if (app) {
    app.destroy(true)
    app = null
  }
  if (mouthAnimationInterval) {
    clearInterval(mouthAnimationInterval)
  }
  if (handAnimationInterval) {
    clearInterval(handAnimationInterval)
  }
  // 移除鼠标移动事件监听
  window.removeEventListener('mousemove', updateMousePosition)
  model.value = null
})
</script>

<style scoped>
.canvas-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.glass-card {
  background: rgba(255, 255, 255, 0.08);
  border-radius: var(--border-radius);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.live2d-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.canvas-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.overlay-gradient {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 150px;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.05) 100%
  );
}

/* 添加发光效果 */
.canvas-container::after {
  content: "";
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  z-index: -1;
  border-radius: calc(var(--border-radius) + 10px);
  background: radial-gradient(
    circle at center,
    rgba(var(--primary-color-rgb, 0, 170, 255), 0.03) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.5s ease;
}

.canvas-container:hover::after {
  opacity: 1;
}

.control-panel {
  padding: 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.control-card {
  background: transparent;
  border: none;
  transition: transform var(--transition-speed);
}

.control-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-color);
}

.control-content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 12px 0;
}

.voice-control {
  display: flex;
  gap: 12px;
}

.record-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 16px;
  transition: all var(--transition-speed);
}

.record-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.record-btn.is-recording {
  animation: recording-pulse 2s infinite;
}

.record-icon {
  font-size: 20px;
}

.record-icon.pulse {
  animation: icon-pulse 1s infinite;
}

@keyframes recording-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(245, 108, 108, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

@keyframes icon-pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

:deep(.el-card__body) {
  padding: 0;
}
</style> 