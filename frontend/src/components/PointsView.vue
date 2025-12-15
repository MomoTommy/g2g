<template>
  <div>
    <h2 class="section-title">Reward Points</h2>

    <div class="form-group">
      <label>Select Customer</label>
      <select v-model="selectedCustomerId" @change="loadPointsData">
        <option value="">Select Customer</option>
        <option v-for="customer in customers" :key="customer.id" :value="customer.id">
          {{ customer.name }} ({{ customer.email }})
        </option>
      </select>
    </div>

    <div v-if="selectedCustomerId && pointsBalance" class="grid">
      <div class="card">
        <h3>Available Balance</h3>
        <p style="font-size: 32px; font-weight: bold; color: #27ae60;">
          {{ pointsBalance.available_balance }} pts
        </p>
        <p style="color: #7f8c8d;">
          = ${{ (pointsBalance.available_balance * 0.01).toFixed(2) }} USD
        </p>
      </div>

      <div class="card">
        <h3>Total Earned</h3>
        <p style="font-size: 32px; font-weight: bold; color: #3498db;">
          {{ pointsBalance.total_credits }} pts
        </p>
      </div>

      <div class="card">
        <h3>Total Redeemed</h3>
        <p style="font-size: 32px; font-weight: bold; color: #e74c3c;">
          {{ pointsBalance.total_debits }} pts
        </p>
      </div>
    </div>

    <div v-if="selectedCustomerId">
      <h3>Transaction History</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Points</th>
            <th>Description</th>
            <th>Expiry Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="point in pointsHistory" :key="point.id">
            <td>{{ formatDate(point.created_at) }}</td>
            <td>
              <span :class="['status-badge', point.transaction_type === 'Credit' ? 'status-delivered' : 'status-cancelled']">
                {{ point.transaction_type }}
              </span>
            </td>
            <td :style="{ color: point.transaction_type === 'Credit' ? '#27ae60' : '#e74c3c' }">
              {{ point.transaction_type === 'Credit' ? '+' : '-' }}{{ point.points }}
            </td>
            <td>{{ point.description || '-' }}</td>
            <td>{{ formatDate(point.expiry_date) }}</td>
            <td>
              <span v-if="point.is_expired" class="status-badge status-cancelled">Expired</span>
              <span v-else-if="isExpiringSoon(point.expiry_date)" class="status-badge status-pending">
                Expiring Soon
              </span>
              <span v-else class="status-badge status-delivered">Active</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../api'

export default {
  name: 'PointsView',
  setup() {
    const customers = ref([])
    const selectedCustomerId = ref('')
    const pointsBalance = ref(null)
    const pointsHistory = ref([])

    const loadCustomers = async () => {
      try {
        const response = await api.getCustomers()
        customers.value = response.data
      } catch (error) {
        console.error('Failed to load customers', error)
      }
    }

    const loadPointsData = async () => {
      if (!selectedCustomerId.value) return

      try {
        const [balanceResponse, historyResponse] = await Promise.all([
          api.getCustomerPoints(selectedCustomerId.value),
          api.getCustomerPointsHistory(selectedCustomerId.value)
        ])

        pointsBalance.value = balanceResponse.data
        pointsHistory.value = historyResponse.data
      } catch (error) {
        console.error('Failed to load points data', error)
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const isExpiringSoon = (expiryDate) => {
      const expiry = new Date(expiryDate)
      const today = new Date()
      const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
      return daysUntilExpiry <= 30 && daysUntilExpiry > 0
    }

    onMounted(() => {
      loadCustomers()
    })

    return {
      customers,
      selectedCustomerId,
      pointsBalance,
      pointsHistory,
      loadPointsData,
      formatDate,
      isExpiringSoon
    }
  }
}
</script>
