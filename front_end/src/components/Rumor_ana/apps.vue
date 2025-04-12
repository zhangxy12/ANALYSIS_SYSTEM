<template>
    <div class="apps" style="height: 98%;">
        <div class="apps_top">
            <svg t="1741674154008" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6708" width="16" height="16" data-spm-anchor-id="a313x.search_index.0.i18.5dda3a812bOxfR"><path d="M569.7 96l-0.1 81.9c185.9 14.9 332.2 170.7 332.2 360.4 0 199.6-161.8 361.3-361.3 361.3-186.1 0-339.4-140.7-359.2-321.6H99c20.1 226.2 210.1 403.5 441.5 403.5 244.8 0 443.2-198.4 443.2-443.2 0-235-182.8-427.3-414-442.3zM123.2 470c0.6-193.3 152.9-350.9 344.1-359.8v-82c-236.5 9-425.5 203.3-426 441.8h81.9z" fill="#ffffff" p-id="6709"></path><path d="M139.9 577.9m-40.9 0a40.9 40.9 0 1 0 81.8 0 40.9 40.9 0 1 0-81.8 0Z" fill="#ffffff" p-id="6710"></path><path d="M569.6 136.9m-40.9 0a40.9 40.9 0 1 0 81.8 0 40.9 40.9 0 1 0-81.8 0Z" fill="#ffffff" p-id="6711"></path><path d="M41.4 470c0 22.6 18.3 41 41 41H471c22.6 0 41-18.3 41-41 0-22.6-18.3-41-41-41H82.4c-22.6 0.1-41 18.4-41 41z" fill="#ffffff" p-id="6712"></path><path d="M471 28.2c-22.6 0-41 18.3-41 41V470c0 22.6 18.3 41 41 41 22.6 0 41-18.3 41-41V69.2c0-22.6-18.3-41-41-41z" fill="#ffffff" p-id="6713"></path></svg>
            <span class="stat-title">发布占比</span>
      <div class="radio">
        <!-- <el-radio-group v-model="radio">
          <el-radio :label="1">天</el-radio>
          <el-radio :label="2">月</el-radio>
        </el-radio-group> -->
      </div>
    </div> 
    <div class="chart-container">
          <div ref="sourceChart" style="width: 100%; height: 230px;"></div>
        </div>
      <!-- <div id="pieChart" ref="pieChartRef" style="width: 600px; height: 300px;"></div> -->
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import * as echarts from 'echarts';
  
  export default {
    name: 'SourceChartComponent',
    data() {
      return {
        results: {},
      };
    },
    mounted() {
      this.fetchData();
    },
    methods: {
      async fetchData() {
        try {
          const key = this.$route.query.key;
          const response = await axios.get(`/rumor/rumorAnalyse?key=${key}`);
          this.results = response.data.data;
          console.log(this.results);
          this.renderChart();
        } catch (error) {
          console.error('获取数据出错:', error);
        }
      },
      renderChart() {
        // 计算各平台数量
        const renminCount = this.results.renmin? this.results.renmin.length : 0;
        const weiboCount = this.results.weibo.result? this.results.weibo.result.length : 0;
        const tiebaCount = this.results.tieba? this.results.tieba.length : 0;
        const wechatCount = this.results.wechat? this.results.wechat.length : 0;
  
        const total = renminCount + weiboCount + tiebaCount + wechatCount;
        console.log(this.$refs.sourceChart);
        if (this.$refs.sourceChart) {
          const sourceChart = echarts.init(this.$refs.sourceChart);
          const sourceOption = {
            title: {
              text: '信息来源占比',
              left: 'center',
              top: 'center',
              textStyle: {
                fontSize: 16,
                fontWeight: 'normal',
                color: '#fff',
              },
            },
            tooltip: {
              trigger: 'item',
              formatter: '{a} <br/>{b}: {c} ({d}%)',
            },
            series: [
              {
                name: '信息来源',
                type: 'pie',
                radius: '50%',
                data: [
                  { value: renminCount, name: '人民网' },
                  { value: weiboCount, name: '微博' },
                  { value: tiebaCount, name: '贴吧' },
                  { value: wechatCount, name: '微信' },
                ],
                color: ['#a4e2c6', '#48c0a3', '#549688', '#1685a9'],
                emphasis: {
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)',
                  },
                },
              },
            ],
          };
          sourceChart.setOption(sourceOption);
        } else {
          console.error('sourceChart element not found');
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .apps {
    
    color: #ffffff;
    /* border-radius: 8px; */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
    border: 2px solid #669ef3a5; /* 深色边框 */
    border-radius: 10px;
    box-sizing: border-box;
  }
  
  .apps_top {
    text-align: center;
    align-items: center;
    margin-bottom: 10px;
    font-size: 18px;
    font-weight: 600;
    color:#ffffff;
    
  }
  </style>