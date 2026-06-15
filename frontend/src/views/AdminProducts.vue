<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAdminProducts, moderateProduct } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Hide, ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(false)
const products = ref([])
const pagination = ref({ page: 1, page_size: 20, total: 0 })
const filters = ref({ status: route.query.status || 'pending', search: '' })

// 驳回弹窗相关
const rejectDialogVisible = ref(false)
const rejectForm = ref({
  productId: '',
  productTitle: '',
  type: 'other',
  reason: '',
})

const rejectTypes = [
  { value: 'human_trafficking', label: '贩卖人口' },
  { value: 'prohibited_items', label: '违规物品/违禁品' },
  { value: 'unclear_images', label: '图片不清晰' },
  { value: 'unfair_price', label: '价格虚高' },
  { value: 'false_description', label: '描述不实' },
  { value: 'other', label: '其他' },
]

const statusOptions = [
  { value: 'pending', label: '待审核' },
  { value: 'active', label: '在售' },
  { value: 'hidden', label: '已下架' },
  { value: 'sold', label: '已售出' },
  { value: 'reserved', label: '已预定' },
  { value: '', label: '全部状态' },
]

const statusTagMap = {
  pending: { type: 'warning', label: '待审核' },
  active: { type: 'success', label: '在售' },
  hidden: { type: 'info', label: '已下架' },
  sold: { type: '', label: '已售出' },
  reserved: { type: '', label: '已预定' },
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await getAdminProducts({
      status: filters.value.status,
      search: filters.value.search,
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    })
    const data = res.data.data || res.data
    products.value = data.products
    pagination.value = data.pagination
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function openRejectDialog(product) {
  rejectForm.value = {
    productId: product.id,
    productTitle: product.title,
    type: 'other',
    reason: '',
  }
  rejectDialogVisible.value = true
}

async function submitReject() {
  if (!rejectForm.value.type) {
    ElMessage.warning('请选择驳回类型')
    return
  }
  try {
    await moderateProduct(
      rejectForm.value.productId,
      'hide',
      rejectForm.value.reason.trim(),
      rejectForm.value.type
    )
    ElMessage.success('驳回成功，已通知卖家')
    rejectDialogVisible.value = false
    fetchProducts()
  } catch {
    ElMessage.error('驳回失败')
  }
}

async function handleModerate(product, action) {
  const labels = { approve: '审核通过', hide: '驳回' }
  const actionLabel = labels[action] || action

  try {
    if (action === 'hide') {
      // 驳回使用弹窗
      openRejectDialog(product)
    } else {
      // 通过直接确认
      await ElMessageBox.confirm(
        `确定要${actionLabel}商品「${product.title}」吗？`,
        actionLabel,
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await moderateProduct(product.id, action)
      ElMessage.success(`${actionLabel}成功`)
      fetchProducts()
    }
  } catch {
    // 取消操作
  }
}

function onPageChange(page) {
  pagination.value.page = page
  fetchProducts()
}

onMounted(fetchProducts)
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <el-button class="back-btn" text @click="$router.push('/admin')">
        <el-icon><ArrowLeft /></el-icon>
        返回管理后台
      </el-button>
      <h1 class="page-title">商品审核</h1>
    </div>

    <el-card class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="filters.search"
          placeholder="搜索商品标题..."
          clearable
          @clear="fetchProducts"
          @keyup.enter="fetchProducts"
          style="width: 280px"
        />
        <el-select v-model="filters.status" @change="fetchProducts" style="width: 140px">
          <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-button type="primary" @click="fetchProducts">查询</el-button>
      </div>
    </el-card>

    <el-card>
      <el-table v-loading="loading" :data="products" stripe>
        <el-table-column label="商品" min-width="250">
          <template #default="{ row }">
            <div class="product-cell">
              <el-image
                v-if="row.image"
                :src="row.image"
                fit="cover"
                style="width: 56px; height: 56px; border-radius: 8px; flex-shrink: 0"
              />
              <div v-else class="img-placeholder" />
              <div class="product-info">
                <div class="product-title">{{ row.title }}</div>
                <div class="product-meta">
                  <span class="price">¥{{ row.price }}</span>
                  <span v-if="row.category">· {{ row.category.name }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="卖家" width="140">
          <template #default="{ row }">
            {{ row.seller?.nickname || row.seller?.username }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="statusTagMap[row.status]?.type || ''"
              size="small"
            >
              {{ statusTagMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="浏览" width="70" align="center">
          <template #default="{ row }">
            {{ row.view_count }}
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              :icon="Check"
              @click="handleModerate(row, 'approve')"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              size="small"
              plain
              @click="handleModerate(row, 'hide')"
            >
              驳回
            </el-button>
            <el-button
              v-if="row.status === 'active'"
              type="warning"
              size="small"
              :icon="Hide"
              @click="handleModerate(row, 'hide')"
            >
              下架
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

    <!-- 驳回商品弹窗 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="驳回商品"
      width="450px"
    >
      <p style="margin-bottom: 16px;">确定要驳回商品「{{ rejectForm.productTitle }}」吗？</p>
      <el-form label-position="top">
        <el-form-item label="驳回类型：" required>
          <el-select v-model="rejectForm.type" style="width: 100%;">
            <el-option
              v-for="item in rejectTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="详细说明（可选）：">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="3"
            placeholder="补充说明驳回原因（选填）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="submitReject">确定驳回</el-button>
      </template>
    </el-dialog>
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

.product-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.img-placeholder {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  background: #f0f0f0;
  flex-shrink: 0;
}

.product-title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.product-meta {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
}

.price {
  color: #e65100;
  font-weight: 500;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
