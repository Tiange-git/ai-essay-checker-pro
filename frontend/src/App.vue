<template>
  <div class="app">
    <header class="header">
      <h1>英语作文批改助手</h1>
    </header>
    <main class="main">
      <EssayChecker />
    </main>
    <footer class="footer">
      <p>© 2026 英语作文批改助手</p>
    </footer>
  </div>
</template>

<script>
import EssayChecker from './components/EssayChecker.vue'

export default {
  name: 'App',
  components: {
    EssayChecker
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: #333;
  background-color: #f5f5f5;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #000;
  color: white;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.header h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.main {
  flex: 1;
  padding: 1rem;
  width: 100%;
}

.footer {
  background-color: #f8f9fa;
  color: #6c757d;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #dee2e6;
  margin-top: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main {
    padding: 0.75rem;
  }
  
  .header h1 {
    font-size: 1.25rem;
  }
}
</style>
