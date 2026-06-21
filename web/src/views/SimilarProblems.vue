<template>
  <div class="similar-problems-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">举一反三</h2>
        <p class="page-desc">基于错题生成相似练习题，巩固薄弱知识点</p>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左栏：错题选择 -->
      <el-col :xs="24" :md="10">
        <el-card class="section-card" shadow="never">
          <template #header>
            <div class="section-title">
              <el-icon><List /></el-icon>
              <span>选择错题生成相似题</span>
            </div>
          </template>

          <!-- 筛选 -->
          <el-row :gutter="8" class="filter-row">
            <el-col :span="12">
              <el-select v-model="filterSubject" placeholder="科目" clearable size="small" style="width:100%" @change="fetchWrongProblems">
                <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
              </el-select>
            </el-col>
            <el-col :span="12">
              <el-input v-model="filterPoint" placeholder="知识点" clearable size="small" @change="fetchWrongProblems" />
            </el-col>
          </el-row>

          <!-- 错题列表 -->
          <div v-loading="wpLoading" class="wp-list">
            <div
              v-for="wp in wrongProblems"
              :key="wp.id"
              class="wp-item"
              :class="{ active: selectedWp?.id === wp.id }"
              @click="selectWp(wp)"
            >
              <div class="wp-header">
                <el-tag :type="subjectTagType(wp.subject)" size="small" effect="dark">{{ wp.subject }}</el-tag>
                <span class="wp-point">{{ wp.knowledge_point }}</span>
              </div>
              <div class="wp-text">{{ wp.problem_text.slice(0, 80) }}{{ wp.problem_text.length > 80 ? '...' : '' }}</div>
            </div>
            <el-empty v-if="!wpLoading && wrongProblems.length === 0" description="暂无错题记录" :image-size="50" />
          </div>
        </el-card>
      </el-col>

      <!-- 右栏：相似题展示 -->
      <el-col :xs="24" :md="14">
        <el-card class="section-card" shadow="never">
          <template #header>
            <div class="section-title">
              <el-icon><Reading /></el-icon>
              <span>{{ similarProblems.length ? '相似练习' : '生成相似题' }}</span>
              <el-button v-if="selectedWp" type="primary" size="small" :loading="generating" @click="generateSimilar" style="margin-left:auto">
                <el-icon><MagicStick /></el-icon>
                {{ generating ? '生成中...' : '生成相似题' }}
              </el-button>
            </div>
          </template>

          <!-- 未选择时提示 -->
          <el-empty v-if="!selectedWp" description="请从左栏选择一道错题，然后点击「生成相似题」" :image-size="60" />

          <!-- 相似题卡片 -->
          <div v-if="similarProblems.length" class="similar-list">
            <div v-for="(sp, i) in similarProblems" :key="i" class="similar-card">
              <div class="card-header">
                <span class="card-number">#{{ i + 1 }}</span>
                <el-tag :type="difficultyTagType(sp.difficulty)" size="small">{{ difficultyLabel(sp.difficulty) }}</el-tag>
              </div>
              <div class="card-problem">{{ sp.problem }}</div>
              <el-collapse>
                <el-collapse-item title="查看答案" name="answer">
                  <div class="card-answer">{{ sp.answer }}</div>
                </el-collapse-item>
                <el-collapse-item title="查看解题过程" name="solution">
                  <div class="card-solution">{{ sp.solution }}</div>
                </el-collapse-item>
              </el-collapse>
              <div class="card-actions">
                <el-button size="small" type="success" plain @click="markPracticed(sp, i)">
                  <el-icon><Select /></el-icon>
                  标记已练习
                </el-button>
                <el-button size="small" @click="regenerate(sp, i)">
                  <el-icon><Refresh /></el-icon>
                  换一题
                </el-button>
              </div>
            </div>
          </div>

          <!-- 已生成的记录列表 -->
          <div v-if="savedProblems.length" class="history-section">
            <el-divider />
            <div class="section-title" style="margin-bottom:12px">
              <el-icon><Clock /></el-icon>
              <span>历史记录</span>
            </div>
            <div v-for="sp in savedProblems.slice(0, 5)" :key="sp.id" class="history-item">
              <div class="history-text">{{ sp.problem_text.slice(0, 60) }}...</div>
              <el-tag v-if="sp.is_practiced" type="success" size="small">已练习</el-tag>
              <el-tag v-else type="info" size="small">未练习</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { List, Reading, MagicStick, Select, Refresh, Clock } from '@element-plus/icons-vue'
import request from '@/api'

const subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']

// ─── 错题列表 ───
const wpLoading = ref(false)
const wrongProblems = ref([])
const selectedWp = ref(null)
const filterSubject = ref('')
const filterPoint = ref('')

// ─── 相似题 ───
const generating = ref(false)
const similarProblems = ref([])
const savedProblems = ref([])

async function fetchWrongProblems() {
  wpLoading.value = true
  try {
    const params = { page_size: 20 }
    if (filterSubject.value) params.subject = filterSubject.value
    if (filterPoint.value) params.knowledge_point = filterPoint.value
    const res = await request.get('/v1/wrong-problems', { params })
    wrongProblems.value = res?.data?.items ?? res?.items ?? []
  } catch {
    ElMessage.error('获取错题列表失败')
    wrongProblems.value = []
  } finally {
    wpLoading.value = false
  }
}

