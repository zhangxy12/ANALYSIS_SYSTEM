<template>
    <div class="mood-container">
        
        <div class="content-wrapper">
            <div class="left-chart">
                <h2><svg t="1741847242078" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5180" width="15" height="15"><path d="M108.8 121.6v787.2h800V121.6z m51.2 51.2h697.6v678.4H160z" p-id="5181" fill="#ffffff"></path><path d="M390.976 586.752c-10.816-1.792-21.312-4.544-32.448-7.424l-3.52-0.96-9.344-2.432a153.6 153.6 0 0 1-57.6-38.4 153.216 153.216 0 0 1-38.4-57.6 230.4 230.4 0 0 1-12.8-70.4 217.6 217.6 0 0 1 9.536-57.984l3.2-12.416a153.6 153.6 0 0 1 38.4-57.6 152.64 152.64 0 0 1 57.6-38.4 229.888 229.888 0 0 1 70.4-12.8 211.2 211.2 0 0 1 56.512 9.344l3.008 0.768 10.944 2.752a151.68 151.68 0 0 1 57.6 38.4 152.832 152.832 0 0 1 38.4 57.6 229.312 229.312 0 0 1 12.8 70.4v0.32c-4.544 0-8.704-0.32-12.8-0.32s-8.32 0-12.8 0.448V409.6a155.648 155.648 0 0 0-153.6-153.6 155.712 155.712 0 0 0-153.6 153.6 156.992 156.992 0 0 0 132.16 152.064 193.536 193.536 0 0 0-3.584 25.088z m25.088-81.216h-76.8a74.24 74.24 0 0 1 76.8-76.8 76.8 76.8 0 0 1 51.968 18.56 191.296 191.296 0 0 0-51.84 58.112z m64-115.2a27.712 27.712 0 0 1-25.6-25.6c0-12.8 6.4-19.2 25.6-25.6a27.712 27.712 0 0 1 25.6 25.6 27.648 27.648 0 0 1-25.6 25.6z m-121.6 0a27.712 27.712 0 0 1-25.6-25.6c0-12.8 6.4-19.2 25.6-25.6a27.392 27.392 0 0 1 25.6 25.6 27.328 27.328 0 0 1-25.6 25.6z" p-id="5182" fill="#ffffff"></path><path d="M505.6 563.2a25.6 25.6 0 0 0 51.2 0 25.6 25.6 0 0 0-51.2 0z m115.2 0a25.6 25.6 0 1 0 25.6-25.6c-19.2 6.4-25.6 12.8-25.6 25.6z m32 70.4a70.4 70.4 0 1 1-140.8 0z" p-id="5183" fill="#ffffff"></path><path d="M582.4 761.6a189.312 189.312 0 0 1-64-12.8 99.52 99.52 0 0 1-51.2-38.4 209.728 209.728 0 0 1-38.4-51.2 189.376 189.376 0 0 1-12.8-64 227.328 227.328 0 0 1 12.8-64 99.52 99.52 0 0 1 38.4-51.2c19.2-12.8 38.4-32 51.2-38.4a166.4 166.4 0 0 1 128 0 99.52 99.52 0 0 1 51.2 38.4 209.728 209.728 0 0 1 38.4 51.2 166.4 166.4 0 0 1 0 128 99.52 99.52 0 0 1-38.4 51.2 209.792 209.792 0 0 1-51.2 38.4 227.328 227.328 0 0 1-64 12.8z m0-307.2a140.8 140.8 0 1 0 140.8 140.8 142.08 142.08 0 0 0-140.8-140.8z" p-id="5184" fill="#ffffff"></path></svg>     情感分析</h2>
                <div ref="sentimentChart" style="width: 96%; height: 210px; margin-bottom: 4px;"></div>
            </div>
            <div class="right-words">
                <div class="positive-words">
                    <h3>正面高频词语</h3>
                    <div class="word-list">
                        <span v-for="(word, index) in topPositiveWords" :key="index" class="p-word-item">
                            {{ word.name }}
                        </span>
                    </div>
                </div>
                <div class="negative-words">
                    <h3>负面高频词语</h3>
                    <div class="word-list">
                        <span v-for="(word, index) in topNegativeWords" :key="index" class="n-word-item">
                            {{ word.name }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
    props: {
        refresh: {
            type: Boolean,
            default: false
        }
    },
    watch: {
        refresh() {
            this.fetchData();
        }
    },
    data() {
        return {
            sentimentRatio: {
                positive: 0,
                negative: 0,
                neutral: 0
            },
            topPositiveWords: [],
            topNegativeWords: [],
            chart: null
        };
    },
    mounted() {
        this.initChart();
        this.fetchData();
    },
    methods: {
        initChart() {
            // 检查图表DOM元素
            if (!this.$refs.sentimentChart) {
                console.error('找不到图表DOM元素');
                return;
            }

            // 如果已有图表实例，先销毁它
            if (this.chart) {
                this.chart.dispose();
            }

            // 创建新的图表实例
            this.chart = echarts.init(this.$refs.sentimentChart);
            this.updateChart();
        },
        updateChart() {
            const option = {
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                series: [
                    {
                        name: '情感占比',
                        type: 'pie',
                        radius: '50%',
                        data: [
                            { value: this.sentimentRatio.positive, name: '积极', itemStyle: { color: '#1f78b4' } },
                            { value: this.sentimentRatio.negative, name: '消极', itemStyle: { color: '#6bd6d1' } },
                            { value: this.sentimentRatio.neutral, name: '中性', itemStyle: { color: '#9ecae1' } }
                        ],
                        label: {
                            color: '#fff',
                            fontSize: 12,
                            position: 'outside', // 标签显示在外部
                            alignTo: 'edge', // 标签对齐到边缘
                            margin: 1 // 标签与色块的间距
                        },
                        labelLine: {
                            length: 6, // 第一段线长度
                            length2: 2, // 第二段线长度
                            lineStyle: {
                                color: '#fff'
                            }
                        }
                    }
                ]
            };
            this.chart.setOption(option);
        },
        async fetchData() {
            try {
                const response = await axios.get('/main/all_hot_mood');
                if (response.data.code === 0) {
                    const data = response.data.data;
                    this.sentimentRatio = data.sentiment_ratio;
                    this.topPositiveWords = data.top_positive_words;
                    this.topNegativeWords = data.top_negative_words;
                    
                    // 检查是否有数据
                    const hasData = (this.sentimentRatio.positive > 0 || 
                                    this.sentimentRatio.negative > 0 || 
                                    this.sentimentRatio.neutral > 0 ||
                                    this.topPositiveWords.length > 0 ||
                                    this.topNegativeWords.length > 0);
                    // 发送数据状态到父组件
                    this.$emit('data-status', hasData);
                    
                    this.updateChart();
                } else {
                    console.error('请求失败:', response.data.message);
                    this.$emit('data-status', false);
                }
            } catch (error) {
                console.error('发生错误:', error);
                this.$emit('data-status', false);
            }
        }
    }
};
</script>

<style scoped>
h2 {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 1px; /* 为标题下方添加一些间距 */
    margin-left: 20px;
}

.mood-container {
    display: flex;
    flex-direction: column; /* 设置为纵向布局 */
    color: #fff;
}

.content-wrapper {
    display: flex;
    justify-content: space-between;
}

.left-chart {
    width: 59%;
}

.right-words {
    width: 41%;
}

.positive-words,
.negative-words {
    margin-top: 8px;
    margin-bottom: 5px;
}

h3 {
    font-weight: 500;
    margin-top: 0;
    font-size: 14px;
    color: #fffffff4;
}

.word-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.p-word-item {
    font-size: 12px;
    color: #fff;
    background-color: #0693f274;
    padding: 4px 8px;
}

.n-word-item {
    font-size: 12px;
    color: #fff;
    background-color: #6bd6d15f;
    padding: 4px 8px;
}
</style>