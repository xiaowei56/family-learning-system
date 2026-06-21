<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2 class="page-title">首页</h2>
      <p class="page-desc">欢迎回来，今日学习概览</p>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton :rows="6" animated />
    </div>

    <template v-else>
      <!-- ===== 统计卡片 ===== -->
      <el-row :gutter="20" class="stat-row">
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-review">
            <div class="stat-icon"><el-icon :size="28"><Notebook /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ dashboard.today_reviews?.total ?? 0 }}</div>
              <div class="stat-label">今日待复习</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-subject">
            <div class="stat-icon"><el-icon :size="28"><Collection /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ subjectCount }}</div>
              <div class="stat-label">涉及科目</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-score">
            <div class="stat-icon"><el-icon :size="28"><TrendCharts /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ avgScoreRate }}</div>
              <div class="stat-label">平均得分率</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card stat-card-record">
            <div class="stat-icon"><el-icon :size="28"><Document /></el-icon></div>
            <div class="stat-body">
              <div class="stat-value">{{ recentWrongCount }}</div>
              <div class="stat-label">近期错题</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- ===== 主体内容：两栏布局 ===== -->
      <el-row :gutter="20" class="main-row">
        <!-- 左栏：今日复习 -->
        <el-col :xs="24" :md="14">
          <el-card class="section-card" shadow="never">
            <template #header>
              <div class="section-title">
                <el-icon><AlarmClock /></el-icon>
                <span>今日复习</span>
                <el-tag v-if="(dashboard.today_reviews?.total ?? 0) > 0" type="warning" size="small" effect="dark" class="section-badge">
                  {{ dashboard.today_reviews?.total }} 项
                </el-tag>
              </div>
            </template>

            <!-- 有复习项 -->
            <div v-if="(dashboard.today_reviews?.subjects ?? []).length > 0" class="review-list">
              <div
                v-for="subject in (dashboard.today_reviews?.subjects ?? [])"
                :key="subject"
                class="review-subject-item"
              >
                <el-tag :type="subjectTagType(subject)" size="default" effect="dark">
                  {{ subject }}
                </el-tag>
                <span class="review-hint">有待复习内容</span>
              </div>
              <div class="review-footer">
                <el-button size="small" @click="$router.push('/review-center')">
                  前往复习中心
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 无复习项 -->
            <el-empty v-else description="今日无待复习内容 🎉">
              <el-button size="small" type="primary" @click="$router.push('/study-records')">
                去记录学习
              </el-button>
            </el-empty>
          </el-card>

          <!-- 近期错题（占位） -->
          <el-card class="section-card" shadow="never">
            <template #header>
              <div class="section-title">
                <el-icon><WarningFilled /></el-icon>
                <span>近期错题</span>
                <el-tag v-if="recentWrongCount > 0" type="danger" size="small" effect="dark" class="section-badge">
                  {{ recentWrongCount }} 道
                </el-tag>
              </div>
            </template>
            <el-empty v-if="recentWrongCount === 0" description="暂无错题记录，继续加油！" :image-size="60" />
          </el-card>
        </el-col>

        <!-- 右栏：得分率摘要 -->
        <el-col :xs="24" :md="10">
          <el-card class="section-card" shadow="never">
            <template #header>
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>各科目最新得分率</span>
              </div>
            </template>

            <div v-if="latestScores.length > 0" class="score-list">
              <div
                v-for="item in latestScores"
                :key="item.subject"
                class="score-item"
              >
                <div class="score-label">
                  <el-tag :type="subjectTagType(item.subject)" size="small" effect="plain">
                    {{ item.subject }}
                  </el-tag>
                </div>
                <div class="score-bar-wrapper">
                  <el-progress
                    :percentage="formatRate(item.score_rate)"
                    :color="scoreRateColor(item.score_rate)"
                    :stroke-width="14"
                    :text-inside="true"
                    :format="() => formatRateDisplay(item.score_rate)"
                  />
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无成绩记录" :image-size="60" />

            <div v-if="latestScores.length > 0" class="score-footer">
              <el-button size="small" @click="$router.push('/exam-scores')">
                查看详细趋势
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </el-card>

          <!-- 快捷入口 -->
          <el-card class="section-card" shadow="never">
            <template #header>
              <div class="section-title">
                <el-icon><Link /></el-icon>
                <span>快捷入口</span>
              </div>
            </template>
            <div class="quick-links">
              <el-button class="quick-link-btn" @click="$router.push('/study-records')">
                <el-icon><EditPen /></el-icon>
                记录学习
              </el-button>
              <el-button class="quick-link-btn" @click="$router.push('/exam-scores')">
                <el-icon><TrendCharts /></el-icon>
                录入成绩
              </el-button>
              <el-button class="quick-link-btn" @click="$router.push('/review-center')">
                <el-icon><AlarmClock /></el-icon>
                开始复习
              </el-button>
              <el-button class="quick-link-btn" @click="$router.push('/settings')">
                <el-icon><Setting /></el-icon>
                设置
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Notebook, Collection, TrendCharts, Document,
  AlarmClock, ArrowRight, WarningFilled,
  DataAnalysis, EditPen, Link, Setting
} from '@element-plus/icons-vue'
import request from '@/api'

