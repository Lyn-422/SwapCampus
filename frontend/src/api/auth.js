import client from './client'

export function register(formData) {
  return client.post('/users/register/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function login(data) {
  return client.post('/users/login/', data)
}

export function refreshToken(refresh) {
  return client.post('/users/token/refresh/', { refresh })
}
