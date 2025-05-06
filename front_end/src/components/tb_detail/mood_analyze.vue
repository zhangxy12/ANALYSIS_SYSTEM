<template>
  <div class="sentiment_ana">
    <div class="sentiment_ana_title">评论情感分析</div>
    <div class="sentiment_ana_contents">
      <div class="sentiment_chart" ref="sentimentChart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: "sentiment_ana",
  data() {
    return {
      sentimentData: {
        positive: 0,
        negative: 0,
        neutral: 0
      },
    };
  },
  methods: {
    // 获取当前博文的情感分析数据
    getComments() {
      let query = this.$route.query;
      // 对 URL 参数进行编码
      const encodedUrl = encodeURIComponent(query.url);
      this.$axios
        .get("comment/mood_tb", {
          params: {
            tag_task_id: query.tag_task_id,
            url: encodedUrl,
          }
        })
        .then((res) => {
          console.log(res);
          // 获取情感分析数据（百分比）
          const sentimentData = res.data.data.data.total_sentiment; 
          console.log(sentimentData);
          this.sentimentData.positive = sentimentData.positive * 100;  // 转换为百分比
          this.sentimentData.negative = sentimentData.negative * 100;
          this.sentimentData.neutral = sentimentData.neutral * 100;

          // 绘制饼状图
          this.drawSentimentChart();
        })
        .catch(error => {
          console.error("获取评论情感分析失败:", error);
        });
    },

    // 绘制饼状图
    drawSentimentChart() {
      const chartElement = this.$refs.sentimentChart;
      const myChart = echarts.init(chartElement);
      const option = {
        
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [
          {
            name: '情感分析',
            type: 'pie',
            radius: ['40%', '70%'],
            label: {
              position: 'outside',
              formatter: '{b}: {d}%'
            },
            itemStyle: {
          // 设置颜色
          normal: {
            color: function (params) {
              // 根据不同的 name 设置颜色
              if (params.name === '积极') {
                return '#73e2eedb'; 
              } else if (params.name === '消极') {
                return '#ec80a6db'; 
              } else if (params.name === '中立') {
                return '#61de80db'; 
              }
            }
          }
        },
            data: [
              { value: this.sentimentData.positive, name: '积极' },
              { value: this.sentimentData.negative, name: '消极' },
              { value: this.sentimentData.neutral, name: '中立' }
            ]
          }
        ]
      };
      myChart.setOption(option);
    },
  },
  mounted() {
    this.getComments();  // 在组件加载时获取评论情感分析数据
  },
};
</script>

<style scoped>
.sentiment_ana {
  position: absolute;
  width: 100%;
  height: 54%;
  top: 46%;
  background-color: #fefefe00;
  color:#ffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
  border: 2px solid #669ef3a5; /* 深色边框 */
  border-radius: 10px;
  box-sizing: border-box;
  
  backdrop-filter: blur(3px); /* 添加磨砂玻璃效果 */
  -webkit-backdrop-filter: blur(10px); /* Safari 兼容 */
  overflow: hidden;
}

.sentiment_ana_title {
  color:#ffff;
  margin-top: 20px;
  margin: 10px 20px;
  padding: 5px;
  font-weight: 600;
  letter-spacing: 1px;
}

.sentiment_ana_contents {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.sentiment_chart {
  width: 80%;
  height: 80%;
}
</style>
