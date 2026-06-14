<script setup>
import { ref, onMounted } from 'vue'
import { getAdminUsers, banUser } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const loading = ref(false)
const users = ref([])
const pagination = ref({ page: 1, page_size: 20, total: 0 })
const filters = ref({ search: '', is_active: '' })

const creditLevelMap = {
  excellent: { type: 'success', label: '优秀' },
  good: { type: '', label: '良好' },
  fair: { type: 'warning', label: '一般' },
  poor: { type: 'danger', label: '较差' },
}

function creditLevel(score) {
  if (score >= 150) return 'excellent'
  if (score >= 100) return 'good'
  if (score >= 60) return 'fair'
  return 'poor'
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await getAdminUsers({
      search: filters.value.search,
      is_active: filters.value.is_active,
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    })
    const data = res.data.data || res.data
    users.value = data.users
    pagination.value = data.pagination
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function handleBan(user) {
  const action = user.is_active ? '封禁' : '解封'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户「${user.nickname || user.username}」吗？`,
      action,
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    await banUser(user.id, !user.is_active)
    ElMessage.success(`${action}成功`)
    fetchUsers()
  } catch {
    // 取消
  }
}

function onPageChange(page) {
  pagination.value.page = page
  fetchUsers()
}

onMounted(fetchUsers)
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <el-button class="back-btn" text @click="$router.push('/admin')">
        <el-icon><ArrowLeft /></el-icon>
        返回管理后台
      </el-button>
      <h1 class="page-title">用户管理</h1>
    </div>

    <el-card class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="filters.search"
          placeholder="搜索学号或昵称..."
          clearable
          @clear="fetchUsers"
          @keyup.enter="fetchUsers"
          style="width: 240px"
        />
        <el-select v-model="filters.is_active" @change="fetchUsers" style="width: 130px">
          <el-option label="全部" value="" />
          <el-option label="正常" value="true" />
          <el-option label="已封禁" value="false" />
        </el-select>
        <el-button type="primary" @click="fetchUsers">查询</el-button>
      </div>
    </el-card>

    <el-card>
      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column label="学号" width="120">
          <template #default="{ row }">
            {{ row.username }}
          </template>
        </el-table-column>
        <el-table-column label="昵称" width="120">
          <template #default="{ row }">
            {{ row.nickname || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="校区" width="100">
          <template #default="{ row }">
            {{ row.campus || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="信用分" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="creditLevelMap[creditLevel(row.credit_score)]?.type || ''" size="small">
              {{ row.credit_score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '已封禁' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.is_staff" style="color: #409eff; font-weight: 500">管理员</span>
            <span v-else style="color: #909399">用户</span>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.date_joined).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_staff"
              :type="row.is_active ? 'danger' : 'success'"
              size="small"
              @click="handleBan(row)"
            >
              {{ row.is_active ? '封禁' : '解封' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="pagination.total > pagination.page_size">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="pagination.total"
          :page-size="pagination.page_size"
          :current-page="pagination.page"
          @current-change="onPageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}

.page-header {
  margin-bottom: 16px;
}

.back-btn {
  margin-bottom: 8px;
  padding-left: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-brand-dark);
}

.filter-card {
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
