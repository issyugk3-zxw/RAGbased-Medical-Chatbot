import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userid = ref('')
  const self_info = ref({})
  const health_info = ref({})
  const isLoggedIn = ref(false)

  // 设置用户信息
  function setUser(id: string) {
    userid.value = id
    isLoggedIn.value = true

    localStorage.setItem('userid', id)
    localStorage.setItem('isLoggedIn', 'true')
  }
  function setSelfInfo(info: any) {
    self_info.value = info
  }
  function getSelfInfo() {
    return self_info.value
  }
  function setHealthInfo(info: any) {
    health_info.value = info
  }
  function getHealthInfo() {
    return health_info.value
  }
  // 清除用户信息
  function clearUser() {
    userid.value = ''
    isLoggedIn.value = false
    // 清除localStorage
    localStorage.removeItem('userid')
    localStorage.removeItem('isLoggedIn')
  }

  // 初始化时从localStorage加载数据
  function initUser() {
    const savedUserid = localStorage.getItem('userid')
    const savedIsLoggedIn = localStorage.getItem('isLoggedIn')
    if (savedUserid && savedIsLoggedIn === 'true') {
      userid.value = savedUserid
      isLoggedIn.value = true
    }
  }

  // 初始化
  initUser()

  return {
    userid,
    isLoggedIn,
    setUser,
    clearUser,
    setSelfInfo,
    self_info,
    setHealthInfo,
    health_info,
    getSelfInfo,
    getHealthInfo
  }
}) 