<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProductsStore } from '@/stores/products'
import ProductCard from '@/components/product/ProductCard.vue'

const auth = useAuthStore()
const productsStore = useProductsStore()
const currentPage = ref(1)
const pageSize = 20
const productsRef = ref(null)

const carouselSlides = [
  { src: '/carousel/472bf1070660183e5bc06a46de7a1df4.jpg', alt: '校园风景 1' },
  { src: '/carousel/98c8b67e6d67ff246ee36050330837a0.jpg', alt: '校园风景 2' },
  { src: '/carousel/9e4433ded35df41857ec545286d22f6d.jpg', alt: '校园风景 3' },
  { src: '/carousel/f0e7b221e5ca73befa72315b4ddcaff5.jpg', alt: '校园风景 4' },
]

const currentSlide = ref(0)
let carouselTimer = null

const slideStyle = computed(() => ({
  transform: `translateX(-${currentSlide.value * 100}%)`,
}))

function nextSlide() {
  currentSlide.value = (currentSlide.value + 1) % carouselSlides.length
}

function prevSlide() {
  currentSlide.value = (currentSlide.value - 1 + carouselSlides.length) % carouselSlides.length
}

function goSlide(index) {
  currentSlide.value = index
}

function startCarousel() {
  carouselTimer = setInterval(nextSlide, 4000)
}

function stopCarousel() {
  if (carouselTimer) {
    clearInterval(carouselTimer)
    carouselTimer = null
  }
}

async function loadProducts() {
  await productsStore.fetchProducts({
    page: currentPage.value,
    page_size: pageSize,
    status: 'active',
  })
}

