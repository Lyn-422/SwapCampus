<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAdminOrders } from '@/api/admin'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(false)
const orders = ref([])
const pagination = ref({ page: 1, page_size: 20, total: 0 })
const filters = ref({ status: route.query.status || '', search: '' })

const statusOptions = [
  { value: '', label: '全部状态' },
  { value: 'pending', label: '等待卖家确认' },
  { value: 'accepted', label: '已接受，待面交' },
  { value: 'face_confirm', label: '面交确认中' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
  { value: 'rejected', label: '已拒绝' },
]

const statusTagMap = {
  pending: { type: 'warning', label: '等待确认' },
  accepted: { type: 'primary', label: '待面交' },
  face_confirm: { type: 'warning', label: '面交确认中' },
  completed: { type: 'success', label: '已完成' },
  cancelled: { type: 'info', label: '已取消' },
  rejected: { type: 'danger', label: '已拒绝' },
}

async function fetchOrders() {
  loading.value = true
  try {
    const res = await getAdminOrders({
      status: filters.value.status,
      search: filters.value.search,
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    })
    const data = res.data.data || res.data
    orders.value = data.orders
    pagination.value = data.pagination
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.value = { status: '', search: '' }
  pagination.value.page = 1
  fetchOrders()
}

function onPageChange(page) {
  pagination.value.page = page
  fetchOrders()
}

onMounted(fetchOrders)
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <el-button class="back-btn" text @click="$router.push('/admin')">
        <el-icon><ArrowLeft /></el-icon>
        返回管理后台
      </el-button>
      <h1 class="page-title">订单管理</h1>
    </div>

    <el-card class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="filters.search"
          placeholder="搜索商品名/学号..."
          clearable
          @clear="fetchOrders"
          @keyup.enter="fetchOrders"
          style="width: 240px"
        />
        <el-select v-model="filters.status" @change="fetchOrders" style="width: 160px">
          <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-button type="primary" @click="fetchOrders">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <el-card>
      <el-table v-loading="loading" :data="orders" stripe>
        <el-table-column label="商品" min-width="140">
          <template #default="{ row }">
            {{ row.product?.title || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="买家" width="120">
          <template #default="{ row }">
            <div>{{ row.buyer?.nickname || row.buyer?.username || '—' }}</div>
            <div class="sub-text">{{ row.buyer?.username }}</div>
          </template>
        </el-table-column>
        <el-table-column label="卖家" width="120">
          <template #default="{ row }">
            <div>{{ row.seller?.nickname || row.seller?.username || '—' }}</div>
            <div class="sub-text">{{ row.seller?.username }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagMap[row.status]?.type || 'info'" size="small">
              {{ statusTagMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="面交地点" width="120">
          <template #default="{ row }">
            {{ row.meet_location || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="面交时间" width="150">
          <template #default="{ row }">
            {{ row.meet_time ? new Date(row.meet_time).toLocaleString('zh-CN') : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="取消原因" min-width="140">
          <template #default="{ row }">
            {{ row.cancel_reason || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="完成时间" width="160">
          <template #default="{ row }">
            {{ row.completed_at ? new Date(row.completed_at).toLocaleString('zh-CN') : '—' }}
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
  max-width: 1400px;
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

.sub-text {
  font-size: 12px;
  color: #909399;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
