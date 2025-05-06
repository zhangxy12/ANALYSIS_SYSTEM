<template>
  <div class="relation_graph" style="height: 100%;">
    <div class="relation_graph_top" @click="ToPersonList">
      <svg class="icon" aria-hidden="true">
        <use xlink:href="#icon-wangluoguanxitu"></use>
      </svg>
      <span>关系图</span>
    </div>
    <div id="show_graph" style=" height: 250px;"></div>
  </div>
</template>

<script>
export default {
  name: "relation_graph",
  data() {
    return {
      categories: [
        {
          name: "   ",
          color: "#00FFFF",
        },
        // {
        //   name: "水军",
        // },
      ],
    };
  },
  methods: {
    myRelationGraph(id) {
      let option;
      let myChart = this.$echarts.init(document.getElementById("show_graph"));
      myChart.showLoading();
      this.$axios.get("relation_graph?tag_task_id=" + id).then((res) => {
        console.log(res.data.data);
        let nodes = res.data.data.nodes_list;
        for (let index in nodes) {
          nodes[index].id = index;
        }
        let links = res.data.data.links_list;
        links.forEach((link) => {
          for (let node of nodes) {
            if (link.source == node.name) {
              link.source = node.id;
              node.show = true;
            }
            if (link.target == node.name) {
              link.target = node.id;
              node.show = true;
            }
          }
        });
        let newNodes = [];
        for (let n in nodes) {
          if (nodes[n].show) {
            newNodes.push(nodes[n]);
          }
        }
        console.log(newNodes);
        console.log(links);
        myChart.hideLoading();
        nodes.forEach(function (node) {
          node.label = {
            show: node.value > 10,
            color: '#ffffff',
          };
        });
        option = {
          // title: {
          //   text: "用户关系图",
          //   top: "top",
          //   left: "left",
          // },
          tooltip: {},
          legend: [
            {
              data: this.categories.map(function (a) {
                return a.name;
              }),
            },
          ],
          animationDuration: 1500,
          animationEasingUpdate: "quinticInOut",
          series: [
            {
              name: "用户关系图",
              type: "graph",
              layout: "force",
              data: newNodes,
              links: links,
              categories: this.categories,
              roam: true,
              label: {
                position: "right",
                formatter: "{b}",
                color: "#ffffff", // 设置标签文字为白色
              },
              lineStyle: {
                color: "#00FFFF", // 青色的线条颜色
                curveness: 0.3,
              },
              emphasis: {
                focus: "adjacency",
                lineStyle: {
                  width: 10,
                  color: "#00FFFF",
                },
                nodeStyle: {
                  color: "#00FFFF", // 青色的线条颜色
                  borderWidth: 3,
                  shadowBlur: 20,
                  shadowColor: 'rgba(0,0,0,0.3)', // 增加阴影效果
                },
                itemStyle: {
                color: "#00FFFF", // 青色的节点颜色
              },
              },
            },
          ],
        };
        myChart.setOption(option);
      });
      option && myChart.setOption(option);
    },
    ToPersonList() {
      this.$router.push({
        path: "/person_list",
        query: {
          tag_task_id: this.tid,
        },
      });
    },
  },
  mounted() {
    let res = Array.from(new Array(5), () => []);
    console.log(res);
    this.$bus.$on("send_tag_task_id", (tag_task_id) => {
      console.log("这里是关系图组件,收到了数据:", tag_task_id);
      this.tid = tag_task_id;
      this.myRelationGraph(tag_task_id);
    });
  },
  beforeDestroy() {
    this.$bus.$off("send_tag_task_id");
  },
};
</script>

<style scoped>
.relation_graph_top {
  margin-top: 0px;
}

.relation_graph {
  border: 2px solid #fefeff6a; /* 深色边框 */
  border-radius: 10px;
  background-color:rgba(254, 254, 255, 0);
  position: relative;

  width: 100%;
  height: 100%;
  /* margin-bottom: 5px; */
  cursor: pointer; /* 改变鼠标指针为手形 */
  color: #ffffff;
  border: 2px solid #669ef3a5; /* 深色边框 */
  border-radius: 10px;
  
  box-sizing: border-box;
  background:rgba(52, 110, 173, 0); /* 背景颜色 */
  box-shadow: 0 0 15px rgba(233, 229, 238, 0.304), 0 0 25px rgba(63, 154, 87, 0.4); /* 外阴影 */
}

.relation_graph:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); /* 鼠标悬浮时加上阴影效果 */
}

#show_graph {
  height: 90%;
  width: 90%;
  
}
</style>