function handlePageChange(page) {
  currentPage.value = page
  loadProducts()
  productsRef.value?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(async () => {
  startCarousel()
  await Promise.all([
    loadProducts(),
    productsStore.fetchCategories(),
  ])
})

onUnmounted(() => {
  stopCarousel()
})
</script>

<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-blob hero-blob--1"></div>
        <div class="hero-blob hero-blob--2"></div>
        <div class="hero-blob hero-blob--3"></div>
      </div>
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          Beijing Forestry University
        </div>
        <h1 class="hero-title">
          闲置有<span class="highlight">新</span>生，<br/>校园有<span class="highlight">信</span>任
        </h1>
        <p class="hero-desc">
          北京林业大学专属 C2C 二手交易平台。学号实名认证与面交担保机制，让校园闲置流转更安全、更放心。
        </p>
        <div class="hero-actions">
          <template v-if="auth.isLoggedIn">
            <button class="btn-primary" @click="$router.push('/publish')">
              发布商品
              <span class="btn-arrow">-></span>
            </button>
            <button class="btn-ghost" @click="productsRef?.scrollIntoView({ behavior: 'smooth' })">
              浏览商品
            </button>
          </template>
          <template v-else>
            <button class="btn-primary" @click="$router.push('/register')">
              立即注册
              <span class="btn-arrow">-></span>
            </button>
            <button class="btn-ghost" @click="productsRef?.scrollIntoView({ behavior: 'smooth' })">
              先看看
            </button>
          </template>
        </div>
        <div class="hero-stats">
          <div class="hero-stat">
            <span class="stat-number">{{ productsStore.total || 0 }}</span>
            <span class="stat-label">在售好物</span>
          </div>
          <div class="stat-divider"></div>
          <div class="hero-stat">
            <span class="stat-number">100%</span>
            <span class="stat-label">实名认证</span>
          </div>
          <div class="stat-divider"></div>
          <div class="hero-stat">
            <span class="stat-number">面交</span>
            <span class="stat-label">安全模式</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Carousel -->
    <section class="carousel-section">
      <div class="carousel-wrap" @mouseenter="stopCarousel" @mouseleave="startCarousel">
        <div class="carousel-track" :style="slideStyle">
          <div
            v-for="(slide, i) in carouselSlides"
            :key="i"
            class="carousel-slide"
          >
            <img :src="slide.src" :alt="slide.alt" class="carousel-img" />
          </div>
        </div>

        <button class="carousel-arrow carousel-arrow--left" @click="prevSlide">
          <el-icon :size="20"><component :is="'ArrowLeft'" /></el-icon>
        </button>
        <button class="carousel-arrow carousel-arrow--right" @click="nextSlide">
          <el-icon :size="20"><component :is="'ArrowRight'" /></el-icon>
        </button>

        <div class="carousel-dots">
          <button
            v-for="(_, i) in carouselSlides"
            :key="i"
            class="carousel-dot"
            :class="{ 'is-active': i === currentSlide }"
            @click="goSlide(i)"
          />
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section v-if="productsStore.categories.length > 0" class="section">
      <div class="section-header">
        <h2 class="section-title">浏览分类</h2>
      </div>
      <div class="category-scroll">
        <button
          v-for="cat in productsStore.categories"
          :key="cat.id"
          class="category-chip"
          @click="$router.push({ path: '/search', query: { category: cat.id } })"
        >
          <span class="chip-icon">
            <el-icon :size="16"><component :is="'Folder'" /></el-icon>
          </span>
          {{ cat.name }}
        </button>
      </div>
    </section>

    <!-- Product Grid -->
    <section ref="productsRef" class="section">
      <div class="section-header">
        <h2 class="section-title">最新发布</h2>
        <span class="section-sub">发现校园好物</span>
      </div>

      <div v-if="productsStore.loading" class="loading-grid">
        <div v-for="n in 6" :key="n" class="skeleton-card">
          <div class="skeleton-img"></div>
          <div class="skeleton-body">
            <div class="skeleton-line w-3/4"></div>
            <div class="skeleton-line w-1/2"></div>
            <div class="skeleton-line w-1/3"></div>
          </div>
        </div>
      </div>

      <div v-else-if="productsStore.products.length > 0">
        <div class="card-grid">
          <ProductCard
            v-for="product in productsStore.products"
            :key="product.id"
            :product="product"
          />
        </div>

        <div class="pagination-wrap" v-if="productsStore.total > pageSize">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="productsStore.total"
            layout="prev, pager, next"
            background
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <div v-else class="empty-state">
        <el-icon :size="48" color="#cbd5e1"><component :is="'Shop'" /></el-icon>
        <p>还没有人在售商品，来做第一个吧</p>
        <el-button type="primary" @click="$router.push('/publish')">
          发布商品
        </el-button>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ===== Hero ===== */
.hero {
  position: relative;
  padding: 72px 0 64px;
  overflow: hidden;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 40%, #f8fafc 100%);
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.hero-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.hero-blob--1 {
  width: 500px;
  height: 500px;
  top: -200px;
  right: -100px;
  background: radial-gradient(circle, #6366f1, #8b5cf6);
}

.hero-blob--2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -80px;
  background: radial-gradient(circle, #f43f5e, #ec4899);
}

.hero-blob--3 {
  width: 300px;
  height: 300px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, #3b82f6, #6366f1);
  opacity: 0.15;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 700px;
  margin: 0 auto;
  text-align: center;
  padding: 0 20px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 20px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.25);
  color: #a5b4fc;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 28px;
  letter-spacing: 0.02em;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #818cf8;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.hero-title {
  font-size: 52px;
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.03em;
  color: #f1f5f9;
  margin-bottom: 20px;
}

.highlight {
  background: linear-gradient(135deg, #818cf8, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 17px;
  line-height: 1.7;
  color: #94a3b8;
  max-width: 520px;
  margin: 0 auto 36px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 48px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  letter-spacing: -0.01em;
}

.btn-primary:hover {
  background: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4);
}

.btn-arrow {
  font-size: 14px;
  transition: transform 0.2s;
}

.btn-primary:hover .btn-arrow {
  transform: translateX(3px);
}

.btn-ghost {
  padding: 12px 28px;
  background: transparent;
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-ghost:hover {
  color: #f1f5f9;
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.05);
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
}

.hero-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-number {
  font-size: 22px;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
}

/* ===== Carousel ===== */
.carousel-section {
  max-width: 1200px;
  margin: -16px auto 48px;
  padding: 0 20px;
}

.carousel-wrap {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-xl);
  aspect-ratio: 16 / 9;
  background: #1e293b;
  box-shadow: var(--shadow-lg);
}

.carousel-track {
  display: flex;
  height: 100%;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-slide {
  min-width: 100%;
  height: 100%;
}

.carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0;
}

.carousel-wrap:hover .carousel-arrow {
  opacity: 1;
}

.carousel-arrow:hover {
  background: rgba(255, 255, 255, 0.25);
}

.carousel-arrow--left {
  left: 12px;
}

.carousel-arrow--right {
  right: 12px;
}

.carousel-dots {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.carousel-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.25s;
  padding: 0;
}

.carousel-dot.is-active {
  background: #fff;
  width: 24px;
  border-radius: 4px;
}

/* ===== Sections ===== */
.section {
  max-width: 1200px;
  margin: 0 auto 48px;
  padding: 0 20px;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 18px;
}

.section-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.section-sub {
  font-size: 14px;
  color: var(--text-secondary);
}

/* ===== Category chips ===== */
.category-scroll {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-regular);
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.category-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-light);
  transform: translateY(-1px);
}

.chip-icon {
  color: var(--color-primary);
  opacity: 0.7;
}

/* ===== Loading skeletons ===== */
.loading-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.skeleton-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.skeleton-img {
  width: 100%;
  height: 180px;
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line {
  height: 12px;
  border-radius: 4px;
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

.w-3\/4 { width: 75%; }
.w-1\/2 { width: 50%; }
.w-1\/3 { width: 33%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ===== Pagination ===== */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 36px;
}
</style>
