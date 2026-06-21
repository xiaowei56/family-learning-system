<template>
  <div class="settings-container">
    <el-card class="settings-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Setting /></el-icon>
          <span>用户设置</span>
        </div>
      </template>
      
      <!-- 个人信息 -->
      <el-divider content-position="left">个人信息</el-divider>
      <el-card class="info-card" shadow="never">
        <div class="info-content">
          <div class="info-item">
            <span class="info-label">用户名：</span>
            <span class="info-value">{{ userInfo.username }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">身份：</span>
            <span class="info-value role-badge" :class="userInfo.role === 'parent' ? 'parent-role' : 'student-role'">
              {{ userInfo.role === 'parent' ? '家长' : '学生' }}
            </span>
          </div>
        </div>
      </el-card>
      
      <!-- 学生管理 -->
      <el-divider content-position="left">学生管理</el-divider>
      <div class="students-section">
        <div class="section-header">
          <h3>学生资料</h3>
          <el-button type="primary" size="small" @click="showAddStudentDialog = true">
            <el-icon><Plus /></el-icon>
            添加学生
          </el-button>
        </div>
        
        <el-empty v-if="students.length === 0" description="暂无学生资料" />
        
        <div class="students-grid" v-else>
          <el-card 
            v-for="student in students" 
            :key="student.id" 
            class="student-card"
            shadow="never"
          >
            <div class="student-card-content">
              <div class="student-info">
                <h4 class="student-name">{{ student.name }}</h4>
                <div class="student-meta">
                  <el-tag size="small" :type="getGradeTagType(student.grade_level)">
                    {{ student.grade_level }}
                  </el-tag>
                </div>
              </div>
              <div class="student-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  circle
                  @click="editStudent(student)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  circle
                  @click="deleteStudent(student.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 科目管理 -->
      <el-divider content-position="left">科目管理</el-divider>
      <div class="subjects-section">
        <div class="section-header">
          <h3>可选科目</h3>
          <div class="subject-controls">
            <span class="grade-label">年级：</span>
            <el-select 
              v-model="selectedGrade" 
              placeholder="选择年级"
              size="small"
              @change="onGradeChange"
            >
              <el-option label="小学" value="小学" />
              <el-option label="初中" value="初中" />
              <el-option label="高中" value="高中" />
            </el-select>
          </div>
        </div>
        
        <el-checkbox-group v-model="selectedSubjects" class="subjects-grid">
          <el-checkbox 
            v-for="subject in filteredSubjects" 
            :key="subject.id" 
            :label="subject.name"
            :value="subject.name"
            class="subject-checkbox"
          >
            <div class="subject-item">
              <el-icon :class="subject.icon" />
              <span>{{ subject.name }}</span>
            </div>
          </el-checkbox>
        </el-checkbox-group>
        
        <div class="save-section">
          <el-button 
            type="primary" 
            size="large"
            :loading="saving"
            @click="saveSubjects"
          >保存设置</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 添加/编辑学生对话框 -->
    <el-dialog
      v-model="showAddStudentDialog"
      :title="editingStudent ? '编辑学生' : '添加学生'"
      width="400px"
      @closed="resetStudentForm"
    >
      <el-form :model="studentForm" :rules="studentRules" ref="studentFormRef">
        <el-form-item label="学生姓名" prop="name">
          <el-input v-model="studentForm.name" placeholder="请输入学生姓名" />
        </el-form-item>
        
        <el-form-item label="年级" prop="grade_level">
          <el-select v-model="studentForm.grade_level" placeholder="请选择年级">
            <el-option label="小学" value="小学" />
            <el-option label="初中" value="初中" />
            <el-option label="高中" value="高中" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddStudentDialog = false">取消</el-button>
        <el-button type="primary" @click="saveStudent" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus, Edit, Delete } from '@element-plus/icons-vue'
import request from '@/api'

// 响应式状态
const students = ref([])
const selectedGrade = ref('小学')
const selectedSubjects = ref([])
const allSubjects = ref([])
const showAddStudentDialog = ref(false)
const editingStudent = ref(false)
const saving = ref(false)

// 学生表单
const studentFormRef = ref()
const studentForm = reactive({
  id: null,
  name: '',
  grade_level: ''
})

const studentRules = {
  name: [
    { required: true, message: '请输入学生姓名', trigger: 'blur' }
  ],
  grade_level: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ]
}

// 用户信息
const userInfo = ref({
  username: '张三',
  role: 'parent'
})

// 科目定义
const subjectsList = [
  { id: 1, name: '数学', icon: 'el-icon-Operation', grade: ['小学', '初中', '高中'] },
  { id: 2, name: '物理', icon: 'el-icon-Basketball', grade: ['初中', '高中'] },
  { id: 3, name: '化学', icon: 'el-icon-Atom', grade: ['高中'] },
  { id: 4, name: '语文', icon: 'el-icon-Edit', grade: ['小学', '初中', '高中'] },
  { id: 5, name: '英语', icon: 'el-icon-World', grade: ['小学', '初中', '高中'] },
  { id: 6, name: '生物', icon: 'el-icon-Direction', grade: ['初中', '高中'] },
  { id: 7, name: '历史', icon: 'el-icon-History', grade: ['初中', '高中'] },
  { id: 8, name: '地理', icon: 'el-icon-Map', grade: ['初中', '高中'] },
  { id: 9, name: '政治', icon: 'el-icon-Reading', grade: ['高中'] }
]