function selectWp(wp) {
  selectedWp.value = wp
  similarProblems.value = []
}

async function generateSimilar() {
  if (!selectedWp.value) return
  generating.value = true
  try {
    const res = await request.post('/v1/similar-problems/generate', {
      source_problem_id: selectedWp.value.id,
      subject: selectedWp.value.subject,
      knowledge_point: selectedWp.value.knowledge_point,
      problem_text: selectedWp.value.problem_text
    })
    const data = res?.data || res
    similarProblems.value.unshift({
      problem: data.problem,
      answer: data.answer,
      solution: data.solution,
      difficulty: data.difficulty,
      index: similarProblems.value.length
    })
    ElMessage.success('相似题生成成功')
    await fetchSavedProblems()
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.message || '生成失败'
    ElMessage.error(msg)
  } finally {
    generating.value = false
  }
}

async function markPracticed(sp, i) {
  // 查找已保存的记录
  const saved = savedProblems.value[i]
  if (saved?.id) {
    try {
      await request.put(`/v1/similar-problems/${saved.id}/practice`)
      ElMessage.success('已标记为练习')
      await fetchSavedProblems()
    } catch {
      ElMessage.error('操作失败')
    }
  } else {
    ElMessage.info('已练习')
  }
}

function regenerate(sp, i) {
  similarProblems.value.splice(i, 1)
  generateSimilar()
}

async function fetchSavedProblems() {
  try {
    const res = await request.get('/v1/similar-problems', { params: { page_size: 10 } })
    savedProblems.value = res?.data?.items ?? res?.items ?? []
  } catch {
    savedProblems.value = []
  }
}

// ─── 工具函数 ───
const subjectTagColors = {
  '数学': 'primary', '物理': 'cyan', '化学': 'warning',
  '语文': 'success', '英语': '', '生物': 'purple',
  '历史': 'danger', '地理': 'info', '政治': 'danger'
}
function subjectTagType(s) { return subjectTagColors[s] || 'info' }
function difficultyTagType(d) { return { 1: 'success', 2: 'warning', 3: 'danger' }[d] || 'info' }
function difficultyLabel(d) { return { 1: '简单', 2: '中等', 3: '困难' }[d] || '未知' }

// ─── 初始化 ───
onMounted(() => {
  fetchWrongProblems()
  fetchSavedProblems()
})
</script>

<style scoped>
.similar-problems-page {
  padding: 0;
}

.page-header { margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 600; color: var(--el-text-color-primary); margin: 0 0 4px 0; }
.page-desc { font-size: 14px; color: var(--el-text-color-secondary); margin: 0; }

.section-card { margin-bottom: 20px; border-radius: 10px; border: 1px solid var(--el-border-color-light); }
.section-card :deep(.el-card__header) { padding: 14px 20px; border-bottom: 1px solid var(--el-border-color-light); background: var(--el-fill-color-light); }
.section-title { display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 600; color: var(--el-text-color-primary); }
.section-title .el-icon { font-size: 16px; color: var(--el-color-primary); }

/* ── 筛选 ── */
.filter-row { margin-bottom: 12px; }

/* ── 错题列表 ── */
.wp-list { max-height: 500px; overflow-y: auto; }
.wp-item { padding: 12px; margin-bottom: 8px; border: 1px solid var(--el-border-color-light); border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.wp-item:hover { border-color: var(--el-color-primary-light-5); background: var(--el-color-primary-light-9); }
.wp-item.active { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.wp-header { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
.wp-point { font-size: 13px; font-weight: 500; color: var(--el-text-color-secondary); }
.wp-text { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.5; }

/* ── 相似题 ── */
.similar-list { max-height: 550px; overflow-y: auto; }
.similar-card { padding: 16px; margin-bottom: 14px; background: var(--el-fill-color-lighter); border-radius: 10px; border: 1px solid var(--el-border-color-lighter); }
.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.card-number { font-size: 14px; font-weight: 700; color: var(--el-color-primary); }
.card-problem { font-size: 15px; line-height: 1.7; color: var(--el-text-color-primary); white-space: pre-wrap; margin-bottom: 10px; }
.card-answer { font-size: 14px; line-height: 1.6; color: var(--el-text-color-regular); white-space: pre-wrap; padding: 8px; background: var(--el-bg-color); border-radius: 6px; }
.card-solution { font-size: 14px; line-height: 1.7; color: var(--el-text-color-regular); white-space: pre-wrap; padding: 8px; background: var(--el-bg-color); border-radius: 6px; }
.card-actions { display: flex; gap: 8px; margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--el-border-color-lighter); }

/* ── 历史 ── */
.history-item { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--el-border-color-lighter); }
.history-item:last-child { border-bottom: none; }
.history-text { font-size: 13px; color: var(--el-text-color-regular); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── 响应式 ── */
@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 12px; }
}
</style>
