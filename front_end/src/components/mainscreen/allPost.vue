<template>
    <div>
        <h2><svg t="1741848222918" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="16922" width="200" height="200"><path d="M170.667 739.556c34.133 0 56.889 22.755 56.889 56.888v113.778c0 34.134-22.756 56.89-56.89 56.89s-56.888-22.756-56.888-56.89V796.444c0-34.133 22.755-56.888 56.889-56.888z m682.666-341.334c34.134 0 56.89 22.756 56.89 56.89v455.11c0 34.134-22.756 56.89-56.89 56.89s-56.889-22.756-56.889-56.89v-455.11c0-34.134 22.756-56.89 56.89-56.89z m-455.11 284.445c34.133 0 56.888 22.755 56.888 56.889v170.666c0 34.134-22.755 56.89-56.889 56.89s-56.889-22.756-56.889-56.89V739.556c0-34.134 22.756-56.89 56.89-56.89z m227.555-113.778c34.133 0 56.889 22.755 56.889 56.889v284.444c0 34.134-22.756 56.89-56.89 56.89s-56.888-22.756-56.888-56.89V625.778c0-34.134 22.755-56.89 56.889-56.89zM790.756 301.51c-5.69-130.844-11.378-204.8-17.067-227.555C768 51.2 750.933 39.822 722.489 45.51l-227.556 96.711c-17.066 17.067-11.377 28.445 5.69 34.134 11.377 5.688 34.133 22.755 79.644 45.51-108.09 164.978-238.934 267.378-455.111 312.89-34.134 5.688-34.134 34.133-5.69 34.133C347.023 557.51 534.757 460.8 671.29 278.756c28.444 17.066 51.2 34.133 85.333 51.2 28.445 11.377 39.822 5.688 34.134-28.445z" fill="#ffffff" p-id="16923"></path></svg>     舆情趋势</h2>
        <!-- 使用原生 radio 按钮实现时间范围选择 -->
        <div class="option-container" style="height: 20px;">
            <input type="radio" id="oneWeek" name="timeRange" value="oneWeek" v-model="timeRange" @change="fetchData">
            <label for="oneWeek">一周</label>
            <input type="radio" id="oneMonth" name="timeRange" value="oneMonth" v-model="timeRange" @change="fetchData">
            <label for="oneMonth">一个月</label>
        </div>
        <div ref="chart" style="width: 100%; height: 190px; margin-top: 0%;"> </div>
        <div v-if="errorMessage" style="color: red;">{{ errorMessage }}</div>
    </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
    data() {
        return {
            chart: null,
            errorMessage: '',
            timeRange: 'oneWeek',
            data: [] // 修改为数组
        };
    },
    mounted() {
        this.fetchData();
    },
    methods: {
        async fetchData() {
            try {
                const response = await axios.get('/main/all_post');
                console.log(response);
                if (response.data.code === 0) {
                    this.data = response.data.data || []; // 确保 this.data 是一个数组
                    console.log(this.data);
                    this.drawChart();
                } else {
                    this.errorMessage = response.data.message;
                }
            } catch (error) {
                this.errorMessage = '请求数据时出现错误，请稍后重试。';
                console.error(error);
            }
        },

        drawChart() {
            const appNames = ['微信', '微博', '人民网', '贴吧'];
            const appKeys = ['wechat', 'weibo', 'renmin', 'tieba'];
            const timePeriod = this.getTimePeriod();

            // 提取数据
            const filteredData = this.data
                .flatMap(item => item.data) // 将嵌套的 data 数组扁平化
                .filter(item => timePeriod.includes(item.date)) // 过滤出符合时间范围的数据
                .sort((a, b) => new Date(a.date) - new Date(b.date)); // 按日期排序

            // 提取日期
            const dates = filteredData.map(item => item.date);

            // 提取每个平台的数据
            const seriesData = appKeys.map(key => {
                return filteredData.map(item => item.source_count[key] || 0);
            });

            // 打印调试信息
            console.log('Filtered Data:', filteredData);
            console.log('Dates:', dates);
            console.log('Series Data:', seriesData);

            this.chart = echarts.init(this.$refs.chart);

            const option = {
                // title: {
                //     text: '舆情趋势',
                //     left: 'center',
                //     textStyle: {
                //         color: '#fff',
                //         fontSize: 18,
                //         fontWeight: 'bold'
                //     }
                // },
                top:'0',
                bottom:'20',
                tooltip: {
                    trigger: 'axis'
                },
                grid: {
                    top:'0.1%',
                    show: false // 不显示网格
                },
                xAxis: {
                    type: 'category',
                    data: dates,
                    axisLabel: {
                        color: '#fff'
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#fff'
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    axisLabel: {
                        color: '#fff'
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#fff'
                        }
                    }
                },
                series: appNames.map((name, index) => {
                    return {
                        name: name,
                        type: 'line',
                        data: seriesData[index],
                        areaStyle: {
                            opacity: 0.3 // 曲线阴影透明度
                        },
                        itemStyle: {
                            color: this.getColor(index)
                        },
                        lineStyle: {
                            color: this.getColor(index)
                        },
                        smooth: true // 添加 smooth 属性，将折线变为平滑曲线
                    };
                })
            };

            this.chart.setOption(option);
        },
        getTimePeriod() {
            const now = new Date();
            const timePeriod = [];
            if (this.timeRange === 'oneWeek') {
                for (let i = 6; i >= 0; i--) {
                    const date = new Date(now);
                    date.setDate(now.getDate() - i);
                    timePeriod.push(date.toISOString().split('T')[0]);
                }
            } else if (this.timeRange === 'oneMonth') {
                for (let i = 29; i >= 0; i--) {
                    const date = new Date(now);
                    date.setDate(now.getDate() - i);
                    timePeriod.push(date.toISOString().split('T')[0]);
                }
            }
            return timePeriod;
        },
        getColor(index) {
            const colors = ['#1f78b4', '#6baed6', '#9ecae1', '#c6dbef'];
            return colors[index % colors.length];
        }
    }
};
</script>

<style scoped>
h2 {
    text-align: center;
    font-size: 18px;
    color: #f2f2f2;
    margin-bottom: 1px;
}

/* 未选中时的样式 */
input[type="radio"] {
  accent-color: rgb(205, 237, 248); /* 未选中时的颜色 */
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); /* 未选中时的阴影 */
}

/* 选中时的样式 */
input[type="radio"]:checked {
  accent-color: rgba(12, 243, 227, 0.867); /* 选中时的颜色 */
  box-shadow: 0 0 5px rgba(12, 243, 228, 0.389); /* 未选中时的阴影 */
}

.option-container {
    margin-top: 0px;
    margin-bottom: 0px;
    margin-left: 550px;
}
</style>