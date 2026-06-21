import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import request from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const displayName = computed(() => user.value?.name || '未登录')

  async function login(credentials) {
    const res = await request.post('/v1/auth/login', credentials)
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    sessionStorage.removeItem('token')
  }

  async function fetchProfile() {
    const res = await request.get('/v1/auth/profile')
    user.value = res
    return res
  }

  return { token, user, isLoggedIn, displayName, login, logout, fetchProfile }
})
