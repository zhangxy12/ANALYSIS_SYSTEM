<template>
  <div class="relation_graph" style="height: 98%; position: relative;">
    <div class="relation_graph_top_row" style="align-items: center;">
      <div class="relation_graph_top" @click="ToPersonList">
        <span class="clickable-text">
          <svg t="1741612751651" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3395" width="200" height="200">
            <path d="M824.888889 682.666667c-28.444444 0-56.888889 11.377778-79.644445 22.755555l-45.511111-45.511111c22.755556-34.133333 39.822222-73.955556 39.822223-119.466667 0-62.577778-28.444444-119.466667-73.955556-153.6l22.755556-45.511111h22.755555C790.755556 341.333333 853.333333 278.755556 853.333333 199.111111S790.755556 56.888889 711.111111 56.888889 568.888889 119.466667 568.888889 199.111111c0 51.2 28.444444 91.022222 62.577778 119.466667l-17.066667 39.822222c-22.755556-11.377778-45.511111-17.066667-73.955556-17.066667C432.355556 341.333333 341.333333 432.355556 341.333333 540.444444c0 28.444444 5.688889 51.2 17.066667 73.955556l-39.822222 17.066667c-28.444444-34.133333-68.266667-62.577778-119.466667-62.577778C119.466667 568.888889 56.888889 631.466667 56.888889 711.111111S119.466667 853.333333 199.111111 853.333333 341.333333 790.755556 341.333333 711.111111v-22.755555l45.511111-22.755556c34.133333 45.511111 91.022222 73.955556 153.6 73.955556 45.511111 0 85.333333-17.066667 119.466667-39.822223l45.511111 45.511111c-11.377778 22.755556-22.755556 51.2-22.755555 79.644445 0 79.644444 62.577778 142.222222 142.222222 142.222222s142.222222-62.577778 142.222222-142.222222-62.577778-142.222222-142.222222-142.222222z m-113.777778-568.888889c45.511111 0 85.333333 39.822222 85.333333 85.333333S756.622222 284.444444 711.111111 284.444444 625.777778 244.622222 625.777778 199.111111 665.6 113.777778 711.111111 113.777778z m-512 682.666666c-45.511111 0-85.333333-39.822222-85.333333-85.333333S153.6 625.777778 199.111111 625.777778s85.333333 39.822222 85.333333 85.333333S244.622222 796.444444 199.111111 796.444444zM398.222222 540.444444C398.222222 460.8 460.8 398.222222 540.444444 398.222222S682.666667 460.8 682.666667 540.444444 620.088889 682.666667 540.444444 682.666667 398.222222 620.088889 398.222222 540.444444z m426.666667 369.777778c-45.511111 0-85.333333-39.822222-85.333333-85.333333s39.822222-85.333333 85.333333-85.333333 85.333333 39.822222 85.333333 85.333333-39.822222 85.333333-85.333333 85.333333z" fill="#ffffff" p-id="3396"></path>
          </svg>
          关系图
        </span>
      </div>
      <button @click="fetchData" class="tech-button">获取数据</button>
    </div>
    <div id="show_graph" style="position: relative;"></div>
    <div id="explosion_graph" style="position: absolute; bottom: 1px; left: 10px; width: 200px; height: 150px; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center;"></div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "relation_graph",
  data() {
    return {
      categories: [
        {
          name: "",
          color: "#0008FF",
        },
      ],
      key: '',
      graphData: null, // 用于存储从后端获取的图数据
      explosionData: null, // 用于存储引爆点图的数据
    };
  },
  methods: {
    myRelationGraph(key) {
      let option;
      let myChart = this.$echarts.init(document.getElementById("show_graph"));
      myChart.showLoading();
      this.$axios.get(`/topic_relation_graph?topic=${key}`).then((graphResponse) => {
        console.log(graphResponse);
        this.graphData = graphResponse.data.data;
        if (!this.graphData) return;

        let nodes = this.graphData.nodes_list;
        for (let index in nodes) {
          nodes[index].id = index;
        }
        let links = this.graphData.links_list;
        links.forEach((link) => {
          for (let node of nodes) {
            if (link.source === node.name) {
              link.source = node.id;
              node.show = true;
            }
            if (link.target === node.name) {
              link.target = node.id;
              node.show = true;
            }
          }
        });

        console.log('转换后的节点:', nodes); // 添加调试信息
        console.log('转换后的边:', links); // 添加调试信息

        let newNodes = [];
        for (let n in nodes) {
          if (nodes[n].show) {
            newNodes.push(nodes[n]);
          }
        }

        myChart.hideLoading();
        nodes.forEach((node) => {
          node.label = {
            show: node.value > 20,
            color: '#ffffff',
          };
        });

        option = {
          tooltip: {},
          legend: [
            {
              data: this.categories.map((a) => a.name),
            },
          ],
          animationDuration: 1500,
          animationEasingUpdate: "quinticInOut",
          series: [
            {
              name: "用户关系图",
              type: "graph",
              layout: "force",
              force: {
                repulsion: 150,  // 增大节点间斥力，防止重叠
                edgeLength: 50,  // 增大边的理想长度
                gravity: 0.3      // 降低向心力，让节点更分散
              },
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
              itemStyle: {
                color: "#3de1ad", // 这里将颜色设置为橙色，你可以换成你想要的任何颜色
              },
              emphasis: {
                focus: "adjacency",
                lineStyle: {
                  width: 7,
                  color: "#00FFFF",
                },
                nodeStyle: {
                  color: "#FF00FF", // 这里将悬停颜色设置为紫色，你可以换成你想要的任何颜色
                  borderWidth: 5,
                  shadowBlur: 20,
                  shadowColor: 'rgba(0,0,0,0.3)', // 增加阴影效果
                },
              },
            },
          ],
        };

        myChart.setOption(option);

        // 处理引爆点图的数据，筛选出value前5的点
        this.explosionData = nodes.sort((a, b) => b.value - a.value).slice(0, 5);
        this.drawExplosionGraph();
      });
    },
    drawExplosionGraph() {
      if (!this.explosionData) return;
      let explosionDiv = document.getElementById('explosion_graph');
      explosionDiv.innerHTML = ''; // 清空容器内容

      // 创建标题元素并添加到容器中
      let title = document.createElement('div');
      title.textContent = "引爆点";
      title.style.fontWeight = 'bold';
      title.style.marginBottom = '5px';
      explosionDiv.appendChild(title);

      this.explosionData.forEach((node) => {
        let item = document.createElement('div');
        item.textContent = `${node.name}: ${node.value}`;
        item.style.marginBottom = '5px';
        explosionDiv.appendChild(item);
      });
    },
    ToPersonList() {
      this.$router.push({
        path: "/topic_person_list",
        query: {
          key: this.key,
        },
      });
    },
    async fetchData() {
      try {
        this.key = this.$route.query.key;
        const response = await this.$axios.get(`/start_topic?topic=${this.key}`);
        console.log(response);
        if (response.data.code === 0) {
          // const graphResponse = await this.$axios.get(`/topic_relation_graph?topic=${this.key}`);
          // console.log(graphResponse);
          // this.graphData = graphResponse.data.data;
          this.myRelationGraph(this.key);
        } else {
          console.error('获取数据失败:', response.data.message);
        }
      } catch (error) {
        console.error('请求出错:', error);
      }
    },
  },
  mounted() {
    this.key = this.$route.query.key;
    // this.$axios.get(`/topic_relation_graph?topic=${this.key}`).then(() => {
    //   this.myRelationGraph(this.key);
    // });
  },
};
</script>

