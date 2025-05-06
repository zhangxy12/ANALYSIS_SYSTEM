<template> 
    <div class="post">
      <div class="post_top">
        <svg class="icon" aria-hidden="true">
          <use xlink:href="#icon-redu"></use>
        </svg>
        <span class="stat-title">人民网发布统计</span>
        <div class="radio">
          <el-radio-group v-model="radio">
            <el-radio :label="1">天</el-radio>
            <el-radio :label="2">月</el-radio>
          </el-radio-group>
        </div>
      </div>
      <div id="lineChart"></div>
    </div>
  </template>
  
  <script>
  export default {
    name: "post",
    data() {
      return {
        day_time: [], // 存储天数据
        day_count: [], // 存储天统计数据
        month_time: [], // 存储月数据
        month_count: [], // 存储月统计数据
        myChart: null, // ECharts实例
        radio: 1, // 默认选择 "天"
      };
    },
    watch: {
      radio(newradio) {
        this.changeline(newradio);
      },
    },
    methods: {
      // 获取话题发博时间统计数据
      getTopicData(id) {
        this.$axios.get(`/post_time_statistics_rm?tag_task_id=${id}`).then((res) => {
          const data = res.data.data.data;
        
          // 确保 data 和 data.day 不为空
            if (data && data.day) {
            // 更新天数据并排序
            this.day_time = Object.keys(data.day).sort((a, b) => a.localeCompare(b)); // 更精确地按日期升序排序
            this.day_count = this.day_time.map(time => data.day[time]);

            // 更新月数据并排序
            this.month_time = Object.keys(data.month).sort((a, b) => a.localeCompare(b));
            this.month_count = this.month_time.map(time => data.month[time]);

            // 默认显示天数据
            this.myLineChart(this.day_time, this.day_count);
            } else {
            console.error('数据格式不正确或缺少 day 数据');
            }
        });
      },
  
      // 渲染折线图
      myLineChart(time, count) {
        let option;
        if (this.myChart) {
          this.myChart.dispose(); // 解决echarts dom已加载的报错
        }
        this.myChart = this.$echarts.init(document.getElementById("lineChart"));
        option = {
          tooltip: {
            trigger: "axis",
            position: "center",
            axisPointer: {
              type: "cross",
              label: {
                backgroundColor: "#6a7985",
              },
            },
          },
          xAxis: {
            type: "category",
            data: time, // 已排序的时间数据
            axisLabel: {
              color: "white", // 设置横坐标的字体颜色为白色
            },
          },
          yAxis: {
            type: "value",
            axisLabel: {
              color: "white", // 设置纵坐标的字体颜色为白色
              formatter: (value) => {
                // 保证纵坐标只显示整数
                return Math.floor(value);
              },
            },
          },
          series: [
            {
              data: count,
              type: "line",
              smooth: true, // 平滑曲线
              lineStyle: {
                color: "#00FFFF", // 线条颜色
              },
              itemStyle: {
                color: "#00FFFF", // 点的颜色
              },
              areaStyle: {
                color: "rgba(0, 255, 255, 0.3)", // 背景区域的颜色
              },
            },
          ],
        };
        this.myChart.setOption(option);
      },
  
      // 根据选中的粒度切换折线图数据
      changeline(line) {
        if (line === 1) {
          // 显示天数据
          this.myLineChart(this.day_time, this.day_count);
        } else if (line === 2) {
          // 显示月数据
          this.myLineChart(this.month_time, this.month_count);
        }
      },
    },
  
    mounted() {
      // 监听父组件传递的 tag_task_id 并获取话题数据
      this.$bus.$on("send_tag_task_id", (tag_task_id) => {
        this.getTopicData(tag_task_id);
      });
    },
  
    beforeDestroy() {
      this.$bus.$off("send_tag_task_id");
    },
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
  
  .post:after {
    content: "";
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 12px;
    border: 3px solid rgba(255, 255, 255, 0); /* 外部细边框 */
    z-index: -1;
    animation: borderAnimation 4s ease-in-out infinite;
  }
  
  #lineChart {
    width: 105%; /* 使图表宽度适应父容器 */
    height: 270px; /* 调整图表高度，使其更加合适 */
    color: white;
  }
  
  .post_top {
    height: 10%;
    margin-left: 20px;
    display: flex;
    align-items: center;
    justify-content: flex-start; /* 使"发布统计"在左边 */
    color: white;
  }
  
  .post_top .radio {
    position: relative;
    margin-right: 20px;
    top: 5px;
    margin-left: auto; /* 使单选按钮组对齐到右边 */
    color: white;
  }
  
  .el-radio {
    z-index: 1;
    color: white;
  }
  
  @media (max-width: 768px) {
    .post {
      height: 10%; /* 在小屏幕上减小高度 */
    }
    #lineChart {
      height: 200px; /* 调整图表高度 */
    }
  }
  </style>
  