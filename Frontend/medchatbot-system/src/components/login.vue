<template>
  <div class="login-container">
    <div class="login-box">
      <h2>登录</h2>
      <div class="input-group">
        <input type="text" v-model="userid" placeholder="请输入账号" />
      </div>
      <div class="input-group">
        <input type="password" v-model="password" placeholder="请输入密码" />
      </div>
      <button @click="submit">登录</button>
      <div class="register-link">
        <router-link to="/register">还没有账号？立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { inject } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const userStore = inject('userStore')
    const router = useRouter()
    return { userStore, router }
  },
  data() {
    return {
      userid: '',
      password: ''
    }
  },
  methods: {
    submit() {
      this.$axios.post('/userapi/login/', {"userid": this.userid, "password": this.password})
        .then((response) => {
          if (response.data.status === 'success') {  
            console.log("login success")
            this.userStore.setUser(response.data.userid)
            this.$axios.get('/userapi/getSelfInfo/', { params: { "userid": this.userid } })
            .then((response) => {
              console.log("response.data", response.data)
              this.userStore.setSelfInfo(response.data.info)
            })
            this.$axios.get('/userapi/getHealthInfo/', { params: { "userid": this.userid } })
            .then((response) => {
              this.userStore.setHealthInfo(response.data.info)
            })
            this.router.push('/MedicalQA')
          }
          alert(response.data.msg)
        })
        .catch((error) => {
          alert('登录失败：' + error.message)
        })
    }
  }
}
</script>

<style scoped>
html, body, #app, .login-container {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  min-height: 100vh;
  min-width: 100vw;
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

@keyframes bgMove {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}

.login-box {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  border-radius: 18px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  width: 100%;
  max-width: 380px;
  animation: fadeIn 1s;
  border: 1.5px solid rgba(255,255,255,0.3);
  margin: 0 auto; /* 添加自动外边距 */
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(40px);}
  to { opacity: 1; transform: translateY(0);}
}

h2 {
  text-align: center;
  color: #2d3a4b;
  margin-bottom: 2rem;
  font-weight: 700;
  letter-spacing: 2px;
}

.input-group {
  margin-bottom: 1.5rem;
}

input {
  width: 100%;
  padding: 13px 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  background: rgba(255,255,255,0.85);
  box-shadow: 0 2px 8px rgba(80, 120, 255, 0.07);
  transition: box-shadow 0.3s, background 0.3s;
  outline: none;
  margin-bottom: 2px;
}

input:focus {
  background: #eaf1ff;
  box-shadow: 0 0 0 2px #7b9fff;
}

button {
  width: 100%;
  padding: 13px;
  background: linear-gradient(90deg, #4f8cff 0%, #a084ee 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
  box-shadow: 0 2px 8px rgba(80, 120, 255, 0.13);
  transition: background 0.3s, transform 0.2s;
}

button:hover {
  background: linear-gradient(90deg, #6fa8ff 0%, #bfa4ff 100%);
  transform: translateY(-2px) scale(1.03);
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
}

.register-link a {
  color: #4f8cff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.register-link a:hover {
  color: #a084ee;
  text-decoration: underline;
}
</style>