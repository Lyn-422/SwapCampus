<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { studentIdRule, passwordRule } from '@/utils/validators'
import ImageUploader from '@/components/common/ImageUploader.vue'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const showPasswordTips = ref(false)
const studentIdCardFile = ref(null)
const studentCardFiles = ref([])

const form = reactive({
  username: '',
  password: '',
  password_confirm: '',
  email: '',
  nickname: '',
  campus: '',
})

const studentCardRule = {
  required: true,
  validator: (rule, value, callback) => {
    if (!studentIdCardFile.value) {
      callback(new Error('请上传学生证照片'))
    } else {
      callback()
    }
  },
  trigger: 'change',
}

function handleStudentCardChange(files) {
  studentCardFiles.value = files
  studentIdCardFile.value = files.length > 0 ? files[0] : null
  if (formRef.value) {
    formRef.value.validateField('student_id_card').catch(() => {})
  }
}

const passwordConfirmRule = {
  required: true,
  validator: (rule, value, callback) => {
    if (value !== form.password) {
      callback(new Error('两次密码输入不一致'))
    } else {
      callback()
    }
  },
  trigger: 'blur',
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await auth.register({ ...form, studentIdCardFile: studentIdCardFile.value })
    ElMessage.success('注册已提交，请等待管理员审核')
    router.push('/login')
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-bg-orb orb-1"></div>
    <div class="auth-bg-orb orb-2"></div>

    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">S</div>
        <h1>加入 SwapCampus</h1>
        <p>北京林业大学校园闲置交易平台</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        label-position="top"
        size="large"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="学号" prop="username" :rules="[studentIdRule]">
          <el-input
            v-model="form.username"
            placeholder="输入学号"
            maxlength="9"
          />
        </el-form-item>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="密码" prop="password" :rules="[passwordRule]">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="至少 8 位"
                show-password
                @focus="showPasswordTips = true"
                @blur="showPasswordTips = false"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确认密码" prop="password_confirm" :rules="[passwordConfirmRule]">
              <el-input
                v-model="form.password_confirm"
                type="password"
                placeholder="再次输入密码"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div v-if="showPasswordTips" class="password-tips">
          <p>密码要求：至少8个字符，不能全为数字，不能过于简单</p>
        </div>

        <el-form-item label="昵称（选填）" prop="nickname">
          <el-input v-model="form.nickname" placeholder="给自己起个名字" maxlength="50" />
        </el-form-item>

        <el-form-item label="校区（选填）" prop="campus">
          <el-select v-model="form.campus" placeholder="选择校区" clearable style="width: 100%">
            <el-option label="校本部" value="校本部" />
            <el-option label="鹫峰校区" value="鹫峰校区" />
          </el-select>
        </el-form-item>

        <el-form-item label="邮箱（选填）" prop="email">
          <el-input v-model="form.email" placeholder="用于找回密码" type="email" />
        </el-form-item>

        <el-form-item label="学生证照片" prop="student_id_card" :rules="[studentCardRule]">
          <ImageUploader
            v-model="studentCardFiles"
            :max="1"
            @update:model-value="handleStudentCardChange"
          />
          <div class="upload-hint">
            请上传清晰的学生证照片用于身份验证，注册后需管理员审核通过方可登录
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleRegister"
            class="auth-submit-btn"
          >
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        已有账号？<router-link to="/login">立即登录</router-link>
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
  background: #fafaf9;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.auth-bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
  pointer-events: none;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: #fde68a;
  top: -120px;
  right: -100px;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: #fecdd3;
  bottom: -80px;
  left: -60px;
}

.auth-card {
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border-radius: 20px;
  padding: 40px 40px 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 8px 32px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}

.auth-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #d97706, #f59e0b);
  color: #fff;
  font-size: 24px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(217, 119, 6, 0.25);
}

.auth-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 14px 0 4px;
  letter-spacing: -0.02em;
}

.auth-header p {
  font-size: 13px;
  color: var(--text-secondary);
}

.auth-submit-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.05em;
  border-radius: 12px;
  margin-top: 4px;
}

.auth-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.auth-footer a {
  color: #d97706;
  font-weight: 600;
}

.auth-footer a:hover {
  color: #b45309;
}

.password-tips {
  padding: 4px 0 8px;
  color: #a8a29e;
  font-size: 12px;
}

.password-tips p {
  margin: 0;
  line-height: 1.5;
}

.upload-hint {
  margin-top: 6px;
  font-size: 12px;
  color: #a8a29e;
  line-height: 1.5;
}
</style>
