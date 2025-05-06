<template>
  <div class="cloud_graph">
    <div class="cloud_graph_title">评论词云图</div>
    <div id="graph_word_cloud"></div>
  </div>
</template>

<script>
export default {
  name: "word_cloud",
  data() {
    return {
      timer: "",
      myChart: "",
      cloud_graph_data: "",
    };
  },
  methods: {
    getCloudGraph() {
      let query = this.$route.query;
      this.$axios.get("comment/cloud?tag_task_id="+query.tag_task_id+"&weibo_id="+query.weibo_id).then((res) => {
        this.cloud_graph_data = res.data.data.data;
        console.log(res.data.data.data)
      });
    },
    myWordCloud() {
      let option;
      if (
        this.myChart != null &&
        this.myChart != "" &&
        this.myChart != undefined
      ) {
        this.myChart.dispose(); //解决echarts dom已经加载的报错
      }
      // 基于准备好的dom，初始化echarts实例
      this.myChart = this.$echarts.init(
        document.getElementById("graph_word_cloud")
      );
      // 指定图表的配置项和数据
      option = {
        tooltip: {
          show: true,
        },
        series: [
          {
            type: "wordCloud",
            sizeRange: [10, 50], //文字范围
            //文本旋转范围，文本将通过rotationStep45在[-90,90]范围内随机旋转
            rotationRange: [-45, 90],
            rotationStep: 45,
            textRotation: [0, 45, 90, -45],
            //形状
            shape: "cardioid ",
            textStyle: {
              color: function () {
                //文字颜色的随机色
                return (
                  "rgb(" +
                  [
                  Math.round(Math.random() * 55 + 200), // 红色分量：200-255
                  Math.round(Math.random() * 55 + 200), // 绿色分量：200-255
                  Math.round(Math.random() * 55 + 200), // 蓝色分量：200-255
                  ].join(",") +
                  ")"
                );
              },
            },
            data: this.cloud_graph_data,
          },
        ],
      };
      this.myChart.setOption(option);
      // 使用刚指定的配置项和数据显示图表。
      option && this.myChart.setOption(option);
    },
  },
  mounted() {
    this.getCloudGraph();
    this.timer = setInterval(() => {
      this.myWordCloud();
    }, 5000);
  },
  beforeDestroy() {
    clearInterval(this.timer);
    this.timer = null;
  },
};
</script>

<style scoped>
.cloud_graph {
  position: absolute;
  width: 100%;
  height:43%;
  top: 1%;
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
.cloud_graph_title {
  margin: 10px 20px;
  padding: 5px;
  font-weight: 600;
  letter-spacing: 1px;
}
#graph_word_cloud {
  width: 90%;
  height: 80%;

}
</style>