<style scoped>
.tech-button {
    
    /* 布局 */
    padding: 8px 14px;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-top: 14px;
    /* 文字 */
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: #fff;
    text-transform: uppercase;
    
    /* 背景与边框 */
    background: linear-gradient(135deg, #15bac0 0%, #2663be 100%);
    border: none;
    border-radius: 8px;
    
    /* 光影效果 */
    box-shadow: 
        0 4px 20px rgba(5, 40, 108, 0.3),
        inset 0 2px 4px rgba(255, 255, 255, 0.1);
    
    /* 交互效果 */
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

/* 悬停状态 */
.tech-button:hover {
    transform: translateY(-1px);
    background: linear-gradient(135deg, #2663be 0%, #15bac0 100%);
    box-shadow: 
        0 6px 24px rgba(5, 40, 108, 0.4),
        inset 0 3px 6px rgba(255, 255, 255, 0.15);
}

/* 点击状态 */
.tech-button:active {
    transform: translateY(1px);
    box-shadow: 
        0 2px 12px rgba(5, 40, 108, 0.2),
        inset 0 1px 2px rgba(255, 255, 255, 0.1);
}

/* 科技感边框高光 (可选) */
.tech-button::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    pointer-events: none;
}

/* 动态流光效果 (可选) */
.tech-button::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        45deg,
        transparent 25%,
        rgba(255, 255, 255, 0.1) 50%,
        transparent 75%
    );
    animation: techFlow 4s infinite linear;
    opacity: 0.3;
}

@keyframes techFlow {
    0% { transform: translateX(-25%) translateY(-25%); }
    100% { transform: translateX(25%) translateY(25%); }
}
.clickable-text {
  cursor: pointer; /* 鼠标指针变为手形，表示可点击 */
  color: #ffffff; /* 默认文字颜色 */
  transition: color 0.3s ease; /* 添加颜色过渡效果 */
}

.clickable-text:hover {
  color: #00FFFF; /* 悬停时文字颜色改变 */
}

.relation_graph_top_row {
  margin-left: 40%;
  font-size: 20px;
  font-weight: 600 ;
 
  margin-top: 17px;
  display: flex;
  align-items: center;
  text-align: center;
}
.relation_graph_top {
  color:#ffffff;
  display: flex;
  text-align: center;
  margin-right: 20px; /* 可以根据需要调整间距 */
}

.icon {
  margin-right: 5px; /* 图标和文字之间的间距 */
}

.relation_graph {
  flex-direction: column; /* 垂直排列子元素 */
  margin-top: 0px;
  background-color:rgba(254, 254, 255, 0);
  position: relative;
  width: 93%;
  height: 90%;
  text-align: center;
  cursor: pointer; /* 改变鼠标指针为手形 */
  color: #ffffff;
  border: 2px solid #669ef3a5; /* 深色边框 */
  border-radius: 10px;
  
  box-sizing: border-box;
  box-shadow: 0 0 15px rgba(233, 229, 238, 0.304), 0 0 25px rgba(63, 154, 87, 0.4); /* 外阴影 */
}

.relation_graph:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); /* 鼠标悬浮时加上阴影效果 */
}
#show_graph {
  
  width: 100%;
  height: 450px; /* 或使用 calc(100% - 50px) 等动态值 */
}

#explosion_graph {
  width: 100%; height: 100%;
    background-color: rgba(126, 119, 119, 0.192); /* 半透明黑色背景 */
    border: 1px solid rgba(255, 255, 255, 0.2); /* 淡色边框 */
    box-shadow: 0 0 5px rgba(10, 122, 133, 0.5); /* 阴影 */
}
</style>