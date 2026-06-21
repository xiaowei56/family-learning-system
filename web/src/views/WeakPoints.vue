<template>
  <div class="weak-points-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">薄弱点分析</h2>
        <p class="page-desc">分析知识薄弱环节，获取针对性学习建议与智能练习试卷</p>
      </div>
      <el-button type="primary" :loading="analyzing" @click="handleAnalyze">
        <el-icon><DataAnalysis /></el-icon>
        {{ analyzing ? '分析中...' : '开始分析' }}
      </el-button>
    </div>

    <!-- 未分析时的引导 -->
    <el-empty v-if="!hasData && !analyzing" description="点击上方「开始分析」按钮，系统将基于错题和考试成绩进行智能分析">
      <template #image>
        <el-icon :size="64" style="color: var(--el-color-primary-light-3)"><DataAnalysis /></el-icon>
      </template>
    </el-empty>

    <div v-loading="analyzing" class="content-area">
      <template v-if="hasData">
        <!-- ===== 第一行：雷达图 + 掌握度概览 ===== -->
        <el-row :gutter="20">
          <!-- 雷达图 -->
          <el-col :xs="24" :md="14">
            <el-card class="section-card" shadow="never">
              <template #header><div class="section-title"><el-icon><TrendCharts /></el-icon><span>掌握度雷达图</span></div></template>
              <div ref="radarRef" class="chart-container"></div>
            </el-card>
          </el-col>
          <!-- 掌握度概览 -->
          <el-col :xs="24" :md="10">
            <el-card class="section-card" shadow="never">
              <template #header><div class="section-title"><el-icon><List /></el-icon><span>知识点掌握度</span></div></template>
              <div class="mastery-list">
                <div v-for="wp in weakPoints" :key="wp.id" class="mastery-item">
                  <div class="mastery-header">
                    <el-tag :type="subjectTagType(wp.subject)" size="small" effect="dark">{{ wp.subject }}</el-tag>
                    <span class="mastery-point">{{ wp.knowledge_point }}</span>
                    <el-tag :type="masteryTagType(wp.mastery_level)" size="small" effect="plain" class="mastery-tag">
                      {{ masteryLabel(wp.mastery_level) }}
                    </el-tag>
                  </div>
                  <el-progress
                    :percentage="Math.round(wp.mastery_level * 100)"
                    :color="masteryColor(wp.mastery_level)"
                    :stroke-width="10"
                    :format="() => `${Math.round(wp.mastery_level * 100)}%`"
                  />
                  <div v-if="wp.suggestion" class="mastery-suggestion">{{ wp.suggestion }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- ===== 第二行：诊断报告 + 智能出卷 ===== -->
        <el-row :gutter="20">
          <el-col :xs="24" :md="14">
            <el-card class="section-card" shadow="never">
              <template #header><div class="section-title"><el-icon><Document /></el-icon><span>综合诊断报告</span></div></template>
              <div v-if="advice" class="diagnosis-content">
                <div class="diagnosis-section">
                  <h4>总体诊断</h4>
                  <p>{{ advice.overall_diagnosis || '暂无诊断内容' }}</p>
                </div>
                <div class="diagnosis-section">
                  <h4>学习计划</h4>
                  <p>{{ advice.study_plan || '暂无学习计划' }}</p>
                </div>
                <div class="diagnosis-section">
                  <h4>专项建议</h4>
                  <ul v-if="advice.suggestions?.length">
                    <li v-for="(s, i) in advice.suggestions" :key="i">{{ s }}</li>
                  </ul>
                  <p v-else>暂无专项建议</p>
                </div>
              </div>
              <el-empty v-else description="暂无诊断报告，请先执行分析" :image-size="50" />
            </el-card>
          </el-col>
          <el-col :xs="24" :md="10">
            <el-card class="section-card" shadow="never">
              <template #header><div class="section-title"><el-icon><EditPen /></el-icon><span>智能出卷</span></div></template>
              <el-form label-width="70px">
                <el-form-item label="科目">
                  <el-select v-model="paperForm.subject" placeholder="选择科目" style="width:100%">
                    <el-option v-for="s in subjects" :key="s" :label="s" :value="s" />
                  </el-select>
                </el-form-item>
                <el-form-item label="题数">
                  <el-slider v-model="paperForm.question_count" :min="5" :max="30" :step="5" show-input />
                </el-form-item>
                <el-form-item label="薄弱点" v-if="weakPoints.length">
                  <el-checkbox-group v-model="paperForm.weak_points">
                    <el-checkbox
                      v-for="wp in weakPoints.filter(w => w.subject === paperForm.subject)"
                      :key="wp.id"
                      :label="wp.knowledge_point"
                    />
                  </el-checkbox-group>
                  <div v-if="paperForm.subject && weakPoints.filter(w => w.subject === paperForm.subject).length === 0" class="no-points-hint">
                    该科目暂无薄弱点数据
                  </div>
                </el-form-item>
              </el-form>
              <template #footer>
                <el-button type="primary" :loading="generating" :disabled="!paperForm.subject || !paperForm.weak_points.length" @click="handleGenerate" style="width:100%">
                  <el-icon><MagicStick /></el-icon>
                  {{ generating ? '生成中...' : '生成练习试卷' }}
                </el-button>
              </template>
            </el-card>

            <!-- 最近生成的试卷 -->
            <el-card v-if="papers.length" class="section-card" shadow="never">
              <template #header><div class="section-title"><el-icon><List /></el-icon><span>最近练习试卷</span></div></template>
              <div v-for="p in papers.slice(0, 5)" :key="p.id" class="paper-item" @click="viewPaper(p)">
                <div class="paper-item-info">
                  <span class="paper-item-title">{{ p.title }}</span>
                  <span class="paper-item-meta">{{ p.total_questions }} 题 · {{ p.status === 'completed' ? p.score + '%' : p.status }}</span>
                </div>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </template>
    </div>

    <!-- 试卷详情弹窗 -->
    <el-dialog v-model="showPaper" :title="paperDetail?.title || '练习试卷'" width="700px" destroy-on-close>
      <div v-if="paperDetail" class="paper-detail">
        <el-tabs>
          <el-tab-pane label="题目列表">
            <div v-for="(q, i) in paperDetail.questions" :key="i" class="question-card">
              <div class="q-header">第 {{ i + 1 }} 题</div>
              <div class="q-text">{{ q.problem }}</div>
              <el-collapse>
                <el-collapse-item title="查看答案与解析" name="solution">
                  <div class="q-answer"><strong>答案：</strong>{{ q.answer }}</div>
                  <div class="q-solution"><strong>解析：</strong>{{ q.solution }}</div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-tab-pane>
          <el-tab-pane label="试卷信息">
            <div class="paper-meta-detail">
              <p><strong>科目：</strong>{{ paperDetail.subject }}</p>
              <p><strong>题目总数：</strong>{{ paperDetail.total_questions }}</p>
              <p><strong>针对知识点：</strong>{{ (paperDetail.target_points || []).join('、') }}</p>
              <p><strong>难度分布：</strong>简单 {{ paperDetail.difficulty_distribution?.simple || 0 }} · 中等 {{ paperDetail.difficulty_distribution?.medium || 0 }} · 困难 {{ paperDetail.difficulty_distribution?.hard || 0 }}</p>
              <p><strong>状态：</strong>{{ paperStatusLabel(paperDetail.status) }}</p>
              <p v-if="paperDetail.score != null"><strong>得分率：</strong>{{ paperDetail.score }}%</p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, TrendCharts, List, Document, EditPen, MagicStick, ArrowRight
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import request from '@/api'
import { useStudentStore } from '@/stores/student'

const studentStore = useStudentStore()

const subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']

// ─── 状态 ───
const analyzing = ref(false)
const hasData = ref(false)
const weakPoints = ref([])
const advice = ref(null)
const papers = ref([])

const radarRef = ref(null)
let radarChart = null

const paperForm = ref({ subject: '', question_count: 10, weak_points: [] })
const generating = ref(false)
const showPaper = ref(false)
const paperDetail = ref(null)

// ─── API ───
async function handleAnalyze() {
  analyzing.value = true
  try {
    const res = await request.post('/v1/weak-points/analyze', null, { params: { student_id: studentStore.currentStudentId || undefined } })
    const data = res?.data || res
    weakPoints.value = data?.weak_points || []
    advice.value = { overall_diagnosis: data.overall_diagnosis, study_plan: data.study_plan }
    hasData.value = true
    ElMessage.success('薄弱点分析完成')
    await fetchAdvice()
    await nextTick()
    initRadar()
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.message || '分析失败'
    ElMessage.error(msg)
  } finally {
    analyzing.value = false
  }
}

async function fetchWeakPoints() {
  try {
    const res = await request.get('/v1/weak-points', { params: { student_id: studentStore.currentStudentId || undefined } })
    weakPoints.value = res?.data || res || []
    if (weakPoints.value.length) hasData.value = true
  } catch { /* ignore */ }
}

async function fetchAdvice() {
  try {
    const res = await request.get('/v1/learning-advice', { params: { student_id: studentStore.currentStudentId || undefined } })
    advice.value = res?.data || res
    if (advice.value) hasData.value = true
  } catch { /* ignore */ }
}

async function fetchPapers() {
  try {
    const res = await request.get('/v1/practice-papers', { params: { page_size: 5, student_id: studentStore.currentStudentId || undefined } })
    papers.value = res?.data?.items || res?.items || []
  } catch { /* ignore */ }
}

async function handleGenerate() {
  if (!paperForm.value.subject || !paperForm.value.weak_points.length) {
    ElMessage.warning('请选择科目和至少一个薄弱知识点')
    return
  }
  generating.value = true
  try {
    const res = await request.post('/v1/practice-papers/generate', {
      subject: paperForm.value.subject,
      weak_points: paperForm.value.weak_points,
      question_count: paperForm.value.question_count,
      student_id: studentStore.currentStudentId || undefined
    })
    const paper = res?.data || res
    ElMessage.success(`试卷生成成功！共 ${paper.total_questions} 题`)
    await fetchPapers()
  } catch (err) {
    const msg = err?.response?.data?.detail || err?.message || '生成失败'
    ElMessage.error(msg)
  } finally {
    generating.value = false
  }
}

function viewPaper(paper) {
  paperDetail.value = paper
  showPaper.value = true
}

// ─── 雷达图 ───
function initRadar() {
  if (!radarRef.value) return
  if (radarChart) radarChart.dispose()
  radarChart = echarts.init(radarRef.value)

  const points = weakPoints.value
  if (!points.length) {
    radarChart.setOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { fontSize: 14, color: '#909399' } } })
    return
  }

  const subjects = [...new Set(points.map(p => p.subject))]
  const indicator = points.map(p => ({ name: p.knowledge_point, max: 100 }))
  const seriesData = subjects.map(sub => ({
    name: sub,
    value: points.filter(p => p.subject === sub).map(p => Math.round(p.mastery_level * 100)),
    areaStyle: { opacity: 0.15 }
  }))

  radarChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { data: subjects, bottom: 0, icon: 'circle', itemWidth: 10, itemHeight: 10 },
    radar: {
      indicator,
      center: ['50%', '45%'],
      radius: '60%',
      shape: 'polygon',
      axisName: { color: '#606266', fontSize: 11 },
      splitArea: { areaStyle: { color: ['rgba(64,158,255,0.02)', 'rgba(64,158,255,0.05)'] } }
    },
    series: [{
      type: 'radar',
      data: seriesData,
      lineStyle: { width: 2 },
      symbol: 'circle',
      symbolSize: 6
    }]
  })
}

