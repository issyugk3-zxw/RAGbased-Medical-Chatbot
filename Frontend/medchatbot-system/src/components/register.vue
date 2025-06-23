<template>
  <div class="register-container">
    <div class="register-box">
      <h2>注册</h2>
      <div class="input-group">
        <input type="text" v-model="userid" placeholder="请输入账号" />
      </div>
      <div class="input-group">
        <input type="password" v-model="password" placeholder="请输入密码" />
      </div>
      <div class="input-group">
        <input type="password" v-model="confirmPassword" placeholder="请确认密码" />
      </div>
      <button @click="submit">注册</button>
      <div class="login-link">
        <router-link to="/login">已有账号？立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
  import { inject } from 'vue'
  import { useRouter } from 'vue-router'
export default {
  name: 'Register',

  setup() {
    const userStore = inject('userStore')
    const router = useRouter()
    return { userStore, router }
  },
  data() {
    return {
      userid: '',
      password: '',
      confirmPassword: ''
    }
  },
  methods: {
    submit() {
      if (this.password !== this.confirmPassword) {
        alert('两次输入的密码不一致！')
        return
      }
      this.$axios.post('/userapi/register/', {"userid": this.userid, "password": this.password})
        .then((response) => {
          alert(response.data.msg)
          if (response.data.status === 'success') {  
            this.userStore.setUser(this.userid)
            this.userStore.setSelfInfo({})
            this.userStore.setHealthInfo([])
            this.router.push('/MedicalQA')
          }
        })
    }
  }
}
</script>

<style scoped>
html, body, #app, .register-container {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.register-container {
  min-height: 100vh;
  min-width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
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

.register-box {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  border-radius: 18px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  width: 100%;
  max-width: 380px;
  animation: fadeIn 1s;
  border: 1.5px solid rgba(255,255,255,0.3);
  margin: 0 auto;
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

.login-link {
  text-align: center;
  margin-top: 1.5rem;
}

.login-link a {
  color: #4f8cff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.login-link a:hover {
  color: #a084ee;
  text-decoration: underline;
}
</style>