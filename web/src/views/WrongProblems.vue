<template>
  <div class="wrong-problems-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">错题本</h2>
        <p class="page-desc">整理和复习做错的题目，支持拍照收录与 AI 分析</p>
      </div>
      <el-button type="primary" @click="showAutoCollect = true">
        <el-icon><Camera /></el-icon>
        拍照收录
      </el-button>
    </div>

    <!-- ===== 拍照收录弹窗 ===== -->
    <el-dialog v-model="showAutoCollect" title="拍照收录错题" width="600px" destroy-on-close>
      <div class="auto-collect-body">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          accept="image/jpeg,image/png"
          list-type="picture-card"
          :limit="1"
          :on-change="handleFileChange"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>

        <el-form v-if="uploadFile" label-width="80px" class="collect-form">
          <el-form-item label="科目">
            <el-select v-model="collectForm.subject" placeholder="选择科目">
              <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item label="知识点">
            <el-input v-model="collectForm.knowledge_point" placeholder="如：一元二次方程" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="collectLoading" @click="handleAutoCollect">
              <el-icon><MagicStick /></el-icon>
              开始智能收录
            </el-button>
            <el-tag v-if="collectResult" :type="collectResult.is_correct ? 'success' : 'danger'" class="collect-result-tag">
              {{ collectResult.is_correct ? '回答正确' : '收录为错题' }}
            </el-tag>
          </el-form-item>
        </el-form>

        <div v-if="collectResult" class="collect-result">
          <el-divider />
          <h4>OCR 识别结果</h4>
          <p class="ocr-text">{{ collectResult.ocr_text }}</p>
          <h4>AI 评估</h4>
          <p class="eval-text">{{ collectResult.evaluation }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showAutoCollect = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ===== 筛选栏 ===== -->
    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :xs="12" :sm="6">
          <el-select v-model="filterSubject" placeholder="全部科目" clearable style="width:100%" @change="fetchProblems">
            <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="6">
          <el-input v-model="filterPoint" placeholder="知识点搜索" clearable @change="fetchProblems" />
        </el-col>
        <el-col :xs="12" :sm="4">
          <el-select v-model="filterDifficulty" placeholder="全部难度" clearable style="width:100%" @change="fetchProblems">
            <el-option label="简单" :value="1" />
            <el-option label="中等" :value="2" />
            <el-option label="困难" :value="3" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="4">
          <el-select v-model="filterCorrect" placeholder="全部状态" clearable style="width:100%" @change="fetchProblems">
            <el-option label="仅错题" :value="0" />
            <el-option label="已正确" :value="1" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="4" class="filter-actions">
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- ===== 错题列表 ===== -->
    <div v-loading="loading" class="problem-list">
      <div v-if="!loading && problems.length === 0" class="empty-wrapper">
        <el-empty description="暂无错题记录，上传试卷照片开始收录" :image-size="80" />
      </div>

      <div v-for="item in problems" :key="item.id" class="problem-card">
        <div class="problem-header">
          <div class="problem-tags">
            <el-tag :type="subjectTagType(item.subject)" size="small" effect="dark">
              {{ item.subject }}
            </el-tag>
            <el-tag :type="difficultyTagType(item.difficulty)" size="small" effect="plain">
              {{ difficultyLabel(item.difficulty) }}
            </el-tag>
            <el-tag v-if="item.is_correct === 1" type="success" size="small">已掌握</el-tag>
            <el-tag v-else-if="item.is_correct === 0" type="danger" size="small">待订正</el-tag>
            <el-tag v-else type="info" size="small">待评估</el-tag>
          </div>
          <span class="problem-date">{{ formatDate(item.created_at) }}</span>
        </div>

        <div class="problem-body">
          <div class="problem-text">{{ item.problem_text }}</div>

          <!-- 展开详情 -->
          <div v-if="expandedId === item.id" class="problem-detail">
            <div v-if="item.student_answer" class="detail-row">
              <strong>学生作答：</strong><span :class="item.is_correct === 1 ? 'text-correct' : 'text-wrong'">{{ item.student_answer }}</span>
            </div>
            <div v-if="item.correct_answer" class="detail-row">
              <strong>正确答案：</strong><span class="text-correct">{{ item.correct_answer }}</span>
            </div>
            <div v-if="item.ai_evaluation" class="detail-row">
              <strong>AI 评估：</strong>
              <p class="evaluation-content">{{ item.ai_evaluation }}</p>
            </div>
            <div v-if="item.solution" class="detail-row">
              <strong>解题过程：</strong>
              <div class="solution-content" v-html="renderSolution(item.solution)"></div>
            </div>
            <div class="detail-actions">
              <el-button size="small" :loading="solutionLoadingId === item.id" @click="fetchSolution(item)">
                <el-icon><Reading /></el-icon>
                查看解题
              </el-button>
              <el-popconfirm title="确定删除该错题？" confirm-button-text="删除" confirm-button-type="danger" @confirm="deleteProblem(item.id)">
                <template #reference>
                  <el-button type="danger" size="small" link>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </div>

        <div class="problem-footer">
          <el-button text size="small" @click="toggleExpand(item.id)">
            {{ expandedId === item.id ? '收起' : '查看详情' }}
            <el-icon><ArrowDown v-if="expandedId !== item.id" /><ArrowUp v-else /></el-icon>
          </el-button>
          <span class="wrong-count">错题次数：{{ item.wrong_count }}</span>
        </div>
      </div>
    </div>

    <!-- ===== 分页 ===== -->
    <div v-if="total > pageSize" class="pagination-wrapper">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchProblems"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus, Camera, MagicStick, Reading, Delete, ArrowDown, ArrowUp
} from '@element-plus/icons-vue'
import request from '@/api'
import { useStudentStore } from '@/stores/student'

