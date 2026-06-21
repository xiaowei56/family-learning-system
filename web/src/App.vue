<template>
  <el-container class="app-container">
    <!-- Login page - no sidebar -->
    <router-view v-if="route.path === '/login'" />
    
    <!-- Main layout with sidebar for all other routes -->
    <template v-else>
      <!-- Sidebar -->
      <el-aside :width="sidebarWidth" class="app-sidebar">
        <div class="sidebar-logo">
          <el-icon :size="24" color="#409eff"><School /></el-icon>
          <span class="logo-text">家庭学习系统</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          :router="true"
          background-color="var(--sidebar-bg)"
          text-color="var(--sidebar-text)"
          active-text-color="var(--sidebar-active-text)"
          class="sidebar-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/study-records">
            <el-icon><Notebook /></el-icon>
            <span>学习记录</span>
          </el-menu-item>
          <el-menu-item index="/exam-scores">
            <el-icon><TrendCharts /></el-icon>
            <span>考试成绩</span>
          </el-menu-item>
          <el-menu-item index="/wrong-problems">
            <el-icon><CloseBold /></el-icon>
            <span>错题本</span>
          </el-menu-item>
          <el-menu-item index="/paper-library">
            <el-icon><FolderOpened /></el-icon>
            <span>试卷库</span>
          </el-menu-item>
          <el-menu-item index="/similar-problems">
            <el-icon><CopyDocument /></el-icon>
            <span>举一反三</span>
          </el-menu-item>
          <el-menu-item index="/weak-points">
            <el-icon><WarningFilled /></el-icon>
            <span>薄弱点分析</span>
          </el-menu-item>
          <el-menu-item index="/review-center">
            <el-icon><Refresh /></el-icon>
            <span>复习中心</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- Right area: header + main -->
      <el-container class="app-main-area">
        <!-- Header -->
        <el-header class="app-header">
          <div class="header-left">
            <span class="header-page-title">{{ currentPageTitle }}</span>
          </div>
          <div class="header-right">
            <!-- 学生切换器 -->
            <div v-if="studentStore.hasStudents" class="header-student-switcher">
              <el-select
                v-model="studentStore.currentStudentId"
                @change="studentStore.selectStudent"
                size="small"
                style="width: 140px"
              >
                <el-option
                  v-for="s in studentStore.students"
                  :key="s.id"
                  :label="`${s.name}（${s.grade_level}）`"
                  :value="s.id"
                />
              </el-select>
            </div>
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="header-user">
                <el-avatar :size="32" icon="UserFilled" />
                <span class="user-name">{{ authStore.displayName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- Main content -->
        <el-main class="app-main-content">
          <router-view />
        </el-main>
      </el-container>
    </template>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useStudentStore } from '@/stores/student'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const studentStore = useStudentStore()

const sidebarWidth = ref('var(--sidebar-width)')

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => route.meta?.title || '家庭学习系统')

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  if (authStore.isLoggedIn) {
    studentStore.fetchStudents()
  }
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  overflow: hidden;
}

/* ---------- Sidebar ---------- */
.app-sidebar {
  background-color: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.3s;
}

.sidebar-logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.sidebar-menu .el-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ---------- Right area ---------- */
.app-main-area {
  display: flex;
  flex-direction: column;
  background: var(--main-bg);
}

/* ---------- Header ---------- */
.app-header {
  height: var(--header-height);
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-page-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--main-text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-student-switcher {
  display: flex;
  align-items: center;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.user-name {
  font-size: 14px;
  color: var(--main-text);
}

/* ---------- Main content ---------- */
.app-main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--main-bg);
}
</style>
