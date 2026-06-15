<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAdminReports, handleReport } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close, ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(false)
const reports = ref([])
const pagination = ref({ page: 1, page_size: 20, total: 0 })
const statusFilter = ref(route.query.status || '')

const reasonLabels = {
  inappropriate: '内容不当',
  counterfeit: '假冒伪劣',
  fraud: '虚假交易',
  prohibited: '违禁物品',
  other: '其他',
}

const statusTagMap = {
  pending: { type: 'danger', label: '待处理' },
  resolved: { type: 'success', label: '已处理' },
  dismissed: { type: 'info', label: '已驳回' },
}

async function fetchReports() {
  loading.value = true
  try {
    const res = await getAdminReports({
      status: statusFilter.value,
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    })
    const data = res.data.data || res.data
    reports.value = data.reports
    pagination.value = data.pagination
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function handleAction(report, action) {
  try {
    await ElMessageBox.prompt(
      `确定要${action === 'resolve' ? '处理' : '驳回'}该举报吗？可填写处理备注：`,
      action === 'resolve' ? '处理举报' : '驳回举报',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '处理备注（可选）',
        inputType: 'textarea',
      },
    ).then(({ value: note }) => {
      return handleReport(report.id, { action, note: note || '' })
    })
    ElMessage.success('操作成功')
    fetchReports()
  } catch {
    // 取消
  }
}

function onPageChange(page) {
  pagination.value.page = page
  fetchReports()
}

onMounted(fetchReports)
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <el-button class="back-btn" text @click="$router.push('/admin')">
        <el-icon><ArrowLeft /></el-icon>
        返回管理后台
      </el-button>
      <h1 class="page-title">举报管理</h1>
    </div>

    <el-card class="filter-card">
      <div class="filter-row">
        <el-select v-model="statusFilter" @change="fetchReports" style="width: 140px">
          <el-option label="全部" value="" />
          <el-option label="待处理" value="pending" />
          <el-option label="已处理" value="resolved" />
          <el-option label="已驳回" value="dismissed" />
        </el-select>
        <el-button type="primary" @click="fetchReports">刷新</el-button>
      </div>
    </el-card>

    <el-card>
      <el-table v-loading="loading" :data="reports" stripe>
        <el-table-column label="举报人" width="120">
          <template #default="{ row }">
            {{ row.reporter?.nickname || row.reporter?.username }}
          </template>
        </el-table-column>
        <el-table-column label="举报原因" width="110">
          <template #default="{ row }">
            {{ reasonLabels[row.reason] || row.reason }}
          </template>
        </el-table-column>
        <el-table-column label="被举报商品" min-width="180">
          <template #default="{ row }">
            <div class="product-title">{{ row.product?.title }}</div>
          </template>
        </el-table-column>
        <el-table-column label="举报描述" min-width="180">
          <template #default="{ row }">
            <span class="desc-text">{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagMap[row.status]?.type || ''" size="small">
              {{ statusTagMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理备注" min-width="140">
          <template #default="{ row }">
            <span class="desc-text">{{ row.handled_note || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column v-if="statusFilter !== 'resolved' && statusFilter !== 'dismissed'" label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" size="small" :icon="Check" @click="handleAction(row, 'resolve')">处理</el-button>
              <el-button type="info" size="small" :icon="Close" @click="handleAction(row, 'dismiss')">驳回</el-button>
            </template>
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

.product-title {
  font-weight: 500;
}

.desc-text {
  color: #909399;
  font-size: 13px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
