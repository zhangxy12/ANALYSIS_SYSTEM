<template>
  <div class="post" style="height: 330px">
    <!-- <div class="post_top">
      <svg t="1741674708658" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="11844" width="32" height="32"><path d="M187.35104 567.66464c0-0.57344 0.57344-2.2528 1.10592-3.8912 16.87552-84.62336 55.00928-174.20288 111.65696-174.20288 19.61984 0 53.37088 21.13536 101.86752 120.2176 8.72448 18.35008 17.408 37.2736 25.06752 55.0912 40.30464 90.68544 81.67424 184.7296 179.73248 184.7296 3.2768 0 7.08608 0 10.89536-0.53248 130.17088-8.88832 163.4304-152.49408 196.07552-291.6352 41.94304-180.8384 133.98016-229.25312 181.37088-229.25312V161.3824c-45.75232 0-95.8464 23.3472-136.72448 64.512-50.09408 50.09408-86.58944 122.4704-108.38016 215.94112-38.66624 165.84704-65.90464 235.9296-136.72448 240.4352-57.7536 3.8912-85.48352-52.87936-126.89408-145.28512a1740.3904 1740.3904 0 0 0-26.13248-57.30304c-35.4304-72.9088-85.52448-156.95872-160.1536-156.95872-117.10464 0-161.792 159.17056-175.9232 227.65568l-0.53248 1.6384 31.5392 7.7824 32.1536 7.7824z" fill="#ffffff" p-id="11845"></path><path d="M68.07552 956.66176V0.57344H2.70336v1022.85312h1020.76416v-66.7648z" fill="#ffffff" p-id="11846"></path></svg>
      <span class="stat-title"> 发布统计</span>
      <div class="radio">
        <el-radio-group v-model="radio">
          <el-radio :label="1">天</el-radio>
          <el-radio :label="2">月</el-radio>
        </el-radio-group>
      </div>
    </div> -->
    <div id="lineChart" ref="timeLineChart" style="width: 100%; height: 100%;"></div>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: "post",
  data() {
    return {
      key: '',
      timeData: {}
    };
  },
  mounted() {
    this.key = this.$route.query.key;
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get(`/rumor/rumorPost?key=${encodeURIComponent(this.key)}`);
        console.log(response);
        if (response.data.code === 0) {
          const data = this.filterOneYearData(response.data.data);
          this.timeData = this.calculateTimeData(data);
          this.renderChart();
        }
      } catch (error) {
        console.error('获取数据出错:', error);
      }
    },
    filterOneYearData(data) {
      const oneYearAgo = new Date();
      oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

      const filteredData = {
        renmin_date_count: {},
        tieba_date_count: {},
        wechat_date_count: {},
        weibo_date_count: {}
      };

      const platforms = ['renmin_date_count', 'tieba_date_count', 'wechat_date_count', 'weibo_date_count'];
      platforms.forEach(platform => {
        for (const [date, count] of Object.entries(data[platform])) {
          const currentDate = new Date(date);
          if (currentDate >= oneYearAgo) {
            filteredData[platform][date] = count;
          }
        }
      });

      return filteredData;
    },
    calculateTimeData(data) {
      const renminData = data.renmin_date_count;
      const tiebaData = data.tieba_date_count;
      const wechatData = data.wechat_date_count;
      const weiboData = data.weibo_date_count;

      const allDates = new Set();
      for (const platformData of [renminData, tiebaData, wechatData, weiboData]) {
        for (const date in platformData) {
          allDates.add(date);
        }
      }
      const labels = Array.from(allDates).sort();

      return {
        labels: labels,
        renmin: labels.map(date => renminData[date] || 0),
        tieba: labels.map(date => tiebaData[date] || 0),
        wechat: labels.map(date => wechatData[date] || 0),
        weibo: labels.map(date => weiboData[date] || 0)
      };
    },
    renderChart() {
      const timeLineChart = echarts.init(this.$refs.timeLineChart);
      const timeLineOption = {
        title: {
          text: '发布时间趋势',
          left: 'center',
          top: '3%',
          bottom: '5%',
          textStyle: {
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['人民网', '微博', '贴吧', '微信'],
          top: '17%',
          textStyle: {
            color: '#fff'
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.timeData.labels,
          axisLabel: {
            color: '#fff'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value} 条',
            color: '#fff'
          },
          axisTick: {
            alignWithLabel: true
          },
          minInterval: 1 // 设置最小刻度间隔为1，确保显示整数
        },
        grid: {
          top: '30%',
          left: '10%',
          right: '8%',
          bottom: '20%'
        },
        series: [
          {
            name: '人民网',
            type: 'line',
            data: this.timeData.renmin,
            smooth: true,
            color: '#a4e2c6',
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(164, 226, 198, 0.5)' // 与折线颜色相同，半透明
                  },
                  {
                    offset: 1,
                    color: 'rgba(164, 226, 198, 0)' // 完全透明
                  }
                ]
              }
            }
          },
          {
            name: '微博',
            type: 'line',
            data: this.timeData.weibo,
            smooth: true,
            color: '#48c0a3',
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(72, 192, 163, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(72, 192, 163, 0)'
                  }
                ]
              }
            }
          },
          {
            name: '贴吧',
            type: 'line',
            data: this.timeData.tieba,
            smooth: true,
            color: '#C0FF3E',
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(84, 150, 136, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(84, 150, 136, 0)'
                  }
                ]
              }
            }
          },
          {
            name: '微信',
            type: 'line',
            data: this.timeData.wechat,
            smooth: true,
            color: '#ffffff',
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(22, 133, 169, 0.5)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(22, 133, 169, 0)'
                  }
                ]
              }
            }
          }
        ]
      };
      timeLineChart.setOption(timeLineOption);
    }
  }
};
</script>

<style scoped>
  .post {
    color: #ffffff;
    /* border-radius: 8px; */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
    border: 2px solid #669ef3a5; /* 深色边框 */
    border-radius: 10px;
    box-sizing: border-box;
  }

  .post_top {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }

  .stat-title {
    margin-right: 10px;
    font-size: 18px;
    font-weight: 600;
  }

  .radio {
    margin-left: auto;
  }
</style>