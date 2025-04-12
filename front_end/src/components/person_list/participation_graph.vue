<template>
  <div class="participation_graph">
    <div id="participation_graph"></div>
  </div>
</template>

<script>
export default {
  name: "participation_graph",
  methods: {
    getParticipationGraph() {
      let myChart = this.$echarts.init(
        document.getElementById("participation_graph")
      );
      let option;

      myChart.showLoading();
      let query = this.$route.query;
      this.$axios.get("retweet/detail_relation_graph?tag_task_id=" + query.tag_task_id).then((res) => {
          let graph = res.data.data;
        console.log(graph)
        myChart.hideLoading();
          graph.nodes_list.forEach(function (node) {
            node.label = {
              show: node.symbolSize > 5,
              color: "white", // 修改文字颜色为白色
            };
          });
           // 修改类别的颜色为浅色系
           graph.categories.forEach(function (category, index) {
            category.itemStyle = {
              color: ["#aed6f1", "#c5e1a5", "#ffcccb", "#f5e79e", "#d7bde2"][index % 5], // 定义浅色系配色
            };
          });
          option = {
            title: {
              text: "Participation Graph",
              textStyle: {
                color: "white", // 修改标题文字颜色为白色
              },
              left: "left",
            },
            tooltip: {
              textStyle: {
                color: "black", // 修改提示框文字颜色为白色
              },
            },
            legend: [
              {
                // selectedMode: 'single',
                data: graph.categories.map(function (a) {
                  return a.name;
                }),
                textStyle: {
                  color: "white", // 修改图例文字颜色为白色
                },
              },
            ],
            animationDuration: 1500,
            animationEasingUpdate: "quinticInOut",
            series: [
              {
                name: "Participation Graph",
                type: "graph",
                layout: "force",
                data: graph.nodes_list,
                links: graph.links_list,
                categories: graph.categories,
                roam: true,
                label: {
                  top: "10px",
                  position: "right",
                  formatter: "{b}",
                  color: "white", // 修改图节点文字颜色为白色
                },
                lineStyle: {
                  color: "source",
                  curveness: 0.3,
                },
                emphasis: {
                  focus: "adjacency",
                  lineStyle: {
                    width: 10,
                  },
                },
              },
            ],
          };
          myChart.setOption(option);
        });
      option && myChart.setOption(option);
    },
  },
  mounted() {
    this.getParticipationGraph();
  },
};
</script>

<style scoped>
#participation_graph {
  top: 20px;
  position: center;
  width: 1080px;
  height: 840px;
}
</style>
