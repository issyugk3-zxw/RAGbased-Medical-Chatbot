import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './style.css'
import App from './App.vue'
import router from './router' 
import { createPinia } from 'pinia'
import axios from 'axios'
const app = createApp(App)
const pinia = createPinia()

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
axios.defaults.baseURL = "http://localhost:8085"
app.config.globalProperties.$axios = axios

app.use(pinia)
app.use(router) 
app.use(ElementPlus)
app.mount('#app')
