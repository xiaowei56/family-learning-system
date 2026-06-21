<template>
  <div class="study-records-page">
    <!-- 顶部工具栏 -->
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="subjectFilter"
          placeholder="全部科目"
          clearable
          @change="fetchRecords"
          style="width: 160px"
        >
          <el-option
            v-for="s in subjectOptions"
            :key="s.value"
            :label="s.label"
            :value="s.value"
          />
        </el-select>
        <el-input
          v-model="searchTitle"
          placeholder="搜索标题……"
          clearable
          style="width: 200px"
          @input="fetchRecords"
        />
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新增记录
      </el-button>
    </div>

    <!-- 记录表格 -->
    <el-table
      :data="records"
      v-loading="loading"
      style="width: 100%"
      :default-expand-all="false"
      row-key="id"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="expanded-content">
            <p class="content-label">学习内容：</p>
            <div class="content-text">{{ row.content }}</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="subject" label="科目" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="subjectTagType(row.subject)" effect="plain">
            {{ row.subject }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />

      <el-table-column label="标签" width="200">
        <template #default="{ row }">
          <template v-if="getTagList(row).length">
            <el-tag
              v-for="tag in getTagList(row).slice(0, 4)"
              :key="tag"
              size="small"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
            <el-tag v-if="getTagList(row).length > 4" size="small" type="info">
              +{{ getTagList(row).length - 4 }}
            </el-tag>
          </template>
          <span v-else class="no-tag">—</span>
        </template>
      </el-table-column>

      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 空状态 -->
    <el-empty v-if="!loading && records.length === 0" description="暂无学习记录">
      <el-button type="primary" @click="openCreateDialog">新增第一条记录</el-button>
    </el-empty>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增学习记录' : '编辑学习记录'"
      width="640px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="60px"
        @submit.prevent="handleSave"
      >
        <el-form-item label="科目" prop="subject">
          <el-select v-model="form.subject" placeholder="请选择科目" style="width: 100%">
            <el-option
              v-for="s in subjectOptions"
              :key="s.value"
              :label="s.label"
              :value="s.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请输入学习内容……"
            maxlength="10000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="标签">
          <div class="tag-input-wrapper">
            <el-tag
              v-for="(tag, idx) in form.tags"
              :key="idx"
              closable
              :disable-transitions="false"
              @close="removeTag(idx)"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="tagInputVisible"
              ref="tagInputRef"
              v-model="tagInputValue"
              size="small"
              placeholder="输入标签后回车"
              @keyup.enter="confirmTag"
              @blur="confirmTag"
              class="tag-input"
            />
            <el-button v-else size="small" @click="showTagInput">+ 添加标签</el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/api'
import { useStudentStore } from '@/stores/student'

const studentStore = useStudentStore()

// ─── 科目选项 ───
const subjectOptions = [
  { label: '数学', value: '数学' },
  { label: '物理', value: '物理' },
  { label: '化学', value: '化学' },
  { label: '语文', value: '语文' },
  { label: '英语', value: '英语' },
  { label: '生物', value: '生物' },
  { label: '历史', value: '历史' },
  { label: '地理', value: '地理' },
  { label: '政治', value: '政治' },
]

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
  const color = subjectTagColors[subject]
  if (!color) return 'info'
  return color
}

// ─── 状态 ───
const loading = ref(false)
const saving = ref(false)
const records = ref([])
const subjectFilter = ref('')
const searchTitle = ref('')
const dialogVisible = ref(false)
const dialogMode = ref('create') // 'create' | 'edit'
const editingId = ref(null)
const formRef = ref()

const defaultForm = {
  subject: '',
  title: '',
  content: '',
  tags: [],
}

const form = reactive({ ...defaultForm })
const formRules = {
  subject: [{ required: true, message: '请选择科目', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入学习内容', trigger: 'blur' }],
}

// ─── 标签输入 ───
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref()

function showTagInput() {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

function confirmTag() {
  const val = tagInputValue.value.trim()
  if (val && !form.tags.includes(val)) {
    form.tags.push(val)
  }
  tagInputVisible.value = false
  tagInputValue.value = ''
}

function removeTag(idx) {
  form.tags.splice(idx, 1)
}

// ─── 工具函数 ───
function getTagList(row) {
  if (!row.tags) return []
  if (Array.isArray(row.tags)) return row.tags
  try {
    const parsed = JSON.parse(row.tags)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return row.tags.split(',').filter(Boolean).map((t) => t.trim())
  }
}

function tagsToString(tags) {
  return JSON.stringify(tags)
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ─── API 操作 ───
async function fetchRecords() {
  loading.value = true
  try {
    const params = {
      student_id: studentStore.currentStudentId || undefined,
    }
    if (subjectFilter.value) params.subject = subjectFilter.value
    if (searchTitle.value) params.title = searchTitle.value
    const res = await request.get('/v1/study-records', { params })
    records.value = Array.isArray(res) ? res : res.data || []
  } catch (err) {
    console.error('获取学习记录失败:', err)
    ElMessage.error('获取学习记录失败')
    records.value = []
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.subject = ''
  form.title = ''
  form.content = ''
  form.tags = []
  editingId.value = null
  tagInputVisible.value = false
  tagInputValue.value = ''
}

function openCreateDialog() {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row) {
  dialogMode.value = 'edit'
  editingId.value = row.id
  form.subject = row.subject
  form.title = row.title
  form.content = row.content
  form.tags = getTagList(row)
  tagInputVisible.value = false
  tagInputValue.value = ''
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true
  const payload = {
    subject: form.subject,
    title: form.title,
    content: form.content,
    tags: tagsToString(form.tags),
    student_id: studentStore.currentStudentId || undefined,
  }

  try {
    if (dialogMode.value === 'create') {
      await request.post('/v1/study-records', payload)
      ElMessage.success('新增成功')
    } else {
      await request.put(`/v1/study-records/${editingId.value}`, payload)
      ElMessage.success('修改成功')
    }
    dialogVisible.value = false
    await fetchRecords()
  } catch (err) {
    console.error('保存失败:', err)
    ElMessage.error('保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除「${row.title}」吗？此操作不可恢复。`,
      '确认删除',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    await request.delete(`/v1/study-records/${row.id}`)
    ElMessage.success('删除成功')
    await fetchRecords()
  } catch (err) {
    // 取消删除不做处理
    if (err !== 'cancel') {
      console.error('删除失败:', err)
    }
  }
}

// ─── 初始化 ───
fetchRecords()
</script>

<style scoped>
.study-records-page {
  padding: 0;
}

/* ── 工具栏 ── */
.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ── 展开内容 ── */
.expanded-content {
  padding: 16px 32px;
}

.content-label {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  font-size: 14px;
}

.content-text {
  color: var(--el-text-color-regular);
  line-height: 1.7;
  white-space: pre-wrap;
  font-size: 14px;
}

/* ── 标签 ── */
.tag-item {
  margin-right: 6px;
  margin-bottom: 4px;
}

.no-tag {
  color: var(--el-text-color-placeholder);
  font-size: 13px;
}

/* ── 标签输入 ── */
.tag-input-wrapper {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  min-height: 32px;
}

.tag-input {
  width: 120px;
}

/* ── 空状态 ── */
.el-empty {
  margin-top: 60px;
}
</style>
