<template>
  <div class="paper-library-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">试卷库</h2>
        <p class="page-desc">管理各科目试卷资源，支持 OCR 识别与笔迹擦除</p>
      </div>
      <el-button type="primary" @click="showUpload = true">
        <el-icon><Upload /></el-icon>
        上传试卷
      </el-button>
    </div>

    <!-- ===== 上传弹窗 ===== -->
    <el-dialog v-model="showUpload" title="上传试卷" width="500px" destroy-on-close>
      <el-form :model="uploadForm" label-width="70px">
        <el-form-item label="科目" required>
          <el-select v-model="uploadForm.subject" placeholder="选择科目" style="width:100%">
            <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="uploadForm.title" placeholder="如：2026 期中数学试卷" />
        </el-form-item>
        <el-form-item label="考试类型">
          <el-select v-model="uploadForm.exam_type" placeholder="选填" clearable style="width:100%">
            <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试日期">
          <el-date-picker v-model="uploadForm.exam_date" type="date" placeholder="选填" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="图片" required>
          <el-upload ref="uploadRef" :auto-upload="false" accept="image/jpeg,image/png" :limit="1" :on-change="handlePaperFile" drag>
            <el-icon class="upload-icon"><Plus /></el-icon>
            <div class="upload-text">点击或拖拽上传试卷图片</div>
            <template #tip><div class="upload-hint">支持 JPG/PNG，最大 50MB</div></template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          {{ uploading ? '上传中...' : '确认上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- ===== 筛选栏 ===== -->
    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :xs="12" :sm="6">
          <el-select v-model="filterSubject" placeholder="全部科目" clearable style="width:100%" @change="fetchPapers">
            <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="6">
          <el-select v-model="filterExamType" placeholder="全部类型" clearable style="width:100%" @change="fetchPapers">
            <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="4">
          <el-select v-model="filterStatus" placeholder="全部状态" clearable style="width:100%" @change="fetchPapers">
            <el-option label="已上传" value="uploaded" />
            <el-option label="已识别" value="ocr_done" />
            <el-option label="已擦除" value="cleaned" />
            <el-option label="已标注" value="annotated" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- ===== 试卷网格 ===== -->
    <div v-loading="loading" class="paper-grid">
      <div v-if="!loading && papers.length === 0" class="empty-wrapper">
        <el-empty description="暂无试卷，点击右上角上传" :image-size="80" />
      </div>

      <div v-for="paper in papers" :key="paper.id" class="paper-card">
        <div class="paper-image-wrapper">
          <el-image
            :src="paperImageUrl(paper.original_image_path)"
            fit="cover"
            class="paper-thumb"
          >
            <template #error>
              <div class="image-placeholder">
                <el-icon :size="36"><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <div class="paper-status-badge" :class="'status-' + paper.status">
            {{ statusLabel(paper.status) }}
          </div>
        </div>

        <div class="paper-info">
          <div class="paper-title">{{ paper.title }}</div>
          <div class="paper-meta">
            <el-tag :type="subjectTagType(paper.subject)" size="small" effect="dark">{{ paper.subject }}</el-tag>
            <span v-if="paper.exam_type" class="meta-type">{{ paper.exam_type }}</span>
            <span v-if="paper.exam_date" class="meta-date">{{ paper.exam_date }}</span>
          </div>
        </div>

        <div class="paper-actions">
          <el-button size="small" @click="viewPaper(paper)">
            <el-icon><View /></el-icon>
            查看
          </el-button>
          <el-button size="small" :loading="ocrLoadingId === paper.id" @click="ocrPaper(paper)">
            <el-icon><Document /></el-icon>
            OCR 识别
          </el-button>
          <el-popconfirm title="确定删除该试卷？" confirm-button-text="删除" confirm-button-type="danger" @confirm="deletePaper(paper.id)">
            <template #reference>
              <el-button size="small" type="danger" link>
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-popconfirm>
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
        @current-change="fetchPapers"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Upload, View, Document, Delete, Picture } from '@element-plus/icons-vue'
import request from '@/api'
import { useStudentStore } from '@/stores/student'

const studentStore = useStudentStore()

// ─── 常量 ───
const subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
const examTypes = ['日常练习', '周测', '月考', '期中', '期末']

// ─── 状态 ───
const loading = ref(false)
const papers = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const ocrLoadingId = ref(null)

// ─── 筛选 ───
const filterSubject = ref('')
const filterExamType = ref('')
const filterStatus = ref('')

// ─── 上传 ───
const showUpload = ref(false)
const uploading = ref(false)
const uploadFile = ref(null)
const uploadForm = reactive({
  subject: '',
  title: '',
  exam_type: '',
  exam_date: ''
})

