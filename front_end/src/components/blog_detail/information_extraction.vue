<template>
  <div class="information_extraction">
    <div class="information_extraction_title">信息抽取</div>
    <div id="information_extraction" style="height: 80%;"></div>
  </div>
</template>

<script>
export default {
  name: "information_extraction",
  data() {
    return {
      timer: "",
      myChart: "",
      information_extraction_data: {
        triples: [], // 存储提取的三元组
      },
    };
  },
  methods: {
    getInformationExtraction() {
      let query = this.$route.query;
      this.$axios
        .get(
          "comment/knowledge_graph?tag_task_id=" +
            query.tag_task_id +
            "&weibo_id=" +
            query.weibo_id
        )
        .then((res) => {
          this.information_extraction_data = res.data.data;
          console.log(res.data.data);
          this.myInformationExtraction(); // 调用绘图方法
        });
    },

    // 绘制知识图谱图表
    myInformationExtraction() {
      let option;

      if (this.myChart != null && this.myChart !== "" && this.myChart !== undefined) {
        this.myChart.dispose(); // 清理现有的图表实例
      }

      // 基于准备好的dom，初始化echarts实例
      this.myChart = this.$echarts.init(document.getElementById("information_extraction"));

      // 获取三元组数据
      const triples = this.information_extraction_data;

      // 用于存储节点和边
      const nodes = [];
      const links = [];
      const nodeIds = {}; // 用于记录已存在的节点

      // 遍历三元组数据并处理每个三元组
      triples.forEach((triple, index) => {
        // 如果subject、predicate、object是数组，处理每个元素
        const subjects = Array.isArray(triple.subject) ? triple.subject : [triple.subject];
        const predicates = Array.isArray(triple.predicate) ? triple.predicate : [triple.predicate];
        const objects = Array.isArray(triple.object) ? triple.object : [triple.object];

        subjects.forEach(subject => {
          if (!nodeIds[subject]) {
            nodeIds[subject] = nodes.length;
            nodes.push({
              id: subject,
              name: subject,
              category: 0,
              label: {
                show: true,
                position: "inside",
                formatter: "{b}",
                fontSize: 14,
                color: '#ffffff',
              },
              itemStyle: {
                color: this.getRandomColor(),
                opacity: 0.9,
                borderRadius: '50%',
                borderColor: '#ffffff',
                borderWidth: 2,
              },
              symbolSize: 50,
            });
          }
        });

        objects.forEach(object => {
          if (!nodeIds[object]) {
            nodeIds[object] = nodes.length;
            nodes.push({
              id: object,
              name: object,
              category: 2,
              label: {
                show: true,
                position: "inside",
                formatter: "{b}",
                fontSize: 14,
                color: '#ffffff',
              },
              itemStyle: {
                color: this.getRandomColor(),
                opacity: 0.9,
                borderRadius: '50%',
                borderColor: '#ffffff',
                borderWidth: 2,
              },
              symbolSize: 50,
            });
          }
        });

        // 创建边连接subject和object，边上标注predicate
        subjects.forEach(subject => {
          predicates.forEach(predicate => {
            objects.forEach(object => {
              links.push({
                source: subject,
                target: object,
                label: {
                  show: true,
                  formatter: predicate, // 显示predicate作为边的label
                  fontSize: 12,
                  color: '#ffffff',
                },
                lineStyle: {
                  color: "#aaa",
                  width: 1,
                  curveness: 0.3,
                },
              });
            });
          });
        });
      });

      // 图表的配置项
      option = {
        tooltip: {
          show: true,
        },
        animation: true,
        series: [
          {
            type: "graph",
            layout: "force",
            roam: true,
            symbolSize: 50,
            label: {
              show: true,
              position: "inside",
              formatter: "{b}",
              fontSize: 14,
              color: '#ffffff',
            },
            edgeSymbol: ["none", "arrow"],
            edgeSymbolSize: [4, 10],
            force: {
              repulsion: 200,
              edgeLength: 150,
            },
            data: nodes,
            links: links,
            categories: [
              { name: "Entity" },
              { name: "Predicate" },
              { name: "Object" },
            ],
            emphasis: {
              focus: "adjacency",
            },
            lineStyle: {
              color: "#aaa",
              width: 1,
              curveness: 0.3,
            },
          },
        ],
      };

      this.myChart.setOption(option);
    },

    // 随机颜色生成函数（浅色系）
    getRandomColor() {
      const letters = '89ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 6)];
      }
      return color;
    }
  },

  mounted() {
    this.getInformationExtraction();
    this.timer = setInterval(() => {
      this.myInformationExtraction(); // 每5秒更新图表
    }, 20000); // 定时更新图表
  },

  beforeDestroy() {
    clearInterval(this.timer);
    this.timer = null;
  },
};
</script>

<style scoped>
.information_extraction {
  position: relative;
  width: 100%;
  height: 100%;
  top: 5%;
  background-color: #ffffff00;
  color: #ffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
  border: 2px solid #669ef3a5; /* 深色边框 */
  border-radius: 10px;
  box-sizing: border-box;
  backdrop-filter: blur(10px); /* 添加磨砂玻璃效果 */
  -webkit-backdrop-filter: blur(10px); /* Safari 兼容 */
  overflow: hidden;
}

.information_extraction_title {
  margin: 10px 20px;
  padding: 5px;
  font-weight: 600;
  letter-spacing: 1px;
}

#information_extraction {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>
