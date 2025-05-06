<template>
  <div class="word_cloud" style="height: 38%;">
    <div class="word_cloud_top">
      <svg class="icon" aria-hidden="true">
        <use xlink:href="#icon-ciyuntu"></use>
      </svg>
      <span class="title_text"> 词云 </span>
    </div>
    <div class="show_words">
      <div id="chars_word_cloud" style=" width: 350px; height:220px ;"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "word_cloud",
  data() {
    return {
      timer: "",
      myChart: "",
      cloud_word: "",
    };
  },
  methods: {
    getCloudWord(id) {
      this.$axios.get("word_cloud?tag_task_id=" + id).then((res) => {
        console.log(res.data)
        this.cloud_word = res.data.data.data;
        this.myWordCloud(res.data.data.data);
      });
    },
    myWordCloud(data) {
      let option;
      if (
        this.myChart != null &&
        this.myChart != "" &&
        this.myChart != undefined
      ) {
        this.myChart.dispose(); //解决echarts dom已经加载的报错
      }
      this.myChart = this.$echarts.init(
        document.getElementById("chars_word_cloud")
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
            data: data,
          },
        ],
      };
      this.myChart.setOption(option);
      // 使用刚指定的配置项和数据显示图表。
      option && this.myChart.setOption(option);
    },
  },
  mounted() {

    this.$bus.$on("send_tag_task_id", (tag_task_id) => {
      console.log("这里是词云组件,收到了数据:", tag_task_id);
      this.getCloudWord(tag_task_id);
    });
    this.timer = setInterval(() => {
      this.myWordCloud(this.cloud_word);
    }, 5000);
  },
  beforeDestroy() {
    this.$bus.$off("send_tag_task_id");
    clearInterval(this.timer);
    this.timer = null;
  },
};
</script>

<style scpoed>
.word_cloud {
  border: 2px solid #fefeff6a; /* 深色边框 */
  border-radius: 10px;
  position: relative;
  width: 100%;
  height: 100%;
  background-color: #ffffff00;
  color: #ffffff;
  border: 2px solid #669ef3a5; /* 深色边框 */
  border-radius: 10px; 
  box-sizing: border-box;
  background: #346ead63; /* 背景颜色 */
  box-shadow: 0 0 15px rgba(233, 229, 238, 0.304), 0 0 25px rgba(63, 154, 87, 0.4); /* 外阴影 */
}
.word_cloud_top {
  margin-left: 1px;
}
.w_title {
  padding-top: 10px;
  height: 50px;
  text-align: center;
  font-size: 20px;
}
.show_words {
  width: 90%;
  height: 90%;
}
#chars_word_cloud {
  width: 330px;
  height: 150px;
  top: -10px;
  position: relative;
  margin-left: -10px;
}
.icon {
  position: relative;
  top: 8px;
}
</style>