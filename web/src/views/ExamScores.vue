<template>
  <div class="exam-scores">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>考试成绩</h2>
      <p class="page-desc">记录与分析各科目考试成绩</p>
    </div>

    <!-- ======== 第一部分：成绩录入 ======== -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="section-title">
          <el-icon><EditPen /></el-icon>
          <span>录入考试成绩</span>
        </div>
      </template>
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="80px"
        label-position="top"
        size="default"
      >
        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="科目" prop="subject">
              <el-select v-model="form.subject" placeholder="选择科目" clearable>
                <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="考试类型" prop="exam_type">
              <el-select v-model="form.exam_type" placeholder="选择类型" clearable>
                <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="考试日期" prop="exam_date">
              <el-date-picker
                v-model="form.exam_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="成绩" prop="score" class="score-field">
              <div class="score-input-group">
                <el-input-number
                  v-model="form.score"
                  :min="0"
                  :max="form.total_score || 999"
                  :controls="false"
                  placeholder="得分"
                  style="width: 80px"
                />
                <span class="score-separator">/</span>
                <el-input-number
                  v-model="form.total_score"
                  :min="1"
                  :max="999"
                  :controls="false"
                  placeholder="总分"
                  style="width: 80px"
                />
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :xs="24" :md="18">
            <el-form-item label="备注" prop="notes">
              <el-input
                v-model="form.notes"
                type="textarea"
                :rows="2"
                placeholder="备注信息（选填）"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6" class="form-actions">
            <el-button type="primary" @click="submitForm" :loading="submitting">
              <el-icon><Plus /></el-icon>
              保存
            </el-button>
            <el-button @click="resetForm">
              重置
            </el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- ======== 第二部分：成绩列表 ======== -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="section-title card-header-with-filter">
          <div class="section-title-left">
            <el-icon><List /></el-icon>
            <span>历史成绩</span>
          </div>
          <div class="filter-bar">
            <el-select
              v-model="filterSubject"
              placeholder="全部科目"
              clearable
              style="width: 130px"
              @change="fetchScoreList"
            >
              <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
            </el-select>
            <el-select
              v-model="filterExamType"
              placeholder="全部类型"
              clearable
              style="width: 150px"
              @change="fetchScoreList"
            >
              <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table
        :data="scoreList"
        v-loading="listLoading"
        stripe
        empty-text="暂无成绩记录"
        row-key="id"
      >
        <el-table-column prop="subject" label="科目" width="90" />
        <el-table-column prop="exam_type" label="考试类型" width="110" />
        <el-table-column label="成绩" width="140">
          <template #default="{ row }">
            <span class="score-cell">
              <strong class="score-value">{{ row.score }}</strong>
              <span class="score-divider">/</span>
              <span class="total-value">{{ row.total_score }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="得分率" width="110">
          <template #default="{ row }">
            <el-tag :type="rateTagType(row.score_rate)" size="small" effect="dark">
              {{ formatRate(row.score_rate) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试日期" width="110" />
        <el-table-column prop="notes" label="备注" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              title="确定要删除该记录吗？"
              confirm-button-text="删除"
              confirm-button-type="danger"
              @confirm="deleteRecord(row.id)"
            >
              <template #reference>
                <el-button type="danger" size="small" link>
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- ======== 第三部分：成绩趋势图 ======== -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="section-title card-header-with-filter">
          <div class="section-title-left">
            <el-icon><TrendCharts /></el-icon>
            <span>成绩趋势</span>
          </div>
          <div class="filter-bar">
            <el-select
              v-model="chartSubjects"
              multiple
              placeholder="选择科目（可多选）"
              style="width: 260px"
              collapse-tags
              collapse-tags-tooltip
            >
              <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
            </el-select>
            <el-select
              v-model="chartExamType"
              placeholder="全部类型"
              clearable
              style="width: 150px"
            >
              <el-option v-for="t in examTypes" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
        </div>
      </template>
      <div class="chart-wrapper">
        <div v-if="!chartSubjects.length" class="chart-placeholder">
          <el-icon class="placeholder-icon"><TrendCharts /></el-icon>
          <p>请在上方选择一个或多个科目查看趋势</p>
        </div>
        <div
          v-show="chartSubjects.length"
          ref="chartRef"
          class="chart-container"
        ></div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  EditPen, Plus, List, Delete, TrendCharts
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import request from '@/api/index.js'

// ============ 常量 ============
const subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
const examTypes = ['日常练习', '周测', '月考', '期中', '期末']

const CHART_COLORS = [
  '#409eff', '#67c23a', '#e6a23c', '#f56c6c',
  '#9b59b6', '#1abc9c', '#e67e22', '#2ecc71', '#e74c3c'
]

// ============ 第一部分：录入表单 ============
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  subject: '',
  exam_type: '',
  score: null,
  total_score: null,
  exam_date: '',
  notes: ''
})

const validateScore = (_rule, value, callback) => {
  if (value === null || value === undefined || value === '') {
    callback(new Error('请输入分数'))
  } else if (form.total_score !== null && Number(value) > Number(form.total_score)) {
    callback(new Error('分数不能大于总分'))
  } else {
    callback()
  }
}

const formRules = {
  subject: [{ required: true, message: '请选择科目', trigger: 'change' }],
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  score: [
    { required: true, message: '请输入分数', trigger: 'blur' },
    { type: 'number', min: 0, message: '分数不能为负数', trigger: 'blur' },
    { validator: validateScore, trigger: 'blur' }
  ],
  total_score: [
    { required: true, message: '请输入总分', trigger: 'blur' },
    { type: 'number', min: 1, message: '总分至少为 1', trigger: 'blur' }
  ],
  exam_date: [{ required: true, message: '请选择考试日期', trigger: 'change' }]
}

async function submitForm() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    await request.post('/v1/exam-results', {
      subject: form.subject,
      exam_type: form.exam_type,
      score: Number(form.score),
      total_score: Number(form.total_score),
      exam_date: form.exam_date,
      notes: form.notes || ''
    })
    ElMessage.success('成绩保存成功')
    resetForm()
    await fetchScoreList()
    await fetchTrendData()
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message || '保存失败，请重试'
    ElMessage.error(msg)
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// ============ 第二部分：成绩列表 ============
const scoreList = ref([])
const listLoading = ref(false)
const filterSubject = ref('')
const filterExamType = ref('')

async function fetchScoreList() {
  listLoading.value = true
  try {
    const params = {}
    if (filterSubject.value) params.subject = filterSubject.value
    if (filterExamType.value) params.exam_type = filterExamType.value
    const res = await request.get('/v1/exam-results', { params })
    // 兼容 wrapper 和裸数组
    scoreList.value = Array.isArray(res) ? res : (res?.data ?? [])
  } catch {
    ElMessage.error('加载成绩列表失败')
    scoreList.value = []
  } finally {
    listLoading.value = false
  }
}

async function deleteRecord(id) {
  try {
    await request.delete(`/v1/exam-results/${id}`)
    ElMessage.success('删除成功')
    await fetchScoreList()
    await fetchTrendData()
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message || '删除失败'
    ElMessage.error(msg)
  }
}

function rateTagType(rate) {
  if (rate == null) return 'info'
  const pct = rate <= 1 ? rate * 100 : rate
  if (pct > 80) return 'success'
  if (pct > 60) return 'warning'
  return 'danger'
}

function formatRate(rate) {
  if (rate == null) return '--'
  const pct = rate <= 1 ? rate * 100 : rate
  return `${pct.toFixed(1)}%`
}

// ============ 第三部分：趋势图表 ============
const chartRef = ref(null)
const chartSubjects = ref([])
const chartExamType = ref('')
const trendLoading = ref(false)

let chartInstance = null

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)
}

