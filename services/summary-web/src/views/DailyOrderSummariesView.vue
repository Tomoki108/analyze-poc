<template>
    <div class="daily-order-summaries">
        <h1>日別注文サマリー</h1>

        <div class="date-picker">
            <DatePicker v-model="selectedDate" type="month" format="YYYY-MM" />
            <button @click="fetchData">データ取得</button>
        </div>

        <div v-if="loading" class="loading">読み込み中...</div>

        <div v-if="error" class="error">{{ error }}</div>

        <div v-if="chartData" class="chart-container">
            <Pie :chartData="chartData" :options="chartOptions" />
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js'
import DatePicker from 'vue3-datepicker'

Chart.register(ArcElement, Tooltip, Legend)

export default {
    name: 'DailyOrderSummariesView',
    components: { Pie, DatePicker },
    setup() {
        const selectedDate = ref(new Date())
        const chartData = ref(null)
        const loading = ref(false)
        const error = ref(null)
        const apiHost = import.meta.env.VITE_API_HOST || 'http://localhost:8080'

        const fetchData = async () => {
            try {
                loading.value = true
                error.value = null

                const yearMonth = selectedDate.value.toISOString().slice(0, 7)
                const response = await fetch(`${apiHost}/api/daily_order_summaries?year_month=${yearMonth}`)

                if (!response.ok) {
                    throw new Error('Network response was not ok')
                }

                const data = await response.json()
                const summary = data.summaries[0] // 最初の日付のデータを使用
                chartData.value = {
                    labels: summary.counts.map(item => item.menu_type === 'washoku' ? '和食' : '洋食'),
                    datasets: [{
                        data: summary.counts.map(item => item.count),
                        backgroundColor: ['#36A2EB', '#FF6384'],
                        hoverBackgroundColor: ['#36A2EB', '#FF6384']
                    }]
                }
            } catch (err) {
                error.value = 'データの取得に失敗しました'
                console.error(err)
            } finally {
                loading.value = false
            }
        }

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false
        }

        return {
            selectedDate,
            chartData,
            loading,
            error,
            fetchData,
            chartOptions
        }
    }
}
</script>

<style scoped>
.daily-order-summaries {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}

.date-picker {
    margin: 20px 0;
    display: flex;
    gap: 10px;
    align-items: center;
}

button {
    padding: 5px 15px;
    background: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background: #3aa876;
}

.chart-container {
    height: 400px;
    margin-top: 20px;
}

.loading,
.error {
    margin: 20px 0;
    padding: 10px;
    text-align: center;
}

.error {
    color: #ff4444;
}
</style>
