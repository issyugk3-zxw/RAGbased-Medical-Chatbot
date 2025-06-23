import { createRouter, createWebHistory } from 'vue-router'
import login from '../components/login.vue' //导入login组件
import register from '../components/register.vue' //导入register组件
import MedicalQA from '../components/MedicalQA.vue'
import { useUserStore } from '../pinia/user'

//配置组件及路径的对应关系
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    component: register,
    meta: { requiresAuth: false }
  },
  {
    path: '/MedicalQA',
    component: MedicalQA,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 全局路由守卫
router.beforeEach(async (to, from, next) => {
  // 从 localStorage 直接检查登录状态
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  
  // 如果路由需要认证且用户未登录
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router //将路由配置导出