function handleResize() { if (radarChart) radarChart.resize() }

// ─── 工具函数 ───
const subjectTagColors = {
  '数学': 'primary', '物理': 'cyan', '化学': 'warning',
  '语文': 'success', '英语': '', '生物': 'purple',
  '历史': 'danger', '地理': 'info', '政治': 'danger'
}
function subjectTagType(s) { return subjectTagColors[s] || 'info' }
function masteryTagType(level) { return level >= 0.7 ? 'success' : level >= 0.4 ? 'warning' : 'danger' }
function masteryLabel(level) { return level >= 0.7 ? '良好' : level >= 0.4 ? '一般' : '薄弱' }
function masteryColor(level) { return level >= 0.7 ? '#67c23a' : level >= 0.4 ? '#e6a23c' : '#f56c6c' }
function paperStatusLabel(s) { return { generated: '已生成', started: '进行中', completed: '已完成' }[s] || s }

watch(() => weakPoints.value.length, () => { nextTick(() => initRadar()) })

onMounted(async () => {
  await Promise.all([fetchWeakPoints(), fetchAdvice(), fetchPapers()])
  await nextTick()
  if (hasData.value) initRadar()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (radarChart) { radarChart.dispose(); radarChart = null }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.weak-points-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title { font-size: 22px; font-weight: 600; color: var(--el-text-color-primary); margin: 0 0 4px 0; }
.page-desc { font-size: 14px; color: var(--el-text-color-secondary); margin: 0; }

.content-area { min-height: 300px; }

/* ── 卡片通用 ── */
.section-card { margin-bottom: 20px; border-radius: 10px; border: 1px solid var(--el-border-color-light); }
.section-card :deep(.el-card__header) { padding: 14px 20px; border-bottom: 1px solid var(--el-border-color-light); background: var(--el-fill-color-light); }
.section-title { display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 600; color: var(--el-text-color-primary); }
.section-title .el-icon { font-size: 16px; color: var(--el-color-primary); }

/* ── 雷达图 ── */
.chart-container { width: 100%; height: 360px; }

/* ── 掌握度列表 ── */
.mastery-list { max-height: 360px; overflow-y: auto; }
.mastery-item { padding: 8px 0; border-bottom: 1px solid var(--el-border-color-lighter); }
.mastery-item:last-child { border-bottom: none; }
.mastery-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
.mastery-point { font-size: 14px; color: var(--el-text-color-primary); font-weight: 500; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mastery-tag { flex-shrink: 0; }
.mastery-suggestion { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; line-height: 1.5; }

/* ── 诊断报告 ── */
.diagnosis-content { max-height: 400px; overflow-y: auto; }
.diagnosis-section { margin-bottom: 16px; }
.diagnosis-section h4 { margin: 0 0 6px 0; font-size: 14px; color: var(--el-color-primary); font-weight: 600; }
.diagnosis-section p { margin: 0; font-size: 14px; line-height: 1.8; color: var(--el-text-color-regular); white-space: pre-wrap; }
.diagnosis-section ul { margin: 0; padding-left: 20px; }
.diagnosis-section li { font-size: 14px; line-height: 1.8; color: var(--el-text-color-regular); }

/* ── 智能出卷 ── */
.no-points-hint { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; }
.paper-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--el-border-color-lighter); cursor: pointer; transition: background 0.15s; }
.paper-item:hover { background: var(--el-fill-color-light); margin: 0 -12px; padding: 10px 12px; border-radius: 6px; }
.paper-item:last-child { border-bottom: none; }
.paper-item-info { flex: 1; min-width: 0; }
.paper-item-title { display: block; font-size: 14px; font-weight: 500; color: var(--el-text-color-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.paper-item-meta { font-size: 12px; color: var(--el-text-color-secondary); }

/* ── 试卷详情 ── */
.question-card { padding: 14px; margin-bottom: 12px; background: var(--el-fill-color-lighter); border-radius: 8px; }
.q-header { font-size: 13px; font-weight: 600; color: var(--el-color-primary); margin-bottom: 6px; }
.q-text { font-size: 14px; line-height: 1.7; color: var(--el-text-color-primary); white-space: pre-wrap; margin-bottom: 8px; }
.q-answer, .q-solution { font-size: 13px; line-height: 1.6; color: var(--el-text-color-regular); white-space: pre-wrap; padding: 4px 0; }
.paper-meta-detail p { font-size: 14px; line-height: 2; color: var(--el-text-color-regular); margin: 0; }

/* ── 响应式 ── */
@media (max-width: 768px) {
  .page-header { flex-direction: column; gap: 12px; }
  .chart-container { height: 280px; }
}
</style>