const studentStore = useStudentStore()

// ─── 常量 ───
const subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']

// ─── 状态 ───
const loading = ref(false)
const problems = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const expandedId = ref(null)
const solutionLoadingId = ref(null)

// ─── 筛选 ───
const filterSubject = ref('')
const filterPoint = ref('')
const filterDifficulty = ref(null)
const filterCorrect = ref(null)

// ─── 拍照收录 ───
const showAutoCollect = ref(false)
const uploadFile = ref(null)
const collectLoading = ref(false)
const collectResult = ref(null)
const collectForm = reactive({
  subject: '',
  knowledge_point: ''
})

// ─── API ───
async function fetchProblems() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterSubject.value) params.subject = filterSubject.value
    if (filterPoint.value) params.knowledge_point = filterPoint.value
    if (filterDifficulty.value != null) params.difficulty = filterDifficulty.value
    if (filterCorrect.value != null) params.is_correct = filterCorrect.value
    params.student_id = studentStore.currentStudentId || undefined
    const res = await request.get('/v1/wrong-problems', { params })
    problems.value = res?.data?.items ?? res?.items ?? []
    total.value = res?.data?.total ?? res?.total ?? 0
  } catch (err) {
    console.error('获取错题失败:', err)
    ElMessage.error('加载错题列表失败')
    problems.value = []
  } finally {
    loading.value = false
  }
}

async function deleteProblem(id) {
  try {
    await request.delete(`/v1/wrong-problems/${id}`)
    ElMessage.success('删除成功')
    await fetchProblems()
  } catch (err) {
    ElMessage.error('删除失败，请重试')
  }
}

async function fetchSolution(item) {
  solutionLoadingId.value = item.id
  try {
    const res = await request.post('/v1/wrong-problems/solution', {
      problem_text: item.problem_text,
      subject: item.subject,
      knowledge_point: item.knowledge_point
    })
    const data = res?.data || res
    item.solution = data.solution || '暂无解题过程'
    expandedId.value = item.id
  } catch (err) {
    ElMessage.error('获取解题过程失败')
  } finally {
    solutionLoadingId.value = null
  }
}

// ─── 拍照收录 ───
function handleFileChange(file) {
  uploadFile.value = file
  collectResult.value = null
}

