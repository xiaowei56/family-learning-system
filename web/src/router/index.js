import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/study-records',
    name: 'StudyRecords',
    component: () => import('@/views/StudyRecords.vue'),
    meta: { title: '学习记录' },
  },
  {
    path: '/exam-scores',
    name: 'ExamScores',
    component: () => import('@/views/ExamScores.vue'),
    meta: { title: '考试成绩' },
  },
  {
    path: '/wrong-problems',
    name: 'WrongProblems',
    component: () => import('@/views/WrongProblems.vue'),
    meta: { title: '错题本' },
  },
  {
    path: '/paper-library',
    name: 'PaperLibrary',
    component: () => import('@/views/PaperLibrary.vue'),
    meta: { title: '试卷库' },
  },
  {
    path: '/similar-problems',
    name: 'SimilarProblems',
    component: () => import('@/views/SimilarProblems.vue'),
    meta: { title: '举一反三' },
  },
  {
    path: '/weak-points',
    name: 'WeakPoints',
    component: () => import('@/views/WeakPoints.vue'),
    meta: { title: '薄弱点分析' },
  },
  {
    path: '/review-center',
    name: 'ReviewCenter',
    component: () => import('@/views/ReviewCenter.vue'),
    meta: { title: '复习中心' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '设置' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
