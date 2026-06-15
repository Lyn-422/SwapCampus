<script setup>
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useNotificationsStore } from '@/stores/notifications'
import { ElMessage } from 'element-plus'
import { Search, Bell } from '@element-plus/icons-vue'
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const chat = useChatStore()
const notifStore = useNotificationsStore()
const router = useRouter()
const searchKeyword = ref('')
let pollTimer = null

onMounted(() => {
  if (auth.isLoggedIn) {
    chat.fetchConversations()
    notifStore.fetchUnreadCount()
    pollTimer = setInterval(() => {
      chat.fetchConversations()
      notifStore.fetchUnreadCount()
    }, 30000)
  }
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

function goSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/search', query: { q: searchKeyword.value.trim() } })
  }
}

function logout() {
  auth.logout()
  ElMessage.success('已退出登录')
}
</script>

<template>
  <el-menu
    :default-active="router.currentRoute.value.path"
    mode="horizontal"
    :ellipsis="false"
    class="navbar"
    router
  >
    <div class="navbar-inner">
      <div class="navbar-left">
        <el-tooltip content="回到首页" placement="bottom" :show-after="500">
          <el-menu-item index="/" class="brand">
            <span class="brand-mark">S</span>
            <span class="brand-text">SwapCampus</span>
          </el-menu-item>
        </el-tooltip>
      </div>

      <div class="navbar-center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索校园二手好物..."
          :prefix-icon="Search"
          size="large"
          class="search-input"
          @keyup.enter="goSearch"
          clearable
        />
      </div>

      <div class="navbar-right">
        <template v-if="auth.isLoggedIn">
          <el-menu-item index="/chat">
            <el-icon><component :is="'ChatDotRound'" /></el-icon>
            <span>消息</span>
            <el-badge
              v-if="chat.unreadTotal > 0"
              :value="chat.unreadTotal"
              class="unread-badge"
            />
          </el-menu-item>

          <el-menu-item index="/notifications">
            <el-icon><component :is="Bell" /></el-icon>
            <span>通知</span>
            <el-badge
              v-if="notifStore.unreadCount > 0"
              :value="notifStore.unreadCount"
              class="unread-badge"
            />
          </el-menu-item>

          <el-menu-item index="/publish" class="publish-btn">
            <button class="btn-publish" @click.stop="$router.push('/publish')">
              <el-icon :size="16"><component :is="'Plus'" /></el-icon>
              发布
            </button>
          </el-menu-item>

          <el-sub-menu index="user-menu">
            <template #title>
              <el-avatar
                :size="32"
                :src="auth.user?.avatar"
                class="nav-avatar"
              >
                {{ auth.user?.nickname?.[0] || auth.user?.username?.[0] || 'U' }}
              </el-avatar>
              <span class="nav-nickname">{{ auth.user?.nickname || auth.user?.username }}</span>
            </template>
            <el-menu-item index="/profile">个人主页</el-menu-item>
            <el-menu-item index="/my-products">我的商品</el-menu-item>
            <el-menu-item index="/my-orders">我的订单</el-menu-item>
            <el-menu-item index="/favorites">我的收藏</el-menu-item>
            <el-divider v-if="auth.isAdmin" style="margin: 4px 0" />
            <el-menu-item v-if="auth.isAdmin" index="/admin">
              <el-icon><component :is="'Setting'" /></el-icon>
              管理后台
            </el-menu-item>
            <el-menu-item @click="logout">退出登录</el-menu-item>
          </el-sub-menu>
        </template>

        <template v-else>
          <div class="nav-auth-buttons">
            <button class="btn-login" @click="$router.push('/login')">登录</button>
            <button class="btn-register" @click="$router.push('/register')">注册</button>
          </div>
        </template>
      </div>
    </div>
  </el-menu>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.94) !important;
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.navbar :deep(.el-menu--horizontal) {
  background: transparent !important;
  border-bottom: none !important;
}

.navbar :deep(.el-sub-menu__title) {
  color: #cbd5e1 !important;
  border-bottom: none !important;
}

.navbar :deep(.el-sub-menu__title:hover) {
  color: #f1f5f9 !important;
  background: rgba(255, 255, 255, 0.06) !important;
}

.navbar :deep(.el-sub-menu__icon-arrow) {
  color: #64748b !important;
}

.navbar-inner {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 0 20px;
  height: 60px;
}

.navbar-left {
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: none !important;
  color: #fff !important;
  padding: 0 12px;
}

.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-text {
  font-size: 19px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.03em;
}

.navbar :deep(.el-menu-item.is-active) {
  background: transparent !important;
  color: #fff !important;
  position: relative;
}

.navbar :deep(.el-menu-item.is-active::after) {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 2px;
  background: #818cf8;
  border-radius: 1px;
}

.navbar-center {
  flex: 1;
  max-width: 440px;
  margin: 0 32px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: none;
  transition: all 0.2s;
}

.search-input :deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.12);
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.search-input :deep(.el-input__inner) {
  color: #e2e8f0;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: #475569;
}

.search-input :deep(.el-input__prefix) {
  color: #64748b;
}

.navbar-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0;
}

.navbar-right :deep(.el-menu-item) {
  border-bottom: none !important;
  color: #94a3b8 !important;
  font-weight: 500;
  transition: color 0.15s;
}

.navbar-right :deep(.el-menu-item:hover) {
  color: #f1f5f9 !important;
  background: rgba(255, 255, 255, 0.05) !important;
}

.publish-btn {
  border-bottom: none !important;
}

.btn-publish {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 18px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-publish:hover {
  background: #4f46e5;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.nav-avatar {
  margin-right: 6px;
}

.nav-nickname {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #cbd5e1;
  font-size: 14px;
}

.nav-auth-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-login {
  padding: 8px 18px;
  background: transparent;
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-login:hover {
  color: #f1f5f9;
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.05);
}

.btn-register {
  padding: 8px 18px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-register:hover {
  background: #4f46e5;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.unread-badge {
  margin-left: 4px;
}

@media (max-width: 768px) {
  .navbar-center {
    display: none;
  }

  .nav-nickname {
    display: none;
  }
}
</style>
