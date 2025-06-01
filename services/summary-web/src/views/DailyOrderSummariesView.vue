<template>
    <div class="daily-order-summaries">
        <h2>日次注文サマリー</h2>

        <div class="date-picker">
            <DatePicker v-model="selectedDate" format="YYYY-MM-DD" />
            <button @click="fetchData">データ取得</button>
        </div>

        <div v-if="loading" class="loading">読み込み中...</div>

        <div v-if="error" class="error">{{ error }}</div>

        <div v-if="chartData" class="chart-container">
            <Pie :data="chartData" :options="chartOptions" />
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js'
import DatePicker from 'vue3-datepicker'

Chart.register(ArcElement, Tooltip, Legend)

interface MenuCount {
    menu_type: string
    count: number
}

interface ChartData {
    labels: string[]
    datasets: {
        data: number[]
        backgroundColor: string[]
        hoverBackgroundColor: string[]
    }[]
}

export default defineComponent({
    name: 'DailyOrderSummariesView',
    components: { Pie, DatePicker },
    setup() {
        const selectedDate = ref<Date>(new Date())
        const chartData = ref<ChartData | null>(null)
        const loading = ref<boolean>(false)
        const error = ref<string | null>(null)
        const apiHost = import.meta.env.VITE_API_HOST || 'http://localhost:8081'

        const fetchData = async () => {
            try {
                loading.value = true
                error.value = null

                // タイムゾーン補正なしで日付を取得
                const year = selectedDate.value.getFullYear()
                const month = String(selectedDate.value.getMonth() + 1).padStart(2, '0')
                const day = String(selectedDate.value.getDate()).padStart(2, '0')
                const date = `${year}-${month}-${day}`
                const response = await fetch(`/api/daily_order_summaries?date=${date}`)

                if (!response.ok) {
                    throw new Error('Network response was not ok')
                }

                const data = await response.json()
                if (!data.summaries || data.summaries.length === 0) {
                    throw new Error('該当するデータが見つかりませんでした')
                }
                const summary = data.summaries[0]
                if (!summary.counts || summary.counts.length === 0) {
                    throw new Error('注文データが見つかりませんでした')
                }
                chartData.value = {
                    labels: summary.counts.map(item => item.menu_type === 'washoku' ? '和食' : '洋食'),
                    datasets: [{
                        data: summary.counts.map(item => item.count),
                        backgroundColor: ['#36A2EB', '#FF6384'],
                        hoverBackgroundColor: ['#36A2EB', '#FF6384']
                    }]
                }
            } catch (err) {
                error.value = err instanceof Error ? err.message : 'データの取得に失敗しました'
                chartData.value = null
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
            chartOptions,
        }
    }
})
</script>

<style scoped>
.daily-order-summaries {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}

.date-picker {
    margin: 20px auto;
    display: flex;
    gap: 10px;
    align-items: center;
    justify-content: center;
    width: fit-content;
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