// ─── 状态 ───
const loading = ref(false)
const dashboard = ref({})

// ─── API ───
async function fetchDashboard() {
  loading.value = true
  try {
    const res = await request.get('/v1/dashboard')
    dashboard.value = res?.data || res || {}
  } catch (err) {
    console.error('获取仪表盘数据失败:', err)
    ElMessage.error('获取仪表盘数据失败')
    dashboard.value = {}
  } finally {
    loading.value = false
  }
}

// ─── 计算属性 ───
const subjectCount = computed(() => {
  return (dashboard.value.today_reviews?.subjects ?? []).length
})

const latestScores = computed(() => {
  return dashboard.value.score_summary?.latest ?? []
})

const recentWrongCount = computed(() => {
  return dashboard.value.recent_wrong?.total ?? 0
})

const avgScoreRate = computed(() => {
  const scores = latestScores.value
  if (scores.length === 0) return '--'
  const total = scores.reduce((sum, s) => {
    const rate = s.score_rate <= 1 ? s.score_rate * 100 : s.score_rate
    return sum + rate
  }, 0)
  return `${(total / scores.length).toFixed(1)}%`
})

// ─── 工具函数 ───
const subjectTagColors = {
  '数学': 'primary',
  '物理': 'cyan',
  '化学': 'warning',
  '语文': 'success',
  '英语': '',
  '生物': 'purple',
  '历史': 'danger',
  '地理': 'info',
  '政治': 'danger',
}

function subjectTagType(subject) {
  return subjectTagColors[subject] || 'info'
}

function formatRate(scoreRate) {
  if (scoreRate == null) return 0
  return scoreRate <= 1 ? Math.round(scoreRate * 100) : Math.round(scoreRate)
}

function formatRateDisplay(scoreRate) {
  return scoreRate == null ? '--' : `${formatRate(scoreRate)}%`
}

function scoreRateColor(scoreRate) {
  if (scoreRate == null) return '#909399'
  const pct = scoreRate <= 1 ? scoreRate * 100 : scoreRate
  if (pct >= 80) return '#67c23a'
  if (pct >= 60) return '#e6a23c'
  return '#f56c6c'
}

// ─── 初始化 ───
onMounted(() => {
  fetchDashboard()
})
</script>

<style scoped>
.dashboard-page {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

/* ── 页头 ── */
.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 4px 0;
}

.page-desc {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

/* ── 统计卡片 ── */
.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 10px;
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-light);
  transition: box-shadow 0.2s, transform 0.15s;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.stat-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #fff;
}

.stat-card-review .stat-icon {
  background: linear-gradient(135deg, #409eff, #337ecc);
}

.stat-card-subject .stat-icon {
  background: linear-gradient(135deg, #67c23a, #529b2e);
}

.stat-card-score .stat-icon {
  background: linear-gradient(135deg, #e6a23c, #cf9236);
}

.stat-card-record .stat-icon {
  background: linear-gradient(135deg, #909399, #73767a);
}

.stat-body {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--el-text-color-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}

/* ── 主体内容 ── */
.main-row {
  margin-bottom: 24px;
}

/* ── 卡片通用 ── */
.section-card {
  margin-bottom: 20px;
  border-radius: 10px;
  border: 1px solid var(--el-border-color-light);
}

.section-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-fill-color-light);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.section-title .el-icon {
  font-size: 16px;
  color: var(--el-color-primary);
}

.section-badge {
  margin-left: 4px;
}

/* ── 复习列表 ── */
.review-list {
  padding: 4px 0;
}

.review-subject-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 4px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.review-subject-item:last-child {
  border-bottom: none;
}

.review-hint {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.review-footer {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
  text-align: right;
}

/* ── 得分率列表 ── */
.score-list {
  padding: 4px 0;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 4px;
}

.score-label {
  flex-shrink: 0;
  width: 56px;
}

.score-bar-wrapper {
  flex: 1;
  min-width: 0;
}

.score-footer {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
  text-align: right;
}

/* ── 快捷入口 ── */
.quick-links {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.quick-link-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 14px 10px;
  border-radius: 8px;
  transition: background 0.2s;
}

/* ── 加载中 / 空状态 ── */
.loading-wrapper {
  padding: 40px 20px;
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .stat-value {
    font-size: 22px;
  }
  .stat-card {
    padding: 14px 16px;
  }
  .quick-links {
    grid-template-columns: 1fr;
  }
}
</style>
