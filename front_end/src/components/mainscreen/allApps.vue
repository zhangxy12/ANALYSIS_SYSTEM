<template>
  <div>
    <h2><svg t="1741847536282" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="13774" width="16" height="16"><path d="M496.64 870.4c-98.816 0-185.856-13.824-245.76-39.424-68.608-25.6-107.52-65.536-107.52-109.056V316.928c0-22.528 9.216-44.032 27.648-62.464 17.92-18.944 44.032-35.328 79.872-51.2 59.392-25.6 146.944-39.424 245.76-39.424s186.368 13.824 245.76 39.424l3.072 1.024c34.816 15.36 59.904 31.744 77.312 49.152 18.432 18.944 27.648 39.936 27.648 62.464V721.92c0 41.472-39.936 81.92-107.52 109.056-59.904 25.6-147.456 39.424-246.272 39.424z m-300.032-153.088c0 13.312 7.68 26.624 23.04 38.4 15.872 12.288 39.424 23.04 69.12 31.232 67.584 19.456 140.288 30.208 206.336 30.208h1.536c80.896 0 158.208-11.264 207.36-30.208 30.208-10.752 53.248-22.528 69.632-34.816 15.36-11.776 23.04-23.552 23.04-34.816v-57.856l-9.216 4.608c-36.352 18.432-65.024 32.768-111.104 44.544-64 14.848-124.416 22.016-183.808 22.016-58.368 0-123.904-8.192-179.712-22.016-40.96-11.264-70.144-25.6-103.424-43.008l-12.288-6.144-0.512 57.856z m0-139.264c0 13.312 7.68 26.624 23.04 38.4 15.872 12.288 39.424 23.04 69.12 31.232 68.608 19.456 142.336 30.208 207.872 30.208 68.608 0 145.92-11.264 207.872-30.208h0.512c29.696-8.704 52.736-18.944 68.608-31.232 15.36-11.776 23.04-24.576 23.04-38.4v-57.856c-4.096 2.048-7.68 4.096-11.264 5.632-35.328 17.92-63.488 32.256-104.448 43.52-64 14.848-124.416 22.016-183.808 22.016-59.904 0-120.32-7.168-183.808-22.016-41.472-11.264-69.12-25.6-104.448-43.52-3.584-2.048-7.68-3.584-11.264-5.632l-1.024 57.856z m92.672-69.632c68.096 19.456 141.824 30.208 207.872 30.208 68.608 0 145.92-11.264 207.872-30.208 68.096-24.576 92.672-49.664 92.672-65.024v-45.056c-11.776 5.12-23.04 10.24-33.28 15.36-25.6 12.288-50.176 24.064-82.944 30.208-64 14.848-123.904 22.016-183.808 22.016s-119.808-7.168-183.808-22.016c-32.768-6.144-56.832-17.92-82.944-30.208-10.752-5.12-21.504-10.24-33.792-15.36v40.96c0 11.264 7.68 23.04 23.04 34.816s38.912 23.552 69.12 34.304zM496.64 217.088c-81.408 0-151.552 10.24-203.264 30.208-58.88 20.992-92.672 46.592-92.672 69.632 0 11.776 7.68 23.552 21.504 34.304 15.872 12.288 39.936 22.528 70.656 30.72C358.4 407.04 439.808 412.16 496.64 412.16c79.36 0 153.088-10.752 203.264-30.208 30.72-8.192 54.784-18.432 70.656-30.72 13.824-10.752 21.504-22.528 21.504-34.304 0-11.264-7.68-23.04-23.04-34.816-15.872-12.288-39.424-24.064-69.632-34.816-59.904-18.944-137.728-30.208-202.752-30.208z" p-id="13775" fill="#ffffff"></path></svg>   多平台来源统计（千）</h2>
  
  <div class="bar-chart-container">
    
    <div ref="barChart" style="width: 100%; height: 150px; position: relative;"></div>
  </div>
</div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  data() {
    return {
      sourceData: {} // 存储从后端获取的数据
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get('/main/all_apps');
        console.log(response);
        if (response.data.code === 0) {
          this.sourceData = response.data.data;
          this.initChart();
        } else {
          console.error('请求失败:', response.data.message);
        }
      } catch (error) {
        console.error('发生错误:', error);
      }
    },
    initChart() {
      const chart = echarts.init(this.$refs.barChart);

      // 处理数据
      let dataArray = Object.entries(this.sourceData).map(([key, value]) => {
        return {
          name: this.getChineseName(key),
          value: value
        };
      });

      // 从大到小排序
      dataArray.sort((a, b) => a.value - b.value);

      const categories = dataArray.map(item => item.name);
      const values = dataArray.map(item => item.value);

      // 定义四个 app 的不同颜色
      const colors = ['#1f78b4', '#6baed6', '#9ecae1', '#c6dbef'];

      const option = {
        // title: {
        //   text: '多平台来源统计',
        //   top: '10px',
        //   left: 'center',
        //   textStyle: {
        //     color: '#fff',
        //     fontSize: 16,
        //     fontWeight: 'bold'
        //   }
        // },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '5%',
          top:'7%',
          containLabel: true,
          show: false // 不显示网格
        },
        xAxis: {
          type: 'value',
          axisLabel: {
            show: false // 不显示横坐标数字
          },
          axisLine: {
            show: false // 不显示横坐标轴线
          },
          splitLine: {
            show: false // 不显示网格线
          }
        },
        yAxis: {
          type: 'category',
          data: categories,
          axisLabel: {
            color: '#fff'
          },
          axisLine: {
            lineStyle: {
              color: '#fff'
            }
          },
          splitLine: {
            show: false // 不显示网格线
          }
        },
        series: [
          {
            name: '来源数量',
            type: 'bar',
            barWidth: 12, // 调整条形图的宽度，使其更细
            borderColor: '#ffffff',
            borderWidth: 1,
            top:'0',
            data: values,
            center: ['50%', '50%'], // 图表居中
            itemStyle: {
              color: (params) => colors[params.dataIndex % colors.length],
              shadowBlur: 10,
                shadowColor: 'rgba(0, 255, 255, 0.8)', // 发光效果
                barBorderRadius: [2, 5, 5, 2] // 设置条形的四个角的圆角半径，数值越大越圆
            },
            label: {
              show: true,
              position: 'right',
              color: '#fff'
            }
          }
        ]
      };

      chart.setOption(option);
    },
    getChineseName(key) {
      switch (key) {
        case 'wechat':
          return '微信';
        case 'weibo':
          return '微博';
        case 'renmin':
          return '人民网';
        case 'tieba':
          return '贴吧';
        default:
          return key;
      }
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

.bar-chart-container {
  width: 100%;
  height: 100%;
  background-color: #03040900; /* 深色背景 */
  padding: 2px;
  box-sizing: border-box;
}
</style>