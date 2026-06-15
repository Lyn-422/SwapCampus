<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { usernameRule, passwordRule } from '@/utils/validators'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    const errorData = err?.response?.data?.error
    const code = errorData?.code
    if (code === 'ACCOUNT_PENDING') {
      ElMessageBox.alert(
        '您的账号正在审核中，请耐心等待管理员审核。',
        '账号审核中',
        { confirmButtonText: '知道了', type: 'warning', center: true },
      )
    } else if (code === 'ACCOUNT_REJECTED') {
      ElMessageBox.alert(
        errorData?.message || '您的注册申请已被拒绝',
        '注册被拒绝',
        { confirmButtonText: '知道了', type: 'error', center: true },
      )
    } else if (code === 'ACCOUNT_DISABLED') {
      ElMessageBox.alert(
        '您的账号已被管理员封禁，如有疑问请联系管理员申诉。',
        '账号已封禁',
        { confirmButtonText: '知道了', type: 'warning', center: true },
      )
    } else {
      ElMessage.error(errorData?.message || '学号或密码错误')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-icon">S</span>
        <h1>欢迎回来</h1>
        <p>登录 SwapCampus，继续你的校园交易</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="{ username: [usernameRule], password: [passwordRule] }"
        label-position="top"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="学号" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入学号"
            :prefix-icon="User"
            maxlength="30"
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            :loading="loading"
            @click="handleLogin"
            class="auth-submit-btn"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #f8fafc 70%, #eef2ff 100%);
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 44px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.auth-header {
  text-align: center;
  margin-bottom: 36px;
}

.auth-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 24px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25);
}

.auth-header h1 {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 16px 0 6px;
  letter-spacing: -0.02em;
}

.auth-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

.auth-submit-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-radius: 12px;
  background: #6366f1;
  border: none;
  color: #fff;
}

.auth-submit-btn:hover {
  background: #4f46e5;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
}

.auth-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.auth-footer a {
  color: #6366f1;
  font-weight: 600;
}

.auth-footer a:hover {
  color: #4f46e5;
}
</style>
