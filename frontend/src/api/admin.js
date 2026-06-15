import client from './client'

// 数据看板
export function getDashboard() {
  return client.get('/admin/dashboard/')
}

// 商品审核
export function getAdminProducts(params = {}) {
  return client.get('/admin/products/', { params })
}

export function moderateProduct(id, action, reason = '', rejectType = 'other') {
  return client.post(`/admin/products/${id}/moderate/?action=${action}`, {
    reason,
    reject_type: rejectType,
  })
}

// 举报管理
export function getAdminReports(params = {}) {
  return client.get('/admin/reports/', { params })
}

export function handleReport(id, data) {
  return client.post(`/admin/reports/${id}/handle/`, data)
}

// 用户管理
export function getAdminUsers(params = {}) {
  return client.get('/admin/users/', { params })
}

export function banUser(id, isActive) {
  return client.post(`/admin/users/${id}/ban/`, { is_active: isActive })
}
