<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { addFavorite, removeFavorite, checkFavorite } from '@/api/favorites'
import { formatPrice, formatTime, conditionLabels, conditionColors } from '@/utils/format'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const router = useRouter()
const auth = useAuthStore()

const isFav = ref(false)
const favId = ref(null)
const favLoading = ref(false)

onMounted(async () => {
  if (!auth.isLoggedIn) return
  try {
    const res = await checkFavorite(props.product.id)
    const data = res.data.data || res.data
    const results = data.results || data
    if (Array.isArray(results) && results.length > 0) {
      isFav.value = true
      favId.value = results[0].id
    }
  } catch {}
})

async function toggleFav() {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  if (favLoading.value) return
  favLoading.value = true
  try {
    if (isFav.value) {
      await removeFavorite(favId.value)
      isFav.value = false
      favId.value = null
    } else {
      const res = await addFavorite(props.product.id)
      const item = res.data.data || res.data
      isFav.value = true
      favId.value = item.id
    }
  } catch {
    // handled by interceptor
  } finally {
    favLoading.value = false
  }
}

function goDetail() {
  router.push(`/product/${props.product.id}`)
}
</script>

<template>
  <article class="card" @click="goDetail">
    <div class="card-img">
      <el-image
        v-if="product.cover_image"
        :src="product.cover_image"
        fit="cover"
        class="card-img-el"
        lazy
      >
        <template #error>
          <div class="card-img-fallback">
            <el-icon :size="32" color="#94a3b8"><component :is="'Picture'" /></el-icon>
          </div>
        </template>
      </el-image>
      <div v-else class="card-img-fallback">
        <el-icon :size="32" color="#94a3b8"><component :is="'Picture'" /></el-icon>
      </div>

      <span v-if="product.condition" class="card-badge" :class="`badge--${product.condition}`">
        {{ conditionLabels[product.condition] || product.condition_display }}
      </span>

      <button
        class="card-fav"
        :class="{ 'is-active': isFav }"
        :disabled="favLoading"
        @click.stop="toggleFav"
      >
        <el-icon :size="14"><component :is="isFav ? 'StarFilled' : 'Star'" /></el-icon>
      </button>

      <div v-if="product.status !== 'active'" class="card-overlay">
        <span class="overlay-tag">
          {{ product.status === 'sold' ? '已售出' : product.status === 'hidden' ? '已下架' : product.status === 'pending' ? '审核中' : product.status === 'banned' ? '违规下架' : '已预定' }}
        </span>
      </div>
    </div>

    <div class="card-body">
      <h3 class="card-title">{{ product.title }}</h3>

      <div class="card-price-row">
        <span class="card-price">{{ formatPrice(product.price) }}</span>
        <span v-if="product.original_price" class="card-original">
          {{ formatPrice(product.original_price) }}
        </span>
      </div>

      <div class="card-footer">
        <div class="card-seller">
          <span class="seller-avatar">{{ product.seller?.nickname?.[0] || '?' }}</span>
          <span class="seller-name">{{ product.seller?.nickname }}</span>
        </div>
        <span class="card-time">{{ formatTime(product.created_at) }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  cursor: pointer;
  border-radius: 14px;
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.04);
  border-color: #d6d3d1;
}

.card:active {
  transform: translateY(-2px);
}

.card-img {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  overflow: hidden;
  background: #f5f5f4;
}

.card-img-el {
  width: 100%;
  height: 100%;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover .card-img-el {
  transform: scale(1.06);
}

.card-img-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f4;
}

.card-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(6px);
  color: var(--text-regular);
}

.badge--new { background: #fef3c7; color: #92400e; }
.badge--like_new { background: #ecfdf5; color: #047857; }
.badge--good { background: #eff6ff; color: #1e40af; }
.badge--fair { background: #fffbeb; color: #b45309; }
.badge--worn { background: #fff1f2; color: #be123c; }

.card-fav {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(6px);
  cursor: pointer;
  color: #a8a29e;
  transition: all 0.2s;
}

.card-fav:hover {
  background: #fff;
  color: #d97706;
  transform: scale(1.1);
}

.card-fav.is-active {
  color: #f59e0b;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.overlay-tag {
  padding: 6px 16px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.card-body {
  padding: 14px 16px 16px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10px;
}

.card-price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 10px;
}

.card-price {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-price);
  letter-spacing: -0.02em;
}

.card-original {
  font-size: 13px;
  color: var(--text-secondary);
  text-decoration: line-through;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-seller {
  display: flex;
  align-items: center;
  gap: 6px;
}

.seller-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d97706, #f59e0b);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.seller-name {
  font-size: 12px;
  color: var(--text-secondary);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-time {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
