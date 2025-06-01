<template>
    <div class="home">
        <h1>ディニー</h1>
        <p>注文ログから、日次の注文状況やユーザーセグメントを分析</p>
        <div class="menu">
            <!-- <RouterLink to="/about">About</RouterLink> -->
            <RouterLink to="/daily_order_summaries">日次注文サマリー</RouterLink>
        </div>
    </div>
</template>

<script>
export default {
    name: 'HomeView'
}
</script>

<style scoped>
.home {
    padding: 20px;
}

.menu {
    margin-top: 20px;
    display: flex;
    gap: 15px;
}

.menu a {
    color: #42b983;
    text-decoration: none;
}

.menu a:hover {
    text-decoration: underline;
}
</style>
