import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // Customers
  getCustomers() {
    return api.get('/customers')
  },
  getCustomer(id) {
    return api.get(`/customers/${id}`)
  },
  createCustomer(data) {
    return api.post('/customers', data)
  },

  // Orders
  getOrders(customerId = null) {
    const params = customerId ? { customer_id: customerId } : {}
    return api.get('/orders', { params })
  },
  getOrder(id) {
    return api.get(`/orders/${id}`)
  },
  createOrder(data) {
    return api.post('/orders', data)
  },
  updateOrderStatus(id, status) {
    return api.patch(`/orders/${id}/status`, { status })
  },

  // Reward Points
  getCustomerPoints(customerId) {
    return api.get(`/customers/${customerId}/points`)
  },
  getCustomerPointsHistory(customerId) {
    return api.get(`/customers/${customerId}/points/history`)
  },

  // Exchange Rates
  getExchangeRates() {
    return api.get('/exchange-rates')
  }
}
