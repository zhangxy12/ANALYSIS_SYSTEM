<template>
    <div class="word-cloud-container" style="height: 90%;">
        
        <div class="title" style="text-decoration: none;"><i class="fa fa-tag"></i>    词频正反面统计</div>
        <div class="word-cloud">
            <div class="word-group">
                <h2 class="sub-title">正面高频词</h2>
                <ul class="word-list positive">
                    <li v-for="(word, index) in positiveWords" :key="index" class="p-word-item">
                        {{ word.name }}
                    </li>
                </ul>
            </div>
            <div class="word-group">
                <h2 class="sub-title">负面高频词</h2>
                <ul class="word-list negative">
                    <li v-for="(word, index) in negativeWords" :key="index" class="n-word-item">
                        {{ word.name }}
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            key: '',
            positiveWords: [],
            negativeWords: [],
        };
    },
    mounted() {
        this.key = this.$route.query.key;
        this.fetchWordData();
    },
    methods: {
        async fetchWordData() {
            try {
                const response = await axios.get(`/topic_ci?tag=${this.key}`);
                if (response.data.code === 0) {
                    console.log(response);
                    this.positiveWords = response.data.data.positive_words;
                    this.negativeWords = response.data.data.negative_words;
                    console.log(this.positiveWords, this.negativeWords); // 添加调试语句
                } else {
                    console.error('请求失败:', response.data.message);
                }
            } catch (error) {
                console.error('请求出错:', error);
            }
        },
        getFontSize(frequency) {
            // 根据词频动态设置字体大小，这里简单示例，可根据需求调整
            return Math.min(24, Math.max(12, frequency * 1.5));
        },
    },
};
</script>

<style scoped>
.word-cloud-container {
    text-align: center;
    padding: 10px;
    background-color: #f9f9f906;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 2px;
    color: #ffffff;
    text-decoration: none;
}

.sub-title {
    font-size: 15px;
    margin-bottom: 10px;
    color: #ffffff;
}

.word-cloud {
    display: flex;
    justify-content: space-around;
    overflow: hidden;
}

.word-group {
    width: 45%;
}

.word-list {
    list-style-type: none;
    padding: 0;
}

.word-item {
    
    margin: 5px 0;
    padding: 5px 10px;
    border-radius: 5px;
    display: inline-block;
    border: 1px solid #ccc;
    /* background-color: transparent; */
}

/* 增加选择器特异性 */
.p-word-item {
    font-size: 13px;
    margin: 5px 0;
    padding: 5px 7px;
    border-radius: 5px;
    display: inline-block;
    border: 1px solid #b1f0a3;
    background-color: #10bc5e65;
    color: white;
}

.n-word-item {
    font-size: 13px;
    margin: 5px 0;
    padding: 5px 7px;
    border-radius: 5px;
    display: inline-block;
    border: 1px solid #e2b2b2;
    background-color: #eb444494;
    color: white;
}
</style>