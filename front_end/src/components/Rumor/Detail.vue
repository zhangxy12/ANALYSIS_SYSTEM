<template>
    <div class="detail">
        <div class="fixed-header">
            <div class="search-container" tabindex="1">
                <input v-model="searchQuery" type="text" placeholder="输入搜索内容">
                <button @click="searchRumors" class="button">
                    <i class="fa fa-search"></i>
                </button>
            </div>
            <h2>谣言详情</h2>
        </div>

        <!-- 加载状态和错误提示 -->
        <div v-if="loading" class="center-message">
            <p>数据加载中...</p>
        </div>
        <div v-else-if="error" class="center-message error-message">
            <p>{{ error }}</p>
        </div>
        <div v-else-if="filteredRumors.length === 0" class="center-message">
            <p>暂无谣言数据，系统将在每天凌晨3点自动更新。</p>
        </div>

        <!-- 遍历所有谣言并显示 -->
        <div v-else class="all">
            <div v-for="(rumor, index) in filteredRumors" :key="index" class="rumor-item">
                <a :href="`/rumorAnalyse?key=${encodeURIComponent(rumor.rumor)}`" class="rumor-title">
                <span><strong>谣言:</strong> {{ rumor.rumor }}</span>
                </a>
                <div class="right-align-container">
                    <span><strong>日期:</strong> {{ rumor.date }}</span>
                    <button @click="toggleTruth(index)" class="tech-button">
                        {{ showTruth[index] ? '收回真相' : '显示真相' }}
                    </button>
                </div>
                
            
                <span v-if="showTruth[index]" class="truth-content">
                    <p><strong>真相:</strong> {{ rumor.truth }}</p>
                </span>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            rumors: [],
            showTruth: [],
            searchQuery: '',
            filteredRumors: [],
            loading: true,
            error: null
        };
    },
    methods: {
        async fetchRumorDetails() {
            try {
                this.loading = true;
                this.error = null;
                const response = await axios.post('/rumor/rumor_detail');
                
                if (response.data.data && response.data.data.length > 0) {
                    this.rumors = response.data.data;
                    // 按日期从大到小排序
                    this.rumors.sort((a, b) => {
                        const dateA = new Date(a.date);
                        const dateB = new Date(b.date);
                        return dateB - dateA;
                    });
                    this.filteredRumors = this.rumors;
                    // 确保初始化数组与数据长度一致
                    this.showTruth = new Array(this.rumors.length).fill(false);
                } else {
                    // 如果没有数据，设置空数组
                    this.rumors = [];
                    this.filteredRumors = [];
                    this.showTruth = [];
                }
                this.loading = false;
            } catch (error) {
                console.error('获取数据失败', error);
                this.error = '获取数据失败，请稍后再试';
                this.loading = false;
            }
        },
        toggleTruth(index) {
            this.$set(this.showTruth, index, !this.showTruth[index]);
        },
        searchRumors() {
            if (this.searchQuery === '') {
                this.filteredRumors = this.rumors;
            } else {
                this.filteredRumors = this.rumors.filter(rumor => {
                    return rumor.rumor.includes(this.searchQuery) || rumor.truth.includes(this.searchQuery);
                });
            }
            if (this.filteredRumors.length > 0) {
                // 定位到第一个匹配项
                const firstMatch = document.querySelector('.rumor-item');
                if (firstMatch) {
                    firstMatch.scrollIntoView({ behavior: 'smooth' });
                }
            }
        }
    },
    mounted() {
        this.fetchRumorDetails();
    }
};
</script>

<style scoped>

*,
*::before,
*::after {
    box-sizing: border-box;
}

html {
    height: 100%;
}

body {
    height: 100%;
    background: #FDF6E3;
    font-family: "Cabin";
}

