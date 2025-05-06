<template>
  <div class="sentiment_trand">
    <div class="sentiment_trand_title">评论情感随时间变化</div>
    <div class="sentiment_trand_contents">
      <!-- ECharts图表容器 -->
      <div id="sentiment-chart" style="width: 100%; height: 100%;"></div>
    </div>
  </div>
</template>

<script>
// 引入echarts
import * as echarts from 'echarts';

export default {
  name: "sentiment_chart",
  data() {
    return {
      sentimentData: [], // 存储从后端获取的情感数据
    };
  },
  methods: {
  // 获取评论情感数据
  getSentimentData() {
    let query = this.$route.query;
    this.$axios
      .get(
        `comment/sentiment/trend?tag_task_id=${query.tag_task_id}&weibo_id=${query.weibo_id}`
      )
      .then((res) => {
        this.sentimentData = res.data.data; // 存储返回的情感数据
        this.drawChart(); // 获取数据后绘制图表
      });
  },

  // 绘制情感趋势图
  drawChart() {
    // 数据准备：按时间分类情感数据
    let timeData = [];
    let positiveData = [];
    let negativeData = [];
    let neutralData = [];

    // 先将数据按时间排序
    this.sentimentData.sort((a, b) => {
      return new Date(a.publish_time) - new Date(b.publish_time); // 按时间升序排序
    });

    this.sentimentData.forEach((item) => {
      timeData.push(item.publish_time); // 时间数据
      positiveData.push(item.sentiment_counts.positive); // 正面情感数量
      negativeData.push(item.sentiment_counts.negative); // 负面情感数量
      neutralData.push(item.sentiment_counts.neutral); // 中立情感数量
    });

    // 初始化ECharts实例
    let myChart = echarts.init(document.getElementById('sentiment-chart'));

    // 图表配置
    let option = {
      tooltip: {
        trigger: 'axis',
      },
      legend: {
        data: ['积极', '消极', '中立'],
        top: '10%',
        textStyle: {
            color: 'white', // 设置图例文字颜色为白色
          },
      },
      xAxis: {
        type: 'category',
        data: timeData, // X轴为时间
        axisLabel: {
          rotate: 45, // 时间标签倾斜显示
        color: "white", // 设置横坐标的字体颜色为白色
      },
      },
      yAxis: {
        type: 'value',
        name: '  ',
        color: "white",
        axisLabel: {
        color: "white", // 设置横坐标的字体颜色为白色
      },
      },
      series: [
        {
          name: '积极',
          type: 'line',
          data: positiveData,
          smooth: true, // 平滑曲线
          color: '#61de80db',
          areaStyle: { color: '#61de80db' }, // 填充区域颜色
        },
        {
          name: '消极',
          type: 'line',
          data: negativeData,
          smooth: true,
          color: '#ec80a6db',
          areaStyle: { color: '#ec80a6db' }, // 填充区域颜色
        },
        {
          name: '中立',
          type: 'line',
          data: neutralData,
          smooth: true,
          color: '#73e2eedb',
          areaStyle: { color: '#73e2eedb' }, // 填充区域颜色
        },
      ],
    };

    // 使用刚指定的配置项和数据显示图表
    myChart.setOption(option);
  },
},
  mounted() {
    this.getSentimentData(); // 组件加载时获取情感数据
  },
};
</script>

<style scoped>
.sentiment_trand {
  position: absolute;
  width: 100%;
  margin-left: 5px;
  top: 50%;
  height: 50%;
  background-color: #ffffff00;
  color:#ffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
  border: 2px solid #669ef3a5; /* 深色边框 */
  border-radius: 10px;
  box-sizing: border-box;
  
  backdrop-filter: blur(3px); /* 添加磨砂玻璃效果 */
  -webkit-backdrop-filter: blur(10px); /* Safari 兼容 */
  overflow: hidden;
}

.sentiment_trand_title {
  margin: 10px 20px;
  padding: 5px;
  font-weight: 600;
  letter-spacing: 1px;
}

.sentiment_trand_contents {
  width: 100%;
  height: 90%;
}
</style>