// 计算属性
const filteredSubjects = computed(() => {
  return subjectsList.filter(subject => subject.grade.includes(selectedGrade.value))
});

// 方法
const getGradeTagType = (grade) => {
  const map = {
    '小学': 'success',
    '初中': 'warning',
    '高中': 'danger'
  };
  return map[grade] || '';
};

const getGradeLabel = (grade) => {
  return grade || '';
};

// 生命周期
onMounted(() => {
  fetchStudents();
  fetchUserInfo();
  fetchSubjects();
});

// API 调用
async function fetchStudents() {
  try {
    const res = await request.get('/v1/students');
    students.value = res;
  } catch (error) {
    console.error('获取学生列表失败:', error);
    ElMessage.error('获取学生列表失败');
  }
}

async function fetchUserInfo() {
  try {
    const res = await request.get('/v1/auth/profile');
    userInfo.value = res;
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
}

async function fetchSubjects() {
  try {
    const res = await request.get('/v1/subjects');
    allSubjects.value = res;
    // 设置默认选中的科目
    selectedSubjects.value = res.map(s => s.name);
  } catch (error) {
    console.error('获取科目列表失败:', error);
    // 使用默认科目列表
    selectedSubjects.value = subjectsList
      .filter(s => s.grade.includes(selectedGrade.value))
      .map(s => s.name);
  }
}

async function saveStudent() {
  if (!studentFormRef.value) return;
  
  try {
    await studentFormRef.value.validate();
    saving.value = true;
    
    if (editingStudent.value) {
      await request.put(`/v1/students/${studentForm.id}`, {
        name: studentForm.name,
        grade_level: studentForm.grade_level
      });
      ElMessage.success('学生信息更新成功');
    } else {
      await request.post('/v1/students', {
        name: studentForm.name,
        grade_level: studentForm.grade_level
      });
      ElMessage.success('学生添加成功');
    }
    
    showAddStudentDialog.value = false;
    fetchStudents();
    
  } catch (error) {
    console.error('保存学生信息失败:', error);
    ElMessage.error('保存失败，请稍后重试');
  } finally {
    saving.value = false;
  }
}

async function deleteStudent(id) {
  try {
    await ElMessageBox.confirm('确定要删除该学生吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await request.delete(`/v1/students/${id}`);
    ElMessage.success('学生删除成功');
    fetchStudents();
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除学生失败:', error);
      ElMessage.error('删除失败，请稍后重试');
    }
  }
}

async function saveSubjects() {
  try {
    saving.value = true;
    
    await request.post('/v1/users/subjects', {
      subjects: selectedSubjects.value
    });
    
    ElMessage.success('科目设置保存成功');
    
  } catch (error) {
    console.error('保存科目设置失败:', error);
    ElMessage.error('保存失败，请稍后重试');
  } finally {
    saving.value = false;
  }
}

function editStudent(student) {
  editingStudent.value = true;
  studentForm.id = student.id;
  studentForm.name = student.name;
  studentForm.grade_level = student.grade_level;
  showAddStudentDialog.value = true;
}

function resetStudentForm() {
  studentForm.id = null;
  studentForm.name = '';
  studentForm.grade_level = '';
  editingStudent.value = false;
}

function onGradeChange() {
  // 根据年级筛选科目
  const availableSubjects = subjectsList
    .filter(subject => subject.grade.includes(selectedGrade.value))
    .map(subject => subject.name);
  
  // 更新选中的科目，只保留当前年级可用的科目
  selectedSubjects.value = selectedSubjects.value.filter(subject => 
    availableSubjects.includes(subject)
  );
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.settings-card {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-icon {
  color: #409eff;
}

.info-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.info-content {
  display: flex;
  gap: 40px;
  padding: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.info-label {
  color: #606266;
  font-weight: 500;
}

.info-value {
  color: #303133;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.parent-role {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.student-role {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.subject-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.grade-label {
  color: #606266;
  font-size: 14px;
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.student-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.student-card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.student-info {
  flex: 1;
}

.student-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.student-meta {
  margin-bottom: 0;
}

.student-actions {
  display: flex;
  gap: 8px;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.subject-checkbox {
  height: auto !important;
}

.subject-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 15px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.subject-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
  transform: translateY(-2px);
}

.subject-checkbox :deep(.el-checkbox__label) {
  width: 100%;
  height: 100%;
}

.subject-icon {
  font-size: 24px;
  color: #409eff;
}

.save-section {
  text-align: center;
  margin-top: 30px;
}

.el-divider {
  margin: 30px 0;
}

:deep(.el-divider__text) {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
</style>
