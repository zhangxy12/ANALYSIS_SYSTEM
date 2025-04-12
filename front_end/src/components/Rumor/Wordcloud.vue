<template>
    
    <div class="wordcloud-container">
        <dv-border-box-7 :color = "['LightSkyBlue','white']">
        <div ref="wordcloud" style="width: 100%; height: 240px;"></div>
    </dv-border-box-7>
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
            error: null
        };
    },
    mounted() {
        this.fetchWordcloudData();
    },
    methods: {
        async fetchWordcloudData() {
            this.loading = true;
            try {
                const response = await axios.get('/rumor/rumor_word');
                if (response.data.code === 0) {
                    this.wordcloudData = response.data.data.wordcloud_data;
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
            const myChart = echarts.init(chartDom);

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
                        data: this.wordcloudData.map(item => ({
                            name: item.name,
                            value: item.value
                        }))
                    }
                ]
            };

            option && myChart.setOption(option);
        }
    }
};
</script>

<style scoped>
.wordcloud-container {
    margin-top: 10px;
}
</style>