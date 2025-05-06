<template>
  <div class="sentiment_ana">
    <div class="sentiment_ana_title">评论情感随时间变化</div>
    <div class="sentiment_ana_contents">
      <div class="sentiment_chart" ref="sentimentChart" style="height: 265px;"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: "sentiment_ana",
  data() {
    return {
      sentimentData: null
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
          // 获取情感分析数据
          this.sentimentData = res.data.data.data.sentiment_by_date;

          // 绘制折线图
          this.drawSentimentChart();
        })
        .catch(error => {
          console.error("获取评论情感分析失败:", error);
        });
    },
    drawSentimentChart() {
      if (!this.sentimentData) return;

      // 提取所有日期
      const dates = Object.keys(this.sentimentData).sort();

      // 提取不同情感类型
      const sentimentTypes = new Set();
      for (const date in this.sentimentData) {
        for (const sentiment in this.sentimentData[date]) {
          sentimentTypes.add(sentiment);
        }
      }

      // 构建每种情感的评论数数组
      const seriesData = [];
      sentimentTypes.forEach(sentiment => {
        const data = [];
        dates.forEach(date => {
          data.push(this.sentimentData[date][sentiment] || 0);
        });

        let areaColor;
        let chineseName;
        switch (sentiment) {
          case 'positive':
            chineseName = '积极';
            areaColor = 'rgba(54, 162, 235, 0.3)'; // 积极情感的颜色，蓝色系
            break;
          case 'neutral':
            chineseName = '中性';
            areaColor = 'rgba(255, 205, 86, 0.3)'; // 中性情感的颜色，黄色系
            break;
          case 'negative':
            chineseName = '消极';
            areaColor = 'rgba(255, 99, 132, 0.3)'; // 消极情感的颜色，红色系
            break;
          default:
            areaColor = 'rgba(153, 153, 153, 0.3)'; // 默认颜色
        }

        seriesData.push({
          name: chineseName,
          type: 'line',
          data: data,
          areaStyle: {
            color: areaColor
          },
          lineStyle: {
            color: areaColor.replace('0.3', '1') // 折线颜色与阴影颜色相同，但不透明
          }
        });
      });

      // 初始化 echarts 实例
      const chart = echarts.init(this.$refs.sentimentChart);

      // 配置项
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: Array.from(sentimentTypes).map(sentiment => {
            switch (sentiment) {
              case 'positive':
                return '积极';
              case 'neutral':
                return '中性';
              case 'negative':
                return '消极';
              default:
                return '其他';
            }
          }),
          textStyle: {
            color: '#fff' // 图例文字为白色
          }
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            color: 'white' // 设置横坐标的字体颜色为白色
          }
        },
        yAxis: {
          type: 'value',
          min: 0,
          axisLabel: {
            formatter: function (value) {
              return Math.round(value); // 确保纵坐标为整数
            },
            color: 'white' // 设置纵坐标的字体颜色为白色
          }
        },
        series: seriesData
      };

      // 使用配置项显示图表
      chart.setOption(option);
    }
  },
  mounted() {
    this.getComments();
  }
};
</script>

<style scoped>
.sentiment_ana {
  width: 100%;
  height: 100%;
}

.sentiment_ana_title {
  color: #ffffff;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 6px;
  margin-left: 10px;
}

.sentiment_ana_contents {
  width: 100%;
  height: calc(100% - 50px);
}

.sentiment_chart {
  width: 100%;
  height: 100%;
}
</style>