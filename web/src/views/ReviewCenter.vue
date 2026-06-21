<template>
  <div class="review-center-page">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">复习中心</h2>
        <p class="page-desc">
          今日待复习
          <span v-if="total > 0" class="total-badge">{{ total }} 项</span>
        </p>
      </div>
      <el-button :loading="loading" @click="fetchReviews">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 空状态 -->
    <div v-else-if="subjects.length === 0" class="empty-wrapper">
      <el-result icon="success" title="今日复习已完成！" sub-title="今日暂无待复习内容，继续保持！">
        <template #icon>
          <el-icon class="celebration-icon" :size="80"><CircleCheckFilled /></el-icon>
        </template>
      </el-result>
    </div>

    <!-- 按科目分组 -->
    <template v-else>
      <div
        v-for="group in subjects"
        :key="group.subject"
        class="subject-group"
      >
        <!-- 科目标题 -->
        <div class="subject-header">
          <el-tag :type="subjectTagType(group.subject)" size="large" effect="dark" class="subject-tag">
            {{ group.subject }}
          </el-tag>
          <span class="subject-count">{{ group.count }} 项待复习</span>
        </div>

        <!-- 该科目下的复习项 -->
        <div class="review-list">
          <div
            v-for="item in group.records"
            :key="item.id"
            class="review-card"
          >
            <div class="review-card-body">
              <div class="review-info">
                <div class="review-title">{{ item.title }}</div>
                <div class="review-meta">
                  <span class="review-count">
                    第 {{ item.review_count }} 次复习
                  </span>
                  <span class="review-subject">
                    <el-tag :type="subjectTagType(group.subject)" size="small" effect="plain">
                      {{ group.subject }}
                    </el-tag>
                  </span>
                </div>
              </div>

              <div class="review-actions">
                <!-- 速度模式 -->
                <div class="speed-selector">
                  <span class="speed-label">速度：</span>
                  <el-radio-group
                    :model-value="item.speed_mode || 'medium'"
                    size="small"
                    @change="(val) => handleSpeedChange(item, val)"
                  >
                    <el-radio-button value="fast">快速</el-radio-button>
                    <el-radio-button value="medium">中等</el-radio-button>
                    <el-radio-button value="slow">慢速</el-radio-button>
                  </el-radio-group>
                </div>

                <!-- 标记已掌握 -->
                <el-button
                  type="success"
                  plain
                  size="small"
                  :loading="masteringId === item.id"
                  @click="handleMaster(item)"
                >
                  <el-icon><Select /></el-icon>
                  标记为已掌握
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Select, CircleCheckFilled } from '@element-plus/icons-vue'
import request from '@/api'

// ─── 状态 ───
const loading = ref(false)
const reviewData = ref(null)
const masteringId = ref(null)

// ─── 计算属性 ───
const subjects = computed(() => reviewData.value?.subjects || [])
const total = computed(() => reviewData.value?.total || 0)

// ─── 科目标签样式 ───
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

// ─── API ───
async function fetchReviews() {
  loading.value = true
  try {
    const res = await request.get('/v1/reviews/today')
    reviewData.value = res?.data || res
  } catch (err) {
    console.error('获取今日复习失败:', err)
    ElMessage.error('获取今日复习失败')
    reviewData.value = { subjects: [], total: 0 }
  } finally {
    loading.value = false
  }
}

async function handleMaster(item) {
  try {
    await ElMessageBox.confirm(
      `确定将「${item.title}」标记为已掌握吗？标记后将不再安排该知识点的复习。`,
      '确认掌握',
      { confirmButtonText: '确定掌握', cancelButtonText: '取消', type: 'success' }
    )
  } catch {
    return
  }

  masteringId.value = item.id
  try {
    await request.put(`/v1/reviews/${item.id}/master`)
    ElMessage.success('已标记为掌握')
    await fetchReviews()
  } catch (err) {
    console.error('标记掌握失败:', err)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    masteringId.value = null
  }
}

async function handleSpeedChange(item, speedMode) {
  const oldSpeed = item.speed_mode
  item.speed_mode = speedMode
  try {
    await request.put(`/v1/reviews/${item.id}/speed`, { speed_mode: speedMode })
    ElMessage.success('复习速度已更新')
  } catch (err) {
    console.error('修改速度失败:', err)
    item.speed_mode = oldSpeed
    ElMessage.error('修改失败，请稍后重试')
  }
}

// ─── 初始化 ───
fetchReviews()
</script>

<style scoped>
.review-center-page {
  padding: 0;
}

/* ── 页头 ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 4px 0;
}

.page-desc {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.total-badge {
  display: inline-block;
  background: var(--el-color-primary-light-1);
  color: #fff;
  font-size: 12px;
  padding: 1px 10px;
  border-radius: 10px;
  font-weight: 500;
}

/* ── 科目分组 ── */
.subject-group {
  margin-bottom: 28px;
}

.subject-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--el-border-color-light);
}

.subject-tag {
  font-weight: 600;
  font-size: 15px;
}

.subject-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* ── 复习卡片列表 ── */
.review-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.review-card {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.review-card:hover {
  border-color: var(--el-border-color-darker);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.review-card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  gap: 16px;
}

.review-info {
  flex: 1;
  min-width: 0;
}

.review-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.review-count {
  font-size: 12px;
  color: var(--el-color-warning);
  background: var(--el-color-warning-light-9);
  padding: 1px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.review-subject {
  display: inline-flex;
}

/* ── 操作区 ── */
.review-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.speed-selector {
  display: flex;
  align-items: center;
  gap: 4px;
}

.speed-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

/* ── 空状态 ── */
.empty-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 80px;
}

.celebration-icon {
  color: var(--el-color-success);
}

/* ── 加载中 ── */
.loading-wrapper {
  padding: 40px 20px;
}
</style>
