<template>
    <div class="chart-container">
      <!-- 饼状图 -->
      <div class="chart-box">
        <h3 class="chart-title">情感分布分析</h3>
        <div id="mood_pie_chart" class="chart"></div>
      </div>
  
      <!-- 折线图 -->
      <div class="chart-box">
        <h3 class="chart-title">情感随时间变化趋势</h3>
        <div id="mood_line_chart" class="chart"></div>
      </div>
    </div>
  </template>
  
  
  
  <script>
  export default {
    name: "MoodAnalysis",
    data() {
      return {
        moodData: {}, // 存储情感分析数据
        myChartPie: null, // 饼状图实例
        myChartLine: null, // 折线图实例
      };
    },
    methods: {
      // 获取情感分析数据并绘制饼状图和折线图
      getMoodData(tag_task_id) {
        this.$axios.get(`/mood_wx?tag_task_id=${tag_task_id}`).then((res) => {
          const data = res.data.data.data; // 获取情感分析结果
          this.moodData = data;
        console.log(data);
          // 绘制情感分布饼状图
          const sentimentCounts = data.total_sentiment;
          const pieData = [
            { value: sentimentCounts.positive, name: "积极" },
            { value: sentimentCounts.neutral, name: "中性" },
            { value: sentimentCounts.negative, name: "消极" }
          ];
  
          this.drawPieChart(pieData);
  
          // 绘制情感随时间变化折线图
          const sentimentByDate = data.sentiment_by_date;
          const dates = Object.keys(sentimentByDate);
          const positiveCounts = dates.map(date => sentimentByDate[date].positive);
          const neutralCounts = dates.map(date => sentimentByDate[date].neutral);
          const negativeCounts = dates.map(date => sentimentByDate[date].negative);
  
          const lineData = {
            dates,
            positive: positiveCounts,
            neutral: neutralCounts,
            negative: negativeCounts
          };
  
          this.drawLineChart(lineData);
        });
      },
  
      // 绘制饼状图
        drawPieChart(data) {
        if (this.myChartPie) {
            this.myChartPie.dispose();
        }
        this.myChartPie = this.$echarts.init(document.getElementById("mood_pie_chart"));

        const option = {
            tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)'
            },
            legend: {
            orient: 'vertical',
            left: 'left',
            data: ['消极', '积极', '中性'],
            textStyle: {
                color: '#fff' // 图例文字为白色
            }
            },
            series: [
            {
                name: '情感分布',
                type: 'pie',
                radius: '50%',
                data: data,
                emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
                },
                label: {
                normal: {
                    show: false,
                    position: 'center',
                    formatter: '{b}\n{d}%',
                    // textStyle: {
                    // fontSize: 16,
                    // fontWeight: 'bold',
                    // color: '#4a4a4a'
                    // }
                }
                }
            }
            ]
        };
        this.myChartPie.setOption(option);
        },
        
      // 绘制折线图
      drawLineChart(data) {
        if (this.myChartLine) {
          this.myChartLine.dispose();
        }
        this.myChartLine = this.$echarts.init(document.getElementById("mood_line_chart"));
  
        const option = {
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: [ '消极','积极', '中性'],
            textStyle: {
                color: '#fff' // 图例文字为白色
            }
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: data.dates,
            axisLabel: {
                color: "white", // 设置横坐标的字体颜色为白色
            },
          },
          yAxis: {
            type: 'value',
            axisLabel: {
                color: "white", // 设置横坐标的字体颜色为白色
            },
          },
          series: [
            {
              name: '消极',
              type: 'line',
              data: data.negative,
              areaStyle: {}
            },
            {
              name: '积极',
              type: 'line',
              data: data.positive,
              areaStyle: {}
            },
            {
              name: '中性',
              type: 'line',
              data: data.neutral,
              areaStyle: {}
            },
            
          ]
        };
        this.myChartLine.setOption(option);
      }
    },
    mounted() {
    this.$bus.$on("send_tag_task_id", (tag_task_id) => {
      console.log("接收到话题任务ID:", tag_task_id);
      this.getMoodData(tag_task_id); // 获取情感分析数据
    });
    },
    beforeDestroy() {
        this.$bus.$off("send_tag_task_id");
      if (this.myChartPie) {
        this.myChartPie.dispose();
      }
      if (this.myChartLine) {
        this.myChartLine.dispose();
      }
    }
  };
  </script>
  
  <style scoped>
 /* 页面容器 */
.chart-container {
  width: 100%;
  height:62vh;
  margin-top: -120px;
  
  position: relative;
  font-family: Arial, sans-serif;
  background-color: #f9f9f900;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  
  box-sizing: border-box; /* 确保 padding 不影响容器大小 */
  color: white; /* 所有字体颜色为白色 */
}

/* 单个图表及标题的包裹盒子 */
.chart-box {
    
  position: relative;
  width: 100%;
  height: 100%;
  border: 2px solid #4aaafac3; /* 深色边框 */
  border-radius: 10px;
  box-shadow: 0 0 15px rgba(233, 229, 238, 0.304), 0 0 25px rgba(63, 154, 87, 0.4); /* 外阴影 */
  margin-bottom: 10px;
}

/* 标题样式 */
.chart-title {
  position: absolute;
  top: 0px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 13px;
  font-weight: bold;
  text-align: center;
  background-color: #3e3e3e00; 
  padding: 0px;
  color: #fff; /* 白色字体 */
  z-index: 1; /* 确保标题在图表内容之上 */
}

/* 设置图表容器 */
.chart {
  margin-top: 27px;
  width: 100%;
  height: 90%;
  background-color: #ffffff00;
  border-radius: 8px;
}

/* 控制图表在不同屏幕上的适配 */
@media screen and (max-width: 768px) {
  .chart-container {
    padding: 10px; /* 保持父容器内边距 */
  }
  
  .chart-box {
    height: 250px !important; /* 小屏幕时设置固定高度 */
  }
}

@media screen and (min-width: 769px) {
  .chart-container {
    
  }

  .chart-box {
    height: 100% !important; /* 大屏幕时使用更大的高度比例 */
  }
}

  </style>