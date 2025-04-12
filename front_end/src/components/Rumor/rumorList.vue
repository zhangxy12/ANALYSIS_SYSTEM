<template>
    <div class="rumor-list">
        <!-- 筛选条件 -->
        <div class="filter">
            <button @click="filterRumors('all')" class="tech-button">全部</button>
            <button @click="filterRumors('oneWeek')" class="tech-button">一周</button>
            <button @click="filterRumors('oneMonth')" class="tech-button">一个月</button>
            <button @click="filterRumors('oneYear')" class="tech-button">一年</button>
        </div>

        <ul class="rumor-ul">
            <li v-for="rumor in filteredRumorList" :key="rumor.url">
                <a :href="rumor.url" target="_blank">{{ rumor.date }}</a>
                
            </li>
        </ul>

        <div v-if="loading">加载中...</div>
        <div v-else-if="error">{{ error }}</div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            rumors: [], // 所有谣言数据
            filteredRumorList: [], // 筛选后的谣言列表
            loading: true,
            error: null,
            filterOption: 'all', // 当前筛选选项
        };
    },
    methods: {
        async fetchRumors() {
            try {
                const response = await this.$axios.post('/rumor/rumor_search');
                if (response.data.message === '谣言搜索并存储成功') {
                    this.rumors = response.data.data;
                    // 按日期从大到小排序
                    this.rumors.sort((a, b) => {
                        const dateA = new Date(a.date);
                        const dateB = new Date(b.date);
                        return dateB - dateA;
                    });
                    console.log(this.rumors);
                    this.filteredRumorList = this.rumors;
                    this.loading = false;
                } else {
                    this.error = response.data.message;
                    this.loading = false;
                }
            } catch (err) {
                this.error = '获取数据失败';
                this.loading = false;
            }
        },

        filterRumors(option) {
            this.filterOption = option;
            this.applyFilter();
        },

        applyFilter() {
            const now = new Date();
            const filtered = this.rumors.filter(rumor => {
                const rumorDate = new Date(rumor.date);
                switch (this.filterOption) {
                    case 'oneWeek':
                        return now - rumorDate <= 7 * 24 * 60 * 60 * 1000; // 一周内
                    case 'oneMonth':
                        return now - rumorDate <= 30 * 24 * 60 * 60 * 1000; // 一个月内
                    case 'oneYear':
                        return now - rumorDate <= 365 * 24 * 60 * 60 * 1000; // 一年内
                    default:
                        return true; // 全部
                }
            });
            this.filteredRumorList = filtered;
        }
    },
    mounted() {
        this.fetchRumors();
    }
};
</script>

<style scoped>
.rumor-list {
    margin-left: 55px;
    padding: 20px;
    background-color: #f9f9f900;
    /* border: 2px solid rgba(5, 162, 189, 0.774); */
    /* border-radius: 4px; */
    /* box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); */
    max-width: 800px;
    margin: 20px auto;
    color:white; padding: 1rem;
    box-shadow: 0 0 3rem rgba(100,200,255,.5) inset;
    background: rgba(106, 150, 148, 0.216);
    border-radius: 10px;
}

.filter {
    margin-bottom: 10px;
    display: flex;
}

.filter button {
    padding: 8px 10px;
    margin-right: 10px;
    border: none;
    border-radius: 4px;
    background-color: #007bff;
    color: white;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.filter button:hover {
    background-color: #0056b3;
}

.rumor-ul {
    max-height: 250px; /* 设置固定的最大高度 */
    overflow-y: auto; /* 超出高度显示垂直滚动条 */
    list-style: none;
    padding: 0;
    /* 自定义滚动条样式 */
   scrollbar-width: none; 
    padding: 10px;
}

.rumor-ul li {
    margin-bottom: 10px;
    padding: 8px;
    border-bottom: 1px solid #eee;
}

.rumor-ul li a {
    font-weight: bold;
    color: #f4f6f6;
    text-decoration: none;
    transition: color 0.3s ease;
}

.rumor-ul li a:hover {
    color: #10e6e6;
}

.rumor-ul li span {
    margin-left: 3px;
    color: #272f36;
}

.loading {
    text-align: center;
    color: #6c757d;
    margin-top: 20px;
}

.error {
    text-align: center;
    color: red;
    margin-top: 20px;
}

/* 自定义滚动条样式 */
.rumor-ul::-webkit-scrollbar {
    width: 5px;
}

.rumor-ul::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.rumor-ul::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

.rumor-ul::-webkit-scrollbar-thumb:hover {
    background: #555;
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

@keyframes techFlow {
    0% { transform: translateX(-25%) translateY(-25%); }
    100% { transform: translateX(25%) translateY(25%); }
}
</style>