<template>
  <div id="app">
    <nav class="main-nav">
      <div class="nav-container">
        <router-link to="/" class="nav-logo">
          <span>ディニー</span>
        </router-link>
        <div class="nav-links">
          <router-link to="/daily_order_summaries">日次注文サマリー</router-link>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style>
:root {
  --primary-color: #4361ee;
  --secondary-color: #3f37c9;
  --light-color: #f8f9fa;
  --dark-color: #212529;
  --success-color: #4cc9f0;
}

#app {
  font-family: 'Noto Sans JP', Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--dark-color);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-nav {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo span {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--dark-color);
  text-decoration: none;
  padding: 0.5rem 0;
  position: relative;
  transition: color 0.3s ease;
}

.nav-links a:hover {
  color: var(--primary-color);
}

.nav-links a.router-link-exact-active {
  color: var(--primary-color);
  font-weight: 600;
}

.nav-links a.router-link-exact-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: var(--primary-color);
  border-radius: 3px 3px 0 0;
}

.main-content {
  flex: 1;
  padding: 2rem;
  background-color: var(--light-color);
}
</style>
