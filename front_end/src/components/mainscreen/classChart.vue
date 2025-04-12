<template>
    <div>
      <h2><i class="fa fa-tags"></i>    文本分类</h2>
      <div ref="chart" style="width: 99%; height: 180px;"></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import * as echarts from 'echarts';
  
  export default {
    data() {
      return {
        chart: null,
        config: {
          backgroundColor: 'transparent',
          // title: {
          //   text: '文本分类',
          //   left: 'center',
          //   top: '12',
          //   bottom:'20',
          //   textStyle: {
          //     color: '#fff',
          //     fontSize: 18,
          //     fontWeight: '700'
          //   }
          // },
          tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} ({d}%)'
          },
          legend: {
            show: false
          },
          series: [
            {
              name: '分类统计',
              type: 'pie',
              radius: ['50%', '70%'],
              center: ['50%', '50%'], // 图表居中
              top:'10',
              avoidLabelOverlap: false,
              label: {
                show: true, // 显示标签
                position: 'outside', // 标签显示在外部
                formatter: '{b}: {d}%', // 标签格式：分类名称 + 百分比
                color: '#fff', // 标签文字颜色
                fontSize: 12
              },
              labelLine: {
                show: true, // 显示标签线
                length: 10, // 第一段线长度
                length2: 20, // 第二段线长度
                lineStyle: {
                  color: '#fff' // 标签线颜色
                }
              },
              emphasis: {
                label: {
                  show: true,
                  fontSize: 14,
                  fontWeight: 'bold'
                }
              },
              data: [],
              itemStyle: {
                borderColor: '#0A2E5D',
                borderWidth: 1,
                shadowBlur: 20,
                shadowColor: 'rgba(0, 255, 255, 0.8)' // 发光效果
              },
              color: [
                '#1f78b4', // 深蓝
                '#6baed6', // 中蓝
                '#9ecae1', // 浅蓝
                '#c6dbef', // 更浅蓝
                '#3182bd', // 深蓝2
                '#6baed6', // 中蓝2
                '#9ecae1', // 浅蓝2
                '#c6dbef', // 更浅蓝2
                '#08519c', // 深蓝3
                '#2171b5'  // 中蓝3
              ]
            },
            {
              type: 'pie',
              radius: ['50%', '70%'],
              center: ['50%', '50%'], // 图表居中
              silent: true,
              top:'10',
              label: { show: false },
              data: [{ value: 1, itemStyle: { color: 'rgba(255,255,255,0.1)' } }],
              itemStyle: {
                color: 'transparent',
                borderWidth: 2,
                borderColor: 'rgba(255,255,255,0.2)'
              }
            }
          ]
        }
      };
    },
    mounted() {
      this.initChart();
      this.fetchData();
    },
    methods: {
      initChart() {
        this.chart = echarts.init(this.$refs.chart);
        this.chart.setOption(this.config);
      },
      async fetchData() {
        try {
          const response = await axios.get('/main/all_hot_class');
          if (response.data.code === 0) {
            const classCount = response.data.data;
            const data = Object.entries(classCount).map(([category, count]) => ({
              value: count,
              name: category
            }));
            this.config.series[0].data = data;
            this.chart.setOption(this.config);
          } else {
            console.error('请求失败:', response.data.message);
          }
        } catch (error) {
          console.error('发生错误:', error);
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
    margin-left: 150px;
}
  /* 可以根据需要添加更多样式 */
  </style>