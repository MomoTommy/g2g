<template>
  <div id="app">
    <header>
      <h1>G2G Technical Assessment</h1>
      <nav>
        <button @click="currentView = 'customers'" :class="{ active: currentView === 'customers' }">
          Customers
        </button>
        <button @click="currentView = 'orders'" :class="{ active: currentView === 'orders' }">
          Orders
        </button>
        <button @click="currentView = 'points'" :class="{ active: currentView === 'points' }">
          Points
        </button>
      </nav>
    </header>

    <main>
      <CustomersView v-if="currentView === 'customers'" />
      <OrdersView v-if="currentView === 'orders'" />
      <PointsView v-if="currentView === 'points'" />
    </main>
  </div>
</template>

<script>
import { ref } from 'vue'
import CustomersView from './components/CustomersView.vue'
import OrdersView from './components/OrdersView.vue'
import PointsView from './components/PointsView.vue'

export default {
  name: 'App',
  components: {
    CustomersView,
    OrdersView,
    PointsView
  },
  setup() {
    const currentView = ref('orders')

    return {
      currentView
    }
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f5f5f5;
  color: #333;
}

#app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

header h1 {
  margin-bottom: 15px;
  color: #2c3e50;
}

nav {
  display: flex;
  gap: 10px;
}

nav button {
  padding: 10px 20px;
  border: none;
  background: #f0f0f0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

nav button:hover {
  background: #e0e0e0;
}

nav button.active {
  background: #3498db;
  color: white;
}

main {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover {
  background: #229954;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

table th,
table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

table tr:hover {
  background: #f8f9fa;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background: #cce5ff;
  color: #004085;
}

.status-delivered {
  background: #d4edda;
  color: #155724;
}

.alert {
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.alert-success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.card {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}
</style>
