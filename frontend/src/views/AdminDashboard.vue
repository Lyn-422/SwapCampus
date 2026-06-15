<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboard } from '@/api/admin'
import { ElMessage } from 'element-plus'
import {
  User, ShoppingCart, Document, Warning, Checked,
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(true)
const stats = ref({
  total_users: 0,
  pending_registrations: 0,
  active_products: 0,
  pending_products: 0,
  pending_orders: 0,
  completed_orders: 0,
  pending_reports: 0,
  recent_registrations: [],
})

async function fetchDashboard() {
  loading.value = true
  try {
    const res = await getDashboard()
    stats.value = res.data.data || res.data
  } catch {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="admin-dashboard">
    <h1 class="page-title">管理后台</h1>

    <div v-loading="loading" class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon users">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_users }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card clickable" @click="router.push({ path: '/admin/users', query: { status: 'pending' } })">
        <div class="stat-inner">
          <div class="stat-icon pending">
            <el-icon :size="28"><Checked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value pending">{{ stats.pending_registrations }}</div>
            <div class="stat-label">待审核注册</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon products">
            <el-icon :size="28"><ShoppingCart /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.active_products }}</div>
            <div class="stat-label">在售商品</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon pending">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending_products }}</div>
            <div class="stat-label">待审核商品</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon orders">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending_orders }}</div>
            <div class="stat-label">待处理订单</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-inner">
          <div class="stat-icon reports">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending_reports }}</div>
            <div class="stat-label">待处理举报</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="detail-row">
      <el-card class="detail-card">
        <template #header>
          <span>最近注册用户</span>
        </template>
        <el-table :data="stats.recent_registrations" stripe size="default">
          <el-table-column prop="username" label="学号" min-width="120" />
          <el-table-column prop="nickname" label="昵称" min-width="100" />
          <el-table-column prop="credit_score" label="信用分" width="80" align="center" />
          <el-table-column label="注册时间" min-width="160">
            <template #default="{ row }">
              {{ new Date(row.date_joined).toLocaleString('zh-CN') }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="detail-card">
        <template #header>
          <span>快捷操作</span>
        </template>
        <div class="quick-actions">
          <el-button type="primary" @click="$router.push('/admin/products')">
            <el-icon><ShoppingCart /></el-icon>
            商品审核
          </el-button>
          <el-button type="warning" @click="$router.push('/admin/reports')">
            <el-icon><Warning /></el-icon>
            举报处理
          </el-button>
          <el-button type="info" @click="$router.push('/admin/users')">
            <el-icon><User /></el-icon>
            用户管理
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--color-brand-dark);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
}

.stat-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-card.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.stat-icon.users { background: #409eff; }
.stat-icon.products { background: #43a047; }
.stat-icon.pending { background: #e6a23c; }
.stat-icon.orders { background: #e6a23c; }
.stat-icon.reports { background: #f56c6c; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}
.stat-value.pending { color: #e6a23c; }

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 2px;
}

.detail-row {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
}

.detail-card {
  border-radius: 12px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-actions .el-button {
  justify-content: flex-start;
  height: 44px;
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .detail-row { grid-template-columns: 1fr; }
}
</style>
