<template>
    <div class="wordcloud-container">
        <dv-border-box-7 :color = "['LightSkyBlue','white']">
        <div v-if="loading" class="loading-message">加载中...</div>
        <div v-else-if="error" class="error-message">{{ error }}</div>
        <div v-else-if="!wordcloudData || wordcloudData.length === 0" class="empty-message">
            暂无词云数据，系统将在每天凌晨3点自动更新。
        </div>
        <div v-else class="wordcloud-chart-container" ref="wordcloudChart"></div>
        </dv-border-box-7>
    </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';
// 确保导入echarts-wordcloud扩展
import 'echarts-wordcloud';

export default {
    name: 'WordCloud',
    data() {
        return {
            wordcloudData: [],
            loading: true,
            error: null,
            chart: null,
            chartInitialized: false
        };
    },
    mounted() {
        // 在组件挂载后获取数据
        this.fetchWordcloudData();
    },
    beforeDestroy() {
        // 组件销毁前释放图表资源
        this.disposeChart();
    },
    methods: {
        disposeChart() {
            // 安全地销毁图表实例
            if (this.chart) {
                this.chart.dispose();
                this.chart = null;
            }
            // 移除resize监听器
            window.removeEventListener('resize', this.handleResize);
        },
        async fetchWordcloudData() {
            this.loading = true;
            try {
                const response = await axios.get('/rumor/rumor_word');
                if (response.data.code === 0) {
                    this.wordcloudData = response.data.data.wordcloud_data || [];
                    
                    // 使用多重延迟确保DOM已完全渲染
                    setTimeout(() => {
                        this.initChart();
                    }, 300);
                } else {
                    this.error = response.data.message || '获取词云数据失败';
                }
            } catch (error) {
                console.error('词云数据请求出错：', error);
                this.error = '请求出错：' + (error.message || '未知错误');
            } finally {
                this.loading = false;
            }
        },
        initChart() {
            // 先销毁旧图表（如果存在）
            this.disposeChart();
            
            // 等待DOM完全渲染
            this.$nextTick(() => {
                try {
                    // 确保DOM元素存在且已渲染
                    if (!this.$refs.wordcloudChart) {
                        console.error('词云图容器元素不存在');
                        this.error = '初始化图表失败：等待DOM渲染';
                        
                        // 再次尝试初始化（以防DOM延迟渲染）
                        setTimeout(() => {
                            if (this.$refs.wordcloudChart) {
                                this.renderChart();
                            } else {
                                this.error = '初始化图表失败：DOM元素不存在';
                            }
                        }, 500);
                        return;
                    }
                    
                    this.renderChart();
                } catch (e) {
                    console.error('初始化词云图表失败:', e);
                    this.error = '初始化图表失败: ' + (e.message || '未知错误');
                }
            });
        },
        renderChart() {
            try {
                const chartDom = this.$refs.wordcloudChart;
                if (!chartDom) {
                    this.error = '渲染图表失败：DOM元素不存在';
                    return;
                }
                
                // 创建图表实例
                this.chart = echarts.init(chartDom);
                this.chartInitialized = true;
                
                // 添加错误处理
                this.chart.on('rendererror', (params) => {
                    console.error('渲染失败:', params);
                    this.error = '渲染失败: ' + (params.message || '未知错误');
                });
                
                // 检查数据格式
                const validData = this.wordcloudData.filter(item => 
                    item && typeof item === 'object' && 
                    item.name && typeof item.name === 'string' && 
                    item.value && typeof item.value === 'number'
                );
                
                if (validData.length === 0) {
                    console.error('词云数据格式无效');
                    this.error = '词云数据格式无效';
                    return;
                }
                
                const option = {
                    series: [
                        {
                            type: 'wordCloud',
                            width: '90%',
                            height: '90%',
                            right: 'center',
                            bottom: 'center',
                            shape: 'circle',
                            sizeRange: [12, 60],
                            rotationRange: [-90, 90],
                            rotationStep: 45,
                            gridSize: 8,
                            drawOutOfBound: false,
                            textStyle: {
                                color: function () {
                                    // 随机生成颜色
                                    return "rgb(" +
                                        [
                                            Math.round(Math.random() * 55 + 200), // 红色分量：200 - 255
                                            Math.round(Math.random() * 55 + 200), // 绿色分量：200 - 255
                                            Math.round(Math.random() * 55 + 200), // 蓝色分量：200 - 255
                                        ].join(",") + ")";
                                },
                                emphasis: {
                                    shadowBlur: 10,
                                    shadowColor: '#333'
                                }
                            },
                            data: validData.map(item => ({
                                name: item.name,
                                value: item.value
                            }))
                        }
                    ]
                };
    
                this.chart.setOption(option);
                
                // 添加窗口大小变化的监听
                window.addEventListener('resize', this.handleResize);
            } catch (e) {
                console.error('渲染词云失败:', e);
                this.error = '渲染词云失败: ' + (e.message || '未知错误');
            }
        },
        handleResize() {
            if (this.chart) {
                // 添加延迟避免频繁触发
                clearTimeout(this._resizeTimer);
                this._resizeTimer = setTimeout(() => {
                    this.chart.resize();
                }, 100);
            }
        }
    }
};
</script>

<style scoped>
.wordcloud-container {
    margin-top: 10px;
}

.wordcloud-chart-container {
    width: 100%;
    height: 240px;
}

.loading-message, .error-message, .empty-message {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 240px;
    color: white;
    font-size: 16px;
    text-align: center;
}

.error-message {
    color: #ff6b6b;
}
</style>