async function handleAutoCollect() {
  if (!uploadFile.value) {
    ElMessage.warning('请先上传图片')
    return
  }
  if (!collectForm.subject || !collectForm.knowledge_point) {
    ElMessage.warning('请填写科目和知识点')
    return
  }

  collectLoading.value = true
  collectResult.value = null
  try {
    // 1. 上传图片
    const formData = new FormData()
    formData.append('file', uploadFile.value.raw)
    const uploadRes = await request.post('/v1/wrong-problems/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const imagePath = uploadRes?.data?.image_path ?? uploadRes?.image_path

    // 2. 自动收录
    const collectRes = await request.post('/v1/wrong-problems/auto-collect', {
      image_path: imagePath,
      subject: collectForm.subject,
      knowledge_point: collectForm.knowledge_point,
      student_id: studentStore.currentStudentId || undefined
    })
    collectResult.value = collectRes?.data || collectRes
    ElMessage.success('错题收录成功！')
    await fetchProblems()
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.message || '收录失败'
    ElMessage.error(msg)
  } finally {
    collectLoading.value = false
  }
}

// ─── 工具函数 ───
function resetFilters() {
  filterSubject.value = ''
  filterPoint.value = ''
  filterDifficulty.value = null
  filterCorrect.value = null
  page.value = 1
  fetchProblems()
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

const subjectTagColors = {
  '数学': 'primary', '物理': 'cyan', '化学': 'warning',
  '语文': 'success', '英语': '', '生物': 'purple',
  '历史': 'danger', '地理': 'info', '政治': 'danger',
}

function subjectTagType(subject) {
  return subjectTagColors[subject] || 'info'
}

function difficultyTagType(diff) {
  return { 1: 'success', 2: 'warning', 3: 'danger' }[diff] || 'info'
}

function difficultyLabel(diff) {
  return { 1: '简单', 2: '中等', 3: '困难' }[diff] || '未知'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.slice(0, 10)
}

function renderSolution(text) {
  if (!text) return ''
  // 替换 LaTeX 公式标记（简化处理）
  return text
    .replace(/\$\$(.+?)\$\$/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

// ─── 初始化 ───
onMounted(() => {
  fetchProblems()
})
</script>

<style scoped>
.wrong-problems-page {
  padding: 0;
}

/* ── 页头 ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
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

/* ── 筛选栏 ── */
.filter-card {
  margin-bottom: 16px;
  border-radius: 10px;
}

.filter-card :deep(.el-card__body) {
  padding: 14px 20px;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}

/* ── 错题列表 ── */
.problem-list {
  min-height: 200px;
}

.problem-card {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  margin-bottom: 12px;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.problem-card:hover {
  border-color: var(--el-border-color-darker);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.problem-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px 0;
}

.problem-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.problem-date {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  flex-shrink: 0;
}

.problem-body {
  padding: 10px 18px;
}

.problem-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
}

.problem-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.detail-row {
  margin-bottom: 10px;
  font-size: 14px;
  line-height: 1.6;
}

.detail-row strong {
  color: var(--el-text-color-secondary);
  font-weight: 600;
}

.text-correct {
  color: var(--el-color-success);
}

.text-wrong {
  color: var(--el-color-danger);
}

.evaluation-content {
  margin: 4px 0 0 0;
  color: var(--el-text-color-regular);
  white-space: pre-wrap;
  background: var(--el-fill-color-lighter);
  padding: 10px;
  border-radius: 6px;
}

.solution-content {
  margin: 4px 0 0 0;
  color: var(--el-text-color-regular);
  white-space: pre-wrap;
  background: var(--el-fill-color-lighter);
  padding: 10px;
  border-radius: 6px;
  line-height: 1.8;
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.problem-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 18px 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.wrong-count {
  font-size: 12px;
  color: var(--el-color-warning);
  background: var(--el-color-warning-light-9);
  padding: 1px 8px;
  border-radius: 4px;
}

/* ── 拍照收录弹窗 ── */
.auto-collect-body {
  min-height: 200px;
}

.collect-form {
  margin-top: 16px;
}

.collect-result-tag {
  margin-left: 8px;
}

.collect-result {
  margin-top: 8px;
}

.collect-result h4 {
  margin: 0 0 6px 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.ocr-text, .eval-text {
  font-size: 13px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  white-space: pre-wrap;
  background: var(--el-fill-color-lighter);
  padding: 10px;
  border-radius: 6px;
  margin: 0 0 12px 0;
}

/* ── 空状态 ── */
.empty-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 60px;
}

/* ── 分页 ── */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin: 24px 0 40px;
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
  }
  .problem-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}
</style>
