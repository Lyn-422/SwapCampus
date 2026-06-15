<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="footer-mark">S</span>
        <span class="footer-title">SwapCampus</span>
        <span class="footer-desc">北京林业大学 · 校园闲置物品交易平台</span>
      </div>
      <div class="footer-right">
        <span>让闲置流转，让信任传递</span>
        <span class="footer-divider">|</span>
        <span>软件工程 T-02</span>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {{ new Date().getFullYear() }} SwapCampus Team</span>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  margin-top: 60px;
  background: #1e293b;
  color: #94a3b8;
  font-size: 13px;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 28px 20px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.footer-mark {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-title {
  font-weight: 700;
  color: #e2e8f0;
  font-size: 15px;
  letter-spacing: -0.02em;
}

.footer-desc {
  color: #64748b;
}

.footer-right {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #64748b;
}

.footer-divider {
  color: #334155;
}

.footer-bottom {
  text-align: center;
  padding: 14px 20px;
  border-top: 1px solid #1e293b;
  color: #475569;
  font-size: 12px;
}

@media (max-width: 640px) {
  .footer-inner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
