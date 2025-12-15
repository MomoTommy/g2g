<template>
  <div>
    <h2 class="section-title">Orders</h2>

    <div v-if="message" :class="['alert', message.type === 'success' ? 'alert-success' : 'alert-error']">
      {{ message.text }}
    </div>

    <div class="card">
      <h3>Create New Order</h3>
      <form @submit.prevent="createOrder">
        <div class="form-group">
          <label>Customer</label>
          <select v-model="newOrder.customer_id" required>
            <option value="">Select Customer</option>
            <option v-for="customer in customers" :key="customer.id" :value="customer.id">
              {{ customer.name }} ({{ customer.email }})
            </option>
          </select>
        </div>
        <div class="grid">
          <div class="form-group">
            <label>Amount</label>
            <input v-model.number="newOrder.total_amount" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Currency</label>
            <select v-model="newOrder.currency" required>
              <option value="MYR">MYR</option>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="JPY">JPY</option>
              <option value="CNY">CNY</option>
              <option value="SGD">SGD</option>
            </select>
          </div>
        </div>
        <div class="form-group" v-if="newOrder.customer_id">
          <label>Use Points (Available: {{ customerPoints }})</label>
          <input v-model.number="newOrder.points_to_use" type="number" step="0.01" min="0" :max="customerPoints" />
          <small v-if="newOrder.points_to_use > 0">
            Discount: ${{ (newOrder.points_to_use * 0.01).toFixed(2) }} USD
          </small>
        </div>
        <button type="submit" class="btn btn-primary">Create Order</button>
      </form>
    </div>

    <h3>All Orders</h3>
    <table>
      <thead>
        <tr>
          <th>Order #</th>
          <th>Customer</th>
          <th>Amount</th>
          <th>Currency</th>
          <th>Status</th>
          <th>Order Date</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in orders" :key="order.id">
          <td>{{ order.order_number }}</td>
          <td>{{ getCustomerName(order.customer_id) }}</td>
          <td>{{ order.total_amount }}</td>
          <td>{{ order.currency }}</td>
          <td>
            <span :class="['status-badge', `status-${order.status.toLowerCase()}`]">
              {{ order.status }}
            </span>
          </td>
          <td>{{ formatDate(order.order_date) }}</td>
          <td>
            <select
              @change="updateStatus(order.id, $event.target.value)"
              :value="order.status"
              class="btn btn-secondary"
            >
              <option value="Active">Active</option>
              <option value="Delivered">Delivered</option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import api from '../api'

export default {
  name: 'OrdersView',
  setup() {
    const orders = ref([])
    const customers = ref([])
    const customerPoints = ref(0)
    const newOrder = ref({
      customer_id: '',
      total_amount: 0,
      currency: 'MYR',
      points_to_use: 0
    })
    const message = ref(null)

    const loadOrders = async () => {
      try {
        const response = await api.getOrders()
        orders.value = response.data
      } catch (error) {
        message.value = { type: 'error', text: 'Failed to load orders' }
      }
    }

    const loadCustomers = async () => {
      try {
        const response = await api.getCustomers()
        customers.value = response.data
      } catch (error) {
        console.error('Failed to load customers', error)
      }
    }

    const loadCustomerPoints = async (customerId) => {
      if (!customerId) {
        customerPoints.value = 0
        return
      }
      try {
        const response = await api.getCustomerPoints(customerId)
        customerPoints.value = response.data.available_balance
      } catch (error) {
        customerPoints.value = 0
      }
    }

    const createOrder = async () => {
      try {
        await api.createOrder(newOrder.value)
        message.value = { type: 'success', text: 'Order created successfully' }
        newOrder.value = { customer_id: '', total_amount: 0, currency: 'MYR', points_to_use: 0 }
        loadOrders()
        setTimeout(() => { message.value = null }, 3000)
      } catch (error) {
        message.value = { type: 'error', text: error.response?.data?.detail || 'Failed to create order' }
      }
    }

    const updateStatus = async (orderId, newStatus) => {
      try {
        await api.updateOrderStatus(orderId, newStatus)
        message.value = { type: 'success', text: 'Order status updated. Points credited if delivered.' }
        loadOrders()
        setTimeout(() => { message.value = null }, 3000)
      } catch (error) {
        message.value = { type: 'error', text: 'Failed to update order status' }
      }
    }

    const getCustomerName = (customerId) => {
      const customer = customers.value.find(c => c.id === customerId)
      return customer ? customer.name : 'Unknown'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    watch(() => newOrder.value.customer_id, (customerId) => {
      loadCustomerPoints(customerId)
    })

    onMounted(() => {
      loadOrders()
      loadCustomers()
    })

    return {
      orders,
      customers,
      customerPoints,
      newOrder,
      message,
      createOrder,
      updateStatus,
      getCustomerName,
      formatDate
    }
  }
}
</script>
