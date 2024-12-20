<script setup lang="ts">
import { ref, computed } from 'vue'

// Reactive variables for form inputs
const selectedSupplier = ref('')
const suppliers = ['Aromatico', 'Beans Inc.', 'Fair Trade AG', 'Farmers of Brazil', 'Handelskontor Hamburg']

const quantity = ref(0)
const selectedWarehouse = ref('')
const warehouses = [
  'Naples - RR',
  'Amsterdam - RR',
  'London - RR',
  'Hamburg - RR',
  'Barcelona - RR',
  'Nairobi - RR',
  'Istanbul - RR'
]

const selectedItemName = ref('')
const itemNames = ['Excelsa', 'Maragogype', 'Maragogype Type B', 'Robusta', 'Liberica', 'Arabica']

const orderDate = ref('')

// The response from the backend
const prediction = ref('')
const loading = ref(false)

// Backend URL computed from environment variable
const backendUrl = computed(() => import.meta.env.VITE_APP_BACKEND_URL)

// Function to fetch the prediction from the backend
const getPrediction = async () => {
  console.log('Fetching data from backend')

  prediction.value = ''
  loading.value = true

  try {
    const url = `${backendUrl.value}?supplier=${encodeURIComponent(selectedSupplier.value)}&quantity=${quantity.value}&warehouse=${encodeURIComponent(selectedWarehouse.value)}&item_name=${encodeURIComponent(selectedItemName.value)}&schedule_date=${encodeURIComponent(orderDate.value)}`

    console.log(`Request URL: ${url}`)

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.statusText}`)
    }

    const data = await response.json()
    console.log('Response data:', data)

    if (data.prediction) {
      prediction.value = data.prediction.toFixed(2) // Round prediction to 2 decimal places
    } else {
      prediction.value = 'No prediction available'
    }
  } catch (error) {
    console.error('Error fetching data:', error)
    alert('Could not fetch data')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Supplier Dropdown -->
  <div>
    <label for="supplier">Please select a supplier:</label>
    <select id="supplier" v-model="selectedSupplier">
      <option value="" disabled>Select a supplier</option>
      <option v-for="supplier in suppliers" :key="supplier" :value="supplier">{{ supplier }}</option>
    </select>
    <div class="hint">Selected supplier: {{ selectedSupplier }}</div>
  </div>

  <!-- Quantity Input -->
  <div>
    <label for="quantity">Enter Quantity:</label>
    <input id="quantity" type="number" v-model="quantity" min="1" />
    <div class="hint">Selected quantity: {{ quantity }}</div>
  </div>

  <!-- Warehouse Dropdown -->
  <div>
    <label for="warehouse">Please select a warehouse:</label>
    <select id="warehouse" v-model="selectedWarehouse">
      <option value="" disabled>Select a warehouse</option>
      <option v-for="warehouse in warehouses" :key="warehouse" :value="warehouse">{{ warehouse }}</option>
    </select>
    <div class="hint">Selected warehouse: {{ selectedWarehouse }}</div>
  </div>

  <!-- Item Name Dropdown -->
  <div>
    <label for="item_name">Please select an item name:</label>
    <select id="item_name" v-model="selectedItemName">
      <option value="" disabled>Select an item</option>
      <option v-for="item in itemNames" :key="item" :value="item">{{ item }}</option>
    </select>
    <div class="hint">Selected item name: {{ selectedItemName }}</div>
  </div>

  <!-- Order Date Input -->
  <div>
    <label for="order_date">Enter Order Date (YYYY-MM-DD):</label>
    <input id="order_date" type="date" v-model="orderDate" />
    <div class="hint">Selected order date: {{ orderDate }}</div>
  </div>

  <!-- Predict Button -->
  <div>
    <button v-if="!loading" type="button" @click="getPrediction">Predict</button>
  </div>

  <!-- Loading Spinner -->
  <div v-if="loading" class="spinner">Loading...</div>

  <!-- Prediction Result -->
  <div class="prediction" v-if="prediction">Predicted number of days late: {{ prediction }}</div>

  <!-- Backend URL Display -->
  <div class="hint">Backend URL: {{ backendUrl }}</div>
</template>

<style scoped>
div {
  margin: 1em;
  text-align: right;
}

label {
  margin-right: 1em;
}

button {
  font-size: 1em;
  padding: 0.5em 1em;
  background-color: cadetblue;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: darkcyan;
}

.hint {
  font-size: 0.9em;
  color: #888;
}

.prediction {
  font-size: 1.5em;
  margin: 1em;
  color: cadetblue;
  text-align: center;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #4CAF50;
  animation: spin 1s ease infinite;
  margin: auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
