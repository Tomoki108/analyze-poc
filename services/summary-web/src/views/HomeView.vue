<template>
    <div class="home">
        <h1>ディニー</h1>
        <p>注文ログから、日次の注文状況やユーザーセグメントを分析</p>
        <div class="menu">
            <RouterLink to="/daily_order_summaries">日次注文サマリー</RouterLink>&nbsp;|&nbsp;
            <RouterLink to="/user_segments">ユーザーセグメント</RouterLink>
        </div>

        <br>
        <hr>
        <p>以下のような注文ログが随時大量に追加されると仮定し、それを分析しサマライズするPOC。</p>
        <p><code>{ "user_id": "u1", "timestamp": "2025-05-31T00:00:00Z", "menu_type": "washoku" }</code></p>
        <a href="https://github.com/Tomoki108/analyze-poc" target="_blank">GitHub Repository</a>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
    name: 'HomeView'
})
</script>

<style scoped>
.home {
    padding: 20px;
}

.menu {
    margin-top: 20px;
    /* display: flex;
    gap: 15px; */
    width: 100%;
}

.menu a {
    color: #42b983;
    text-decoration: none;
}

.menu a:hover {
    text-decoration: underline;
}
</style>