// ─── API ───
async function fetchPapers() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterSubject.value) params.subject = filterSubject.value
    if (filterExamType.value) params.exam_type = filterExamType.value
    if (filterStatus.value) params.status = filterStatus.value
    params.student_id = studentStore.currentStudentId || undefined
    const res = await request.get('/v1/exam-papers', { params })
    papers.value = res?.data?.items ?? res?.items ?? []
    total.value = res?.data?.total ?? res?.total ?? 0
  } catch (err) {
    console.error('获取试卷列表失败:', err)
    ElMessage.error('加载试卷列表失败')
    papers.value = []
  } finally {
    loading.value = false
  }
}

function handlePaperFile(file) {
  uploadFile.value = file
}

async function handleUpload() {
  if (!uploadFile.value) {
    ElMessage.warning('请选择试卷图片')
    return
  }
  if (!uploadForm.subject || !uploadForm.title) {
    ElMessage.warning('请填写科目和标题')
    return
  }

  uploading.value = true
  try {
    // 1. 上传图片到 MinIO
    const formData = new FormData()
    formData.append('file', uploadFile.value.raw)
    const uploadRes = await request.post('/v1/exam-papers/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const imagePath = uploadRes?.data?.image_path ?? uploadRes?.image_path

    // 2. 创建试卷记录
    await request.post('/v1/exam-papers', {
      subject: uploadForm.subject,
      title: uploadForm.title,
      exam_type: uploadForm.exam_type || null,
      exam_date: uploadForm.exam_date || null,
      image_path: imagePath,
      student_id: studentStore.currentStudentId || undefined
    })
    ElMessage.success('试卷上传成功')
    showUpload.value = false
    uploadFile.value = null
    uploadForm.subject = ''
    uploadForm.title = ''
    uploadForm.exam_type = ''
    uploadForm.exam_date = ''
    await fetchPapers()
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.message || '上传失败'
    ElMessage.error(msg)
  } finally {
    uploading.value = false
  }
}

async function ocrPaper(paper) {
  ocrLoadingId.value = paper.id
  try {
    const res = await request.post(`/v1/exam-papers/${paper.id}/ocr`)
    const updated = res?.data || res
    Object.assign(paper, updated)
    ElMessage.success('OCR 识别完成')
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.message || 'OCR 识别失败'
    ElMessage.error(msg)
  } finally {
    ocrLoadingId.value = null
  }
}

async function deletePaper(id) {
  try {
    await request.delete(`/v1/exam-papers/${id}`)
    ElMessage.success('删除成功')
    await fetchPapers()
  } catch (err) {
    ElMessage.error('删除失败，请重试')
  }
}

function viewPaper(paper) {
  // 简单实现：在新窗口预览图片
  window.open(paperImageUrl(paper.original_image_path), '_blank')
}

// ─── 工具函数 ───
function paperImageUrl(path) {
  if (!path) return ''
  // 通过 API 代理获取图片
  return `/api/v1/exam-papers/${path}`
}

function statusLabel(status) {
  return { uploaded: '已上传', ocr_done: '已识别', cleaned: '已擦除', annotated: '已标注' }[status] || status
}

const subjectTagColors = {
  '数学': 'primary', '物理': 'cyan', '化学': 'warning',
  '语文': 'success', '英语': '', '生物': 'purple',
  '历史': 'danger', '地理': 'info', '政治': 'danger',
}

function subjectTagType(subject) {
  return subjectTagColors[subject] || 'info'
}

// ─── 初始化 ───
onMounted(() => {
  fetchPapers()
})
</script>

<style scoped>
.paper-library-page {
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

/* ── 筛选 ── */
.filter-card {
  margin-bottom: 16px;
  border-radius: 10px;
}

.filter-card :deep(.el-card__body) {
  padding: 14px 20px;
}

/* ── 上传图标 ── */
.upload-icon {
  font-size: 40px;
  color: var(--el-color-primary);
}

.upload-text {
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-top: 4px;
}

.upload-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}

/* ── 试卷网格 ── */
.paper-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  min-height: 200px;
}

.paper-card {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.15s;
}

.paper-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.paper-image-wrapper {
  position: relative;
  height: 160px;
  overflow: hidden;
  background: var(--el-fill-color-lighter);
}

.paper-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 160px;
  color: var(--el-text-color-placeholder);
}

.paper-status-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  color: #fff;
}

.status-uploaded { background: var(--el-color-info); }
.status-ocr_done { background: var(--el-color-primary); }
.status-cleaned { background: var(--el-color-success); }
.status-annotated { background: var(--el-color-warning); }

.paper-info {
  padding: 12px 14px 8px;
}

.paper-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.meta-type, .meta-date {
  background: var(--el-fill-color-lighter);
  padding: 1px 6px;
  border-radius: 4px;
}

.paper-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* ── 空状态 ── */
.empty-wrapper {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40px;
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
  .paper-grid {
    grid-template-columns: 1fr;
  }
}
</style>
