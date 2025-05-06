<template>
    
    <div class="wordcloud-container">
        <h2><i class="fa fa-cloud" style="color: #ffffff;"></i>     热点词云</h2>
        <div ref="wordcloud" style="width: 95%; height: 175px;"></div>
    </div>

</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
    name: 'WordCloud',
    data() {
        return {
            wordcloudData: [],
            loading: false,
            error: null,
            chart: null
        };
    },
    props: {
        refresh: {
            type: Boolean,
            default: false
        }
    },
    watch: {
        refresh() {
            this.fetchWordcloudData();
        }
    },
    mounted() {
        this.fetchWordcloudData();
    },
    methods: {
        async fetchWordcloudData() {
            this.loading = true;
            try {
                const response = await axios.get('/main/all_hot_word');
                console.log(response);
                if (response.data.code === 0) {
                    this.wordcloudData = response.data.data;
                    console.log(this.wordcloudData);
                    this.renderWordcloud();
                } else {
                    this.error = response.data.message;
                }
            } catch (error) {
                this.error = '请求出错：' + error.message;
            } finally {
                this.loading = false;
            }
        },
        renderWordcloud() {
            const chartDom = this.$refs.wordcloud;
            if (!chartDom) {
                console.error('找不到图表DOM元素');
                return;
            }
            
            // 检查是否已有图表实例，如果有则销毁
            if (this.chart) {
                this.chart.dispose();
            }
            
            // 创建新实例
            this.chart = echarts.init(chartDom);

            const option = {
                series: [
                    {
                        type: 'wordCloud',
                        width: '90%',
                        height: '90%',
                        right: 'center',
                        left:'center',
                        top:'3px',
                        bottom: 'center',
                        shape: 'circle',
                        sizeRange: [8, 40], 
                        rotationRange: [-90, 90],
                        rotationStep: 45,
                        gridSize: 8,
                        drawOutOfBound: false,
                        textStyle: {
                            color: function () {
                                // 随机生成蓝色系颜色
                                return "rgb(" +
                                    [
                                        Math.round(Math.random() * 55 + 120), // 红色分量：0 - 55
                                        Math.round(Math.random() * 55 + 180), // 绿色分量：0 - 55
                                        Math.round(Math.random() * 55 + 220) // 蓝色分量：200 - 255
                                    ].join(",") + ")";
                            },
                            emphasis: {
                                shadowBlur: 10,
                                shadowColor: '#333'
                            }
                        },
                        data: this.wordcloudData.map(item => ({
                            name: item.name,
                            value: item.value
                        }))
                    }
                ]
            };

            option && this.chart.setOption(option);
        }
    }
};
</script>

<style scoped>
h2 {
    text-align: center;
    font-size: 18px;
    color: #f2f2f2;
    margin-bottom: 0px;
}
.wordcloud-container {
    margin-top: 0px;
}
</style>