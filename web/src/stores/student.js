import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import request from '@/api'

export const useStudentStore = defineStore('student', () => {
  const students = ref([])
  const currentStudentId = ref(localStorage.getItem('currentStudentId') || '')

  const currentStudent = computed(() => {
    if (!currentStudentId.value) return null
    return students.value.find(s => s.id === currentStudentId.value) || null
  })

  const hasStudents = computed(() => students.value.length > 0)

  async function fetchStudents() {
    const res = await request.get('/v1/students')
    students.value = res
    // 如果还没有选中学生，默认选中第一个
    if (!currentStudentId.value && students.value.length > 0) {
      currentStudentId.value = students.value[0].id
      localStorage.setItem('currentStudentId', currentStudentId.value)
    }
    return res
  }

  function selectStudent(studentId) {
    currentStudentId.value = studentId
    localStorage.setItem('currentStudentId', studentId)
  }

  return {
    students,
    currentStudentId,
    currentStudent,
    hasStudents,
    fetchStudents,
    selectStudent,
  }
})
