<template>
  <div>
    <h2 class="section-title">Customers</h2>

    <div v-if="message" :class="['alert', message.type === 'success' ? 'alert-success' : 'alert-error']">
      {{ message.text }}
    </div>

    <div class="card">
      <h3>Add New Customer</h3>
      <form @submit.prevent="createCustomer">
        <div class="form-group">
          <label>Name</label>
          <input v-model="newCustomer.name" type="text" required />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="newCustomer.email" type="email" required />
        </div>
        <button type="submit" class="btn btn-primary">Add Customer</button>
      </form>
    </div>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Email</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="customer in customers" :key="customer.id">
          <td>{{ customer.id }}</td>
          <td>{{ customer.name }}</td>
          <td>{{ customer.email }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../api'

export default {
  name: 'CustomersView',
  setup() {
    const customers = ref([])
    const newCustomer = ref({
      name: '',
      email: ''
    })
    const message = ref(null)

    const loadCustomers = async () => {
      try {
        const response = await api.getCustomers()
        customers.value = response.data
      } catch (error) {
        message.value = { type: 'error', text: 'Failed to load customers' }
      }
    }

    const createCustomer = async () => {
      try {
        await api.createCustomer(newCustomer.value)
        message.value = { type: 'success', text: 'Customer created successfully' }
        newCustomer.value = { name: '', email: '' }
        loadCustomers()
        setTimeout(() => { message.value = null }, 3000)
      } catch (error) {
        message.value = { type: 'error', text: error.response?.data?.detail || 'Failed to create customer' }
      }
    }

    onMounted(() => {
      loadCustomers()
    })

    return {
      customers,
      newCustomer,
      message,
      createCustomer
    }
  }
}
</script>
