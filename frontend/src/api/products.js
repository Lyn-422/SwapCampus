import client from './client'

export function getProducts(params) {
  return client.get('/products/', { params })
}

export function getProduct(id) {
  return client.get(`/products/${id}/`)
}

export function createProduct(data) {
  return client.post('/products/', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function updateProduct(id, data) {
  return client.patch(`/products/${id}/`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getCategories() {
  return client.get('/products/categories/')
}

export function getTags() {
  return client.get('/products/tags/')
}

export function getMyProducts() {
  return client.get('/products/my/')
}

export function getUserProducts(userId) {
  return client.get('/products/', { params: { seller: userId, status: 'active' } })
}

export function getRelatedProducts(id) {
  return client.get(`/products/${id}/related/`)
}

export function markActive(id) {
  return client.post(`/products/${id}/mark_active/`)
}

export function deleteProduct(id) {
  return client.delete(`/products/${id}/`)
}

// 评论相关
export function getComments(productId) {
  return client.get('/products/comments/', { params: { product_id: productId } })
}

export function createComment(data) {
  const formData = new FormData()
  formData.append('product_id', data.productId)
  formData.append('content', data.content)
  if (data.parentId) {
    formData.append('parent_id', data.parentId)
  }
  if (data.image) {
    formData.append('image', data.image)
  }
  return client.post('/products/comments/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteComment(commentId) {
  return client.delete(`/products/comments/${commentId}/`)
}
