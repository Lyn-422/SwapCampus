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
const showMobileMenu = ref(false)
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
  <header class="navbar">
    <div class="navbar-inner">
      <div class="navbar-left">
        <router-link to="/" class="brand">
          <span class="brand-mark">S</span>
          <span class="brand-text">SwapCampus</span>
        </router-link>
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
          <router-link to="/chat" class="nav-link" :class="{ active: $route.path === '/chat' }">
            <el-icon :size="18"><component :is="'ChatDotRound'" /></el-icon>
            <span class="nav-label">消息</span>
            <el-badge
              v-if="chat.unreadTotal > 0"
              :value="chat.unreadTotal"
              class="nav-badge"
            />
          </router-link>

          <router-link to="/notifications" class="nav-link" :class="{ active: $route.path === '/notifications' }">
            <el-icon :size="18"><component :is="Bell" /></el-icon>
            <span class="nav-label">通知</span>
            <el-badge
              v-if="notifStore.unreadCount > 0"
              :value="notifStore.unreadCount"
              class="nav-badge"
            />
          </router-link>

          <router-link to="/publish" class="btn-publish">
            <el-icon :size="16"><component :is="'Plus'" /></el-icon>
            发布
          </router-link>

          <el-dropdown trigger="click" popper-class="user-dropdown">
            <button class="user-trigger">
              <el-avatar
                :size="34"
                :src="auth.user?.avatar"
                class="nav-avatar"
              >
                {{ auth.user?.nickname?.[0] || auth.user?.username?.[0] || 'U' }}
              </el-avatar>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <div class="dropdown-user-info">
                  <span class="dropdown-name">{{ auth.user?.nickname || auth.user?.username }}</span>
                  <span class="dropdown-id">学号 {{ auth.user?.username }}</span>
                </div>
                <el-dropdown-item divided>
                  <router-link to="/profile" class="dropdown-link">个人主页</router-link>
                </el-dropdown-item>
                <el-dropdown-item>
                  <router-link to="/my-products" class="dropdown-link">我的商品</router-link>
                </el-dropdown-item>
                <el-dropdown-item>
                  <router-link to="/my-orders" class="dropdown-link">我的订单</router-link>
                </el-dropdown-item>
                <el-dropdown-item>
                  <router-link to="/favorites" class="dropdown-link">我的收藏</router-link>
                </el-dropdown-item>
                <el-dropdown-item v-if="auth.isAdmin" divided>
                  <router-link to="/admin" class="dropdown-link admin-link">管理后台</router-link>
                </el-dropdown-item>
                <el-dropdown-item divided>
                  <span class="dropdown-link logout-link" @click="logout">退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>

        <template v-else>
          <button class="btn-login" @click="$router.push('/login')">登录</button>
          <button class="btn-register" @click="$router.push('/register')">注册</button>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: #ffffff;
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(12px);
}

.navbar-inner {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 0 20px;
  height: 62px;
}

.navbar-left {
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #d97706, #f59e0b);
  color: #fff;
  font-size: 17px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.25);
}

.brand-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.03em;
}

.navbar-center {
  flex: 1;
  max-width: 420px;
  margin: 0 28px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f5f5f4;
  border: 1px solid transparent;
  box-shadow: none;
  transition: all 0.2s;
}

.search-input :deep(.el-input__wrapper:hover) {
  background: #e7e5e4;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  background: #ffffff;
  border-color: #d97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1);
}

.search-input :deep(.el-input__inner) {
  color: var(--text-primary);
}

.search-input :deep(.el-input__inner::placeholder) {
  color: #a8a29e;
}

.search-input :deep(.el-input__prefix) {
  color: #a8a29e;
}

.navbar-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 14px;
  border-radius: 10px;
  color: var(--text-regular);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  position: relative;
}

.nav-link:hover {
  background: #f5f5f4;
  color: var(--text-primary);
}

.nav-link.active {
  color: #d97706;
  background: #fffbeb;
}

.nav-label {
  display: inline;
}

.nav-badge {
  margin-left: 2px;
}

.nav-badge :deep(.el-badge__content) {
  background: #e11d48;
}

.btn-publish {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: #d97706;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  text-decoration: none;
  margin-left: 6px;
}

.btn-publish:hover {
  background: #b45309;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.3);
  color: #fff;
}

.user-trigger {
  padding: 2px;
  background: none;
  border: 2px solid transparent;
  border-radius: 50%;
  cursor: pointer;
  transition: border-color 0.2s;
  margin-left: 8px;
}

.user-trigger:hover {
  border-color: #d97706;
}

.nav-avatar {
  display: block;
}

.nav-auth-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-login {
  padding: 9px 20px;
  background: transparent;
  color: var(--text-primary);
  border: 1.5px solid var(--border-color);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-login:hover {
  border-color: #d97706;
  color: #d97706;
  background: #fffbeb;
}

.btn-register {
  padding: 9px 22px;
  background: #d97706;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-register:hover {
  background: #b45309;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.3);
}

@media (max-width: 768px) {
  .navbar-center { display: none; }
  .nav-label { display: none; }
}
</style>

<style>
.user-dropdown {
  border-radius: 14px !important;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.06) !important;
  border: 1px solid var(--border-color) !important;
  overflow: hidden;
}

.dropdown-user-info {
  padding: 14px 16px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.dropdown-id {
  font-size: 12px;
  color: var(--text-secondary);
}

.dropdown-link {
  display: block;
  padding: 4px 0;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.dropdown-link:hover {
  color: #d97706;
}

.admin-link {
  color: #d97706;
}

.logout-link {
  color: var(--text-secondary);
  cursor: pointer;
}

.logout-link:hover {
  color: #e11d48;
}
</style>
