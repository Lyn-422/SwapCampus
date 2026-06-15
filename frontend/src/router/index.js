import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/views/HomeView.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/search',
    component: () => import('@/views/SearchView.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/product/:id',
    component: () => import('@/views/ProductDetail.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/product/:id/edit',
    component: () => import('@/views/EditProductView.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/publish',
    component: () => import('@/views/PublishView.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/chat',
    component: () => import('@/views/ChatList.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/chat/:id',
    component: () => import('@/views/ChatView.vue'),
    meta: { layout: 'chat', requiresAuth: true },
  },
  {
    path: '/profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/profile/:id',
    component: () => import('@/views/ProfileView.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/my-products',
    component: () => import('@/views/MyProducts.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/my-orders',
    component: () => import('@/views/MyOrders.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/favorites',
    component: () => import('@/views/FavoritesView.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/notifications',
    component: () => import('@/views/NotificationsView.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/admin',
    component: () => import('@/views/AdminDashboard.vue'),
    meta: { layout: 'default', requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/admin/products',
    component: () => import('@/views/AdminProducts.vue'),
    meta: { layout: 'default', requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/admin/reports',
    component: () => import('@/views/AdminReports.vue'),
    meta: { layout: 'default', requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/admin/orders',
    component: () => import('@/views/AdminOrders.vue'),
    meta: { layout: 'default', requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/admin/users',
    component: () => import('@/views/AdminUsers.vue'),
    meta: { layout: 'default', requiresAuth: true, requiresStaff: true },
  },
  {
    path: '/login',
    component: () => import('@/views/LoginView.vue'),
    meta: { layout: 'blank', guest: true },
  },
  {
    path: '/register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { layout: 'blank', guest: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.guest && auth.isLoggedIn) {
    next('/')
    return
  }

  if (to.meta.requiresStaff && !auth.isAdmin) {
    next('/')
    return
  }

  next()
})

export default router
