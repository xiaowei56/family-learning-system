<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="app-title">家庭学习系统</h1>
      <p class="app-subtitle">为您的孩子打造专属的学习空间</p>
      
      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" @submit.prevent="handleLogin">
            <el-form-item prop="username">
              <template #label>
                <el-icon class="mr-5"><User /></el-icon>
                用户名
              </template>
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名"
                size="large"
                clearable
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <template #label>
                <el-icon class="mr-5"><Lock /></el-icon>
                密码
              </template>
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                size="large" 
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" @submit.prevent="handleRegister">
            <el-form-item prop="username">
              <template #label>
                <el-icon class="mr-5"><User /></el-icon>
                用户名
              </template>
              <el-input 
                v-model="registerForm.username" 
                placeholder="请输入用户名"
                size="large"
                clearable
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <template #label>
                <el-icon class="mr-5"><Lock /></el-icon>
                密码
              </template>
              <el-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="请输入密码"
                size="large"
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <template #label>
                <el-icon class="mr-5"><Lock /></el-icon>
                确认密码
              </template>
              <el-input 
                v-model="registerForm.confirmPassword" 
                type="password" 
                placeholder="请再次输入密码"
                size="large"
                show-password
                @keyup.enter="handleRegister"
              />
            </el-form-item>
            
            <el-form-item prop="role">
              <template #label>
                <el-icon class="mr-5"><User /></el-icon>
                身份
              </template>
              <el-select 
                v-model="registerForm.role" 
                placeholder="请选择身份"
                size="large"
                class="role-select"
              >
                <el-option label="学生" value="student" />
                <el-option label="家长" value="parent" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                size="large" 
                class="login-btn"
                :loading="loading"
                @click="handleRegister"
              >注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div class="login-footer">
        <p>© 2026 家庭学习系统</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import request from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const activeTab = ref('login')
const loading = ref(false)

const loginFormRef = ref()
const registerFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  role: [
    { required: true, message: '请选择身份', trigger: 'change' }
  ]
}

async function handleLogin() {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    ElMessage.success('登录成功')
    
    // Redirect to dashboard
    router.push('/dashboard')
    
  } catch (error) {
    console.error('Login failed:', error)
    if (error.response?.status === 401) {
      ElMessage.error('用户名或密码错误')
    } else {
      ElMessage.error('登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    const res = await request.post('/v1/auth/register', {
      username: registerForm.username,
      password: registerForm.password,
      role: registerForm.role
    })
    
    ElMessage.success('注册成功，请登录')
    
    // Switch to login tab
    activeTab.value = 'login'
    
    // Clear register form
    registerForm.username = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
    registerForm.role = ''
    
  } catch (error) {
    console.error('Register failed:', error)
    if (error.response?.status === 409) {
      ElMessage.error('用户名已存在')
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.app-title {
  text-align: center;
  color: #409eff;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.app-subtitle {
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-bottom: 30px;
}

.login-tabs {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
}

.role-select {
  width: 100%;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.login-footer p {
  color: #999;
  font-size: 12px;
  margin: 0;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-input {
  --el-input-height: 48px;
}

.mr-5 {
  margin-right: 5px;
}
</style>