.detail {
    background-color: #f9f9f900;
    /* border: 2px solid rgba(5, 162, 189, 0.774); */
    /* border-radius: 4px; */
    /* box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); */
    max-width: 880px;
    max-height: 52vh; /* 设置固定的最大高度 */
    overflow-y: auto; /* 超出高度显示垂直滚动条 */
    list-style: none;
    padding: 0;
    /* 自定义滚动条样式 */
    scrollbar-width: none;
    position: relative;
    background: linear-gradient(to left, #2CD5FF, #2CD5FF) left top no-repeat,
                linear-gradient(to bottom, #2CD5FF, #2CD5FF) left top no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) right top no-repeat,
                linear-gradient(to bottom, #2CD5FF, #2CD5FF) right top no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) left bottom no-repeat,
                linear-gradient(to bottom, #2CD5FF, #2CD5FF) left bottom no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) right bottom no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) right bottom no-repeat;
                background-size: 4px 20px, 20px 4px, 4px 20px, 20px 4px;
                border-image: linear-gradient(rgba(5, 162, 189, 0.774), rgba(249, 249, 249, 0.9), rgba(5, 162, 189, 0.774));
                border-image-slice: 1;
                border-width: 2px;
                border-style: solid;
}

.fixed-header {

    top: 0;
    background-color: rgba(71, 179, 237, 0); /* 可以根据需要调整背景颜色 */
    padding: 10px;
    z-index: 1; /* 确保固定头部在滚动内容之上 */
    
}
.fixed-header h2{
    color: #fefefe;
}
.search-container {
    overflow: hidden;
    float: right;
    height: 4em;
    width: 4em;
    border-radius: 2em;
    
    transition: all 0.35s;
    box-shadow: 0 0 3rem rgba(100,200,255,.5) inset;
    background: rgba(106, 150, 148, 0.216);
}

.search-container:hover,
.search-container:focus,
.search-container:focus-within {
    width: 25em;
    border-radius: 5px 2em 2em 5px;
    outline: none;
}

.search-container:hover input,
.search-container:focus input,
.search-container:focus-within input {
    display: inline-block;
    width: 19em;
    padding: 10px;
}

input {
    -moz-appearance: none;
    -webkit-appearance: none;
    appearance: none;
    float: left;
    width: 0em;
    height: 2.3em;
    margin: 1em;
    margin-right: -4.5em;
    background: #fff;
    color: #6A5D4F;
    font-size: 1em;
    font-weight: 600;
    padding: 0px;
    border: 0;
    border-radius: 5px;
    box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2) inset;
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.15);
    transition: all 0.25s;
}

input:focus {
    outline: none;
    box-shadow: 0 -1px 1px rgba(255, 255, 255, 0.25), 0 1px 5px rgba(0, 0, 0, 0.15);
}

.button {
    display: flex;
    align-items: center;
    justify-content: center;
    float: right;
    width: 1.75em;
    height: 1.8em;
    margin: 0.125em;
    background: #23b6c1;
    text-align: center;
    font-size: 2em;
    color: #FDF6E3;
    border-radius: 50%;
    box-shadow: 0 -1px 1px rgba(255, 255, 255, 0.25), 0 1px 1px rgba(0, 0, 0, 0.25);
    text-shadow: 0 -2px 1px rgba(0, 0, 0, 0.3);
    border: none;
    cursor: pointer;
}

.button:active {
    border: 0 !important;
    text-shadow: 0 0 0;
}

.button i {
    font-size: 85%;
}
/* 优化后的 .rumor-title 样式 */
.rumor-title {
    display: inline-block; /* 使链接作为块级元素显示，但不独占一行 */
    padding: 8px 12px; /* 添加内边距，让内容与边框有一定间距 */
    text-decoration: none; /* 去除下划线 */
    font-size: 16px; /* 字体大小 */
    transition: all 0.3s ease; /* 添加过渡效果，使鼠标悬停时变化更平滑 */
    margin-bottom: 8px; /* 与下方元素保持一定间距 */
}

.rumor-title:hover {
    background-color: #b7dbef48; /* 鼠标悬停时背景颜色变深 */
    
    transform: scale(1.02); /* 鼠标悬停时稍微放大 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
}

.rumor-title span {
    font-weight: 500; /* 调整谣言文字的字体粗细 */
}
.rumor-item {
    margin-left: 15px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #e0e0e0; /* 使用横线隔开每条谣言 */
    transition: box-shadow 0.2s;
}

.rumor-item span {
    margin-right: 15px;
    color: #ffffff;
}

button {
    padding: 8px 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
    margin-right: 15px;
}

button:hover {
    background-color: #38d2c3;
}

.truth-content {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 1; transform: translateY(0); }
}

.right-align-container {
    display: flex;
    align-items: center;
    margin-left: auto;
}

.tech-button {
    
    /* 布局 */
    padding: 8px 12px;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    
    /* 文字 */
    font-size: 13px;
    font-weight: 1000;
    letter-spacing: 0.5px;
    color: #fff;
    text-transform: uppercase;
    
    /* 背景与边框 */
    background: linear-gradient(135deg, #15bac0 0%, #2663be 100%);
    border: none;
    border-radius: 8px;
    
    /* 光影效果 */
    box-shadow: 
        0 4px 20px rgba(5, 40, 108, 0.3),
        inset 0 2px 4px rgba(255, 255, 255, 0.1);
    
    /* 交互效果 */
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

/* 悬停状态 */
.tech-button:hover {
    transform: translateY(-1px);
    background: linear-gradient(135deg, #2663be 0%, #15bac0 100%);
    box-shadow: 
        0 6px 24px rgba(5, 40, 108, 0.4),
        inset 0 3px 6px rgba(255, 255, 255, 0.15);
}

/* 点击状态 */
.tech-button:active {
    transform: translateY(1px);
    box-shadow: 
        0 2px 12px rgba(5, 40, 108, 0.2),
        inset 0 1px 2px rgba(255, 255, 255, 0.1);
}

/* 科技感边框高光 (可选) */
.tech-button::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    pointer-events: none;
}

/* 动态流光效果 (可选) */
.tech-button::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        45deg,
        transparent 25%,
        rgba(255, 255, 255, 0.1) 50%,
        transparent 75%
    );
    animation: techFlow 4s infinite linear;
    opacity: 0.3;
}

.center-message {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    color: white;
    font-size: 18px;
}

.error-message {
    color: #ff6b6b;
}

@keyframes techFlow {
    0% { transform: translateX(-25%) translateY(-25%); }
    100% { transform: translateX(25%) translateY(25%); }
}
</style>