function disposeChart() {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

async function fetchTrendData() {
  if (!chartSubjects.value.length) {
    if (chartInstance) {
      chartInstance.clear()
      chartInstance.setOption({ title: { text: '', left: 'center' } })
    }
    return
  }

  trendLoading.value = true
  try {
    const params = {
      subjects: chartSubjects.value.join(',')
    }
    if (chartExamType.value) params.exam_type = chartExamType.value

    const res = await request.get('/v1/exam-results/trend', { params })
    const data = Array.isArray(res) ? res : (res?.data ?? [])
    updateChart(data)
  } catch {
    ElMessage.error('加载趋势数据失败')
  } finally {
    trendLoading.value = false
  }
}

function updateChart(data) {
  if (!chartInstance || !chartRef.value) return

  // 收集所有日期并排序
  const dateSet = new Set()
  const seriesMap = new Map()

  data.forEach((item) => {
    const records = item.records || []
    seriesMap.set(item.subject, records)
    records.forEach((r) => dateSet.add(r.exam_date))
  })

  const sortedDates = Array.from(dateSet).sort()

  if (!sortedDates.length) {
    chartInstance.clear()
    chartInstance.setOption({
      title: {
        text: '暂无趋势数据',
        left: 'center',
        top: 'center',
        textStyle: { fontSize: 14, color: '#909399' }
      }
    })
    return
  }

  // 构建 series
  const series = []
  const legendData = []
  data.forEach((item, idx) => {
    const records = item.records || []
    const recordMap = new Map(records.map((r) => [r.exam_date, r.score_rate]))
    const values = sortedDates.map((d) => {
      const v = recordMap.get(d)
      if (v == null) return null
      return v <= 1 ? Number((v * 100).toFixed(1)) : Number(v.toFixed(1))
    })
    legendData.push(item.subject)
    series.push({
      name: item.subject,
      type: 'line',
      data: values,
      smooth: true,
      lineStyle: { width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: CHART_COLORS[idx % CHART_COLORS.length] },
      connectNulls: false
    })
  })

  const option = {
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v) => (v != null ? `${v}%` : '--')
    },
    legend: {
      data: legendData,
      top: 0,
      icon: 'circle',
      itemWidth: 10,
      itemHeight: 10
    },
    grid: {
      left: 55,
      right: 30,
      bottom: 40,
      top: 50
    },
    xAxis: {
      type: 'category',
      data: sortedDates,
      axisLabel: {
        rotate: 30,
        fontSize: 12
      },
      axisLine: { lineStyle: { color: '#dcdfe6' } },
      axisTick: { alignWithLabel: true }
    },
    yAxis: {
      type: 'value',
      name: '得分率(%)',
      min: 0,
      max: 100,
      splitLine: { lineStyle: { type: 'dashed', color: '#eee' } },
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series
  }

  chartInstance.setOption(option, true)
}

function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// ============ 监听器 ============
watch([chartSubjects, chartExamType], () => {
  nextTick(() => {
    if (chartSubjects.value.length) {
      fetchTrendData()
    } else if (chartInstance) {
      chartInstance.clear()
    }
  })
}, { deep: true })

// ============ 生命周期 ============
onMounted(async () => {
  await fetchScoreList()
  await nextTick()
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  disposeChart()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.exam-scores {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* ---- 页面标题 ---- */
.page-header {
  margin-bottom: 20px;
}
.page-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: var(--main-text, #303133);
  margin-bottom: 4px;
}
.page-desc {
  font-size: 14px;
  color: var(--main-text-secondary, #909399);
}

/* ---- 卡片通用 ---- */
.section-card {
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}
.section-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.section-title .el-icon {
  font-size: 16px;
  color: var(--primary, #409eff);
}

/* ---- 表头含筛选 ---- */
.card-header-with-filter {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.section-title-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

/* ---- 表单 ---- */
.score-input-group {
  display: flex;
  align-items: center;
  gap: 4px;
}
.score-separator {
  font-size: 16px;
  font-weight: 300;
  color: #909399;
  padding: 0 4px;
}
.score-field :deep(.el-form-item__content) {
  align-items: center;
}
.form-actions {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding-bottom: 2px;
}

/* ---- 表格成绩列 ---- */
.score-cell {
  display: inline-flex;
  align-items: baseline;
  gap: 3px;
}
.score-value {
  font-size: 15px;
  color: #303133;
}
.score-divider {
  color: #c0c4cc;
  font-size: 13px;
}
.total-value {
  color: #909399;
  font-size: 13px;
}

/* ---- 图表 ---- */
.chart-wrapper {
  position: relative;
  min-height: 360px;
}
.chart-container {
  width: 100%;
  height: 360px;
}
.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 360px;
  color: #c0c4cc;
  font-size: 14px;
  background: #fafafa;
  border-radius: 6px;
}
.placeholder-icon {
  font-size: 48px;
  margin-bottom: 12px;
  color: #dcdfe6;
}

/* ---- 响应式调整 ---- */
@media (max-width: 768px) {
  .exam-scores {
    padding: 16px;
  }
  .card-header-with-filter {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-bar {
    width: 100%;
  }
  .filter-bar .el-select {
    flex: 1;
  }
  .chart-container {
    height: 280px;
  }
  .chart-wrapper {
    min-height: 280px;
  }
}
</style>
