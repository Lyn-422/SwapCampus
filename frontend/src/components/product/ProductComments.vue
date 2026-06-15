<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getComments, createComment, deleteComment } from '@/api/products'
import { useAuthStore } from '@/stores/auth'
import { formatTime } from '@/utils/format'

const props = defineProps({
  productId: { type: String, required: true },
  productStatus: { type: String, required: true },
  isSeller: { type: Boolean, default: false },
})

const auth = useAuthStore()
const comments = ref([])
const loading = ref(false)
const newComment = ref('')
const replyTo = ref(null)
const commentImage = ref(null)
const submitLoading = ref(false)

onMounted(() => {
  loadComments()
})

async function loadComments() {
  loading.value = true
  try {
    const res = await getComments(props.productId)
    comments.value = res.data.data || res.data || []
  } catch {
    comments.value = []
  } finally {
    loading.value = false
  }
}

async function submitComment() {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  submitLoading.value = true
  try {
    await createComment({
      productId: props.productId,
      content: newComment.value.trim(),
      parentId: replyTo.value?.id || null,
      image: commentImage.value,
    })
    ElMessage.success(replyTo.value ? '回复成功' : '评论成功')
    newComment.value = ''
    replyTo.value = null
    commentImage.value = null
    loadComments()
  } catch {
    ElMessage.error(replyTo.value ? '回复失败' : '评论失败')
  } finally {
    submitLoading.value = false
  }
}

function startReply(comment) {
  replyTo.value = comment
  newComment.value = ''
}

function cancelReply() {
  replyTo.value = null
  newComment.value = ''
}

async function handleDelete(comment) {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '确认删除', {
      type: 'warning',
    })
    await deleteComment(comment.id)
    ElMessage.success('删除成功')
    loadComments()
  } catch {
    // 取消
  }
}

function handleImageChange(file) {
  commentImage.value = file.raw
}

function canDelete(comment) {
  if (!auth.isLoggedIn) return false
  return comment.author === auth.user?.id || props.isSeller
}
</script>

<template>
  <section class="comments-section">
    <h3 class="comments-title">
      留言讨论
      <span v-if="comments.length > 0" class="comments-count">({{ comments.length }})</span>
    </h3>

    <!-- 评论输入框 -->
    <div v-if="productStatus !== 'sold' && auth.isLoggedIn" class="comment-input-box">
      <div v-if="replyTo" class="reply-hint">
        回复 <span class="reply-name">{{ replyTo.author_name }}</span>
        <el-button link size="small" @click="cancelReply">取消</el-button>
      </div>
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="3"
        :placeholder="replyTo ? '写下你的回复...' : '咨询商品详情，卖家会尽快回复...'"
        maxlength="1000"
        show-word-limit
      />
      <div class="comment-actions">
        <el-upload
          accept="image/*"
          :auto-upload="false"
          :on-change="handleImageChange"
          :show-file-list="false"
          class="image-upload"
        >
          <el-button link>
            <el-icon><Picture /></el-icon>
            {{ commentImage ? '已选图片' : '添加图片' }}
          </el-button>
        </el-upload>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="submitComment"
        >
          {{ replyTo ? '回复' : '发表留言' }}
        </el-button>
      </div>
    </div>

    <!-- 未登录提示 -->
    <div v-else-if="productStatus !== 'sold' && !auth.isLoggedIn" class="login-tip">
      <el-button type="primary" text @click="$router.push('/login')">
        登录后可留言咨询
      </el-button>
    </div>

    <!-- 已售出提示 -->
    <div v-else-if="productStatus === 'sold'" class="sold-tip">
      <el-icon><InfoFilled /></el-icon>
      商品已售出，不再接受新留言
    </div>

    <!-- 评论列表 -->
    <div v-if="comments.length > 0" class="comments-list" v-loading="loading">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-main">
          <el-avatar :size="40" :src="comment.author_avatar">
            {{ comment.author_name?.[0] || '?' }}
          </el-avatar>
          <div class="comment-content">
            <div class="comment-header">
              <span class="author-name">{{ comment.author_name }}</span>
              <el-tag v-if="comment.is_seller" size="small" type="success">卖家</el-tag>
              <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
            </div>
            <p class="comment-text">{{ comment.content }}</p>
            <el-image
              v-if="comment.image"
              :src="comment.image"
              fit="cover"
              class="comment-image"
              :preview-src-list="[comment.image]"
            />
            <div class="comment-footer">
              <el-button
                v-if="productStatus !== 'sold' && auth.isLoggedIn && !replyTo"
                link
                size="small"
                @click="startReply(comment)"
              >
                回复
              </el-button>
              <el-button
                v-if="canDelete(comment)"
                link
                size="small"
                type="danger"
                @click="handleDelete(comment)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <!-- 回复列表 -->
        <div v-if="comment.replies?.length > 0" class="replies-list">
          <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
            <el-avatar :size="32" :src="reply.author_avatar">
              {{ reply.author_name?.[0] || '?' }}
            </el-avatar>
            <div class="reply-content">
              <div class="reply-header">
                <span class="author-name">{{ reply.author_name }}</span>
                <el-tag v-if="reply.is_seller" size="small" type="success">卖家</el-tag>
                <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
              </div>
              <p class="reply-text">{{ reply.content }}</p>
              <el-image
                v-if="reply.image"
                :src="reply.image"
                fit="cover"
                class="reply-image"
                :preview-src-list="[reply.image]"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="comments-empty">
      <el-icon :size="48"><ChatDotSquare /></el-icon>
      <p>暂无留言</p>
      <p v-if="productStatus !== 'sold'" class="empty-tip">
        有任何问题？快来咨询卖家吧
      </p>
    </div>
  </section>
</template>

<style scoped>
.comments-section {
  margin-top: 32px;
}

.comments-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comments-count {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.comment-input-box {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.reply-hint {
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.reply-name {
  color: #6366f1;
  font-weight: 500;
}

.comment-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.image-upload {
  display: inline-block;
}

.login-tip,
.sold-tip {
  text-align: center;
  padding: 24px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
  color: #909399;
}

.sold-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 16px;
}

.comment-main {
  display: flex;
  gap: 12px;
}

.comment-content {
  flex: 1;
}

.comment-header,
.reply-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.author-name {
  font-weight: 500;
  color: #303133;
}

.comment-time,
.reply-time {
  font-size: 12px;
  color: #909399;
}

.comment-text,
.reply-text {
  color: #606266;
  line-height: 1.6;
  margin: 0 0 8px;
  white-space: pre-wrap;
}

.comment-image,
.reply-image {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}

.reply-image {
  width: 100px;
  height: 100px;
}

.comment-footer {
  display: flex;
  gap: 12px;
}

.replies-list {
  margin-left: 52px;
  margin-top: 12px;
  padding-left: 16px;
  border-left: 2px solid #ebeef5;
}

.reply-item {
  display: flex;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-content {
  flex: 1;
}

.comments-empty {
  text-align: center;
  padding: 48px 24px;
  color: #909399;
}

.comments-empty p {
  margin: 8px 0 0;
}

.empty-tip {
  font-size: 13px;
}
</style>
