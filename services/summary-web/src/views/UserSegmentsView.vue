<template>
    <div class="user-segments">
        <h2>ユーザーセグメント</h2>

        <div class="segment-selector">
            <select v-model="selectedSegment" @change="fetchData">
                <option value="washoku">和食派</option>
                <option value="yoshoku">洋食派</option>
            </select>
        </div>

        <div v-if="loading" class="loading">読み込み中...</div>

        <div v-if="error" class="error">{{ error }}</div>

        <div v-if="chartData" class="chart-container">
            <Pie :data="chartData" :options="chartOptions" />
        </div>

        <div v-if="selectedUserIds.length > 0" class="user-list">
            <h3>ユーザーIDリスト ({{ selectedSegment === 'washoku' ? '和食派' : '洋食派' }})</h3>
            <ul>
                <li v-for="userId in selectedUserIds" :key="userId">{{ userId }}</li>
            </ul>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { Pie } from 'vue-chartjs'
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js'

Chart.register(ArcElement, Tooltip, Legend)

interface Segment {
    menu_type: string
    count: number
    user_ids: string[]
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
    name: 'UserSegmentsView',
    components: { Pie },
    setup() {
        const selectedSegment = ref<string>('washoku')
        const segments = ref<Segment[]>([])
        const selectedUserIds = ref<string[]>([])
        const chartData = ref<ChartData | null>(null)
        const loading = ref<boolean>(false)
        const error = ref<string | null>(null)
        const apiHost = import.meta.env.VITE_API_HOST || 'http://localhost:8081'

        const fetchData = async () => {
            try {
                loading.value = true
                error.value = null
                chartData.value = null
                selectedUserIds.value = []

                const response = await fetch('/api/user_segments')
                if (!response.ok) {
                    throw new Error('Network response was not ok')
                }

                const data = await response.json()
                if (!data.segments || data.segments.length === 0) {
                    throw new Error('該当するデータが見つかりませんでした')
                }

                segments.value = data.segments
                updateChartAndUserList()
            } catch (err) {
                error.value = err instanceof Error ? err.message : 'データの取得に失敗しました'
                console.error(err)
            } finally {
                loading.value = false
            }
        }

        const updateChartAndUserList = () => {
            if (!segments.value) return

            // チャートデータ更新
            chartData.value = {
                labels: segments.value.map(s => s.menu_type === 'washoku' ? '和食派' : '洋食派'),
                datasets: [{
                    data: segments.value.map(s => s.count),
                    backgroundColor: ['#FF6384', '#36A2EB'],
                    hoverBackgroundColor: ['#FF6384', '#36A2EB']
                }]
            }

            // 選択されたセグメントのユーザーIDリスト更新
            const segment = segments.value.find(s => s.menu_type === selectedSegment.value)
            if (segment) {
                selectedUserIds.value = segment.user_ids
            }
        }

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false
        }

        return {
            selectedSegment,
            selectedUserIds,
            chartData,
            loading,
            error,
            fetchData,
            chartOptions
        }
    }
})
</script>

<style scoped>
.user-segments {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}

.segment-selector {
    margin: 20px auto;
    display: flex;
    gap: 10px;
    align-items: center;
    justify-content: center;
    width: fit-content;
}

select {
    padding: 5px 15px;
    border: 1px solid #ccc;
    border-radius: 4px;
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

.user-list {
    margin-top: 20px;
}

.user-list ul {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #eee;
    padding: 10px;
    list-style-type: none;
}

.user-list li {
    padding: 5px;
    border-bottom: 1px solid #eee;
}
</style>
