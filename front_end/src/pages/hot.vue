<template>
    <div class="main-container">
      <div class="side">
        <SideBorder />
      </div>
    <div class="content">
      <div class="container-wrapper">
        <div class="wb-container">
            <h1>微博热搜</h1>
            <button class="tech-button" @click="fetchHotSearchWb">刷新</button>
            
            <!-- 热搜列表 -->
            <ul class="search-list">
            <li v-for="(item, index) in hotSearchListWb" :key="index" class="search-item">
                <div class="hot-search-details">
                <div class="order-box">
                    <span :class="['order', { 'highlight': index < 3 }]">
                        No.{{ item.seq }}</span>
                </div>
                </div>
    
                <div class="title">
                <a :href="item.url" target="_blank">{{ formatTitle(item.title) }}</a>
                <span v-if="item.label" class="label">{{ item.label }}</span>
                </div>
            </li>
            </ul>
        </div>

        <div class="baidu-container">
            <h1>百度热搜</h1>
            <button class="tech-button" @click="fetchHotSearchBaidu">刷新</button>
            
            <!-- 热搜列表 -->
            <ul class="search-list">
            <li v-for="(item, index) in hotSearchListBaidu" :key="index" class="search-item">
                <div class="hot-search-details">
                <div class="order-box">
                    <span :class="['order', { 'highlight': index < 3 }]"> No.{{ item.seq }}</span>
                </div>
                </div>
    
                <div class="title">
                <a :href="item.url" target="_blank">{{ formatTitle(item.title) }}</a>
                <span v-if="item.label" class="label-baidu">{{ item.hot_index }}</span>
                </div>
            </li>
            </ul>
        </div>

        <div class="tieba-container">
            <h1>贴吧热搜</h1>
            <button class="tech-button" @click="fetchHotSearchTieba">刷新</button>
            
            <!-- 热搜列表 -->
            <ul class="search-list">
            <li v-for="(item, index) in hotSearchListTieba" :key="index" class="search-item">
                <div class="hot-search-details">
                <div class="order-box">
                    <span :class="['order', { 'highlight': index < 3 }]"> No.{{ item.seq }}</span>
                </div>
                </div>
    
                <div class="title">
                <a :href="item.url" target="_blank">{{ formatTitle(item.title) }}</a>
                <span v-if="item.label" class="label-tieba">{{ item.hot }}</span>
                </div>
            </li>
            </ul>
        </div>
      </div>
    

      <div class="container-analyze">
        <div class="sentiment">
            <div id="sentimentChart" style="height: 380px;"></div>
        </div> 
        <div class="wordcloud">
            <div id="wordcloudChart" style="height: 380px;"></div>
        </div>
      </div>
    </div>
    </div>
  </template>
  
  <script>
 import axios from 'axios'; // 引入 axios
 import * as echarts from 'echarts'; // 引入 ECharts
  import SideBorder from "../components/Side_border";
  
  export default {
    data() {
      return {
        hotSearchListWb: [], // 微博热搜列表
        hotSearchListTieba: [], // 贴吧热搜列表
        hotSearchListBaidu: [], // 百度热搜列表
        sentimentData: { // 存储情感分析数据
            wb: { positive: 0, negative: 0, neutral: 0 },
            tieba: { positive: 0, negative: 0, neutral: 0 },
            baidu: { positive: 0, negative: 0, neutral: 0 }
        },
        maxWordCount: 120 ,// 这里设置你想要显示的词云最大数量
        wordcloudData: [] // 存储词云数据
      };
    },
    components: {
      SideBorder,
    },
    mounted() {
        this.fetchHotSearchWb(); // 获取微博热搜
        this.fetchHotSearchTieba(); // 获取贴吧热搜
        this.fetchHotSearchBaidu(); // 获取百度热搜
        this.drawSentimentChart(); // 绘制情感分析柱状图
        this.fetchWordCloudData(); // 获取词云数据
    },
    methods: {
      formatTitle(title) {
      if (title.length > 13) {
        return title.slice(0, 13) + '...';
      }
      return title;
    },

  async fetchHotSearchWb() {
    this.sentimentData.wb = { positive: 0, negative: 0, neutral: 0 };
    try {
      const response = await this.$axios.get('/weibo_hot'); // 微博容器的路由
      if (response.data.code === 0) {
        this.hotSearchListWb = response.data.data; // 存储到微博的列表中
        this.analyzeSentiment('wb', this.hotSearchListWb); // 分析情感
      } else {
        alert('获取微博热搜数据失败');
      }
    } catch (error) {
      alert('微博请求发生错误：' + error.message);
    }
  },

  async fetchHotSearchTieba() {
    this.sentimentData.tieba = { positive: 0, negative: 0, neutral: 0 };
    try {
      const response = await this.$axios.get('/tieba_hot'); // 贴吧容器的路由
      if (response.data.code === 0) {
        this.hotSearchListTieba = response.data.data; // 存储到贴吧的列表中
        this.analyzeSentiment('tieba', this.hotSearchListTieba); // 分析情感
      } else {
        alert('获取贴吧热搜数据失败');
      }
    } catch (error) {
      alert('贴吧请求发生错误：' + error.message);
    }
  },

  async fetchHotSearchBaidu() {
    this.sentimentData.baidu = { positive: 0, negative: 0, neutral: 0 };
    try {
      const response = await this.$axios.get('/baidu_hot'); // 百度容器的路由
      if (response.data.code === 0) {
        this.hotSearchListBaidu = response.data.data; // 存储到百度的列表中
        this.analyzeSentiment('baidu', this.hotSearchListBaidu); // 分析情感
      } else {
        alert('获取百度热搜数据失败');
      }
    } catch (error) {
      alert('百度请求发生错误：' + error.message);
    }
  },
// 情感分析逻辑，基于小数值来判断情感
analyzeSentiment(app, hotSearchList) {
      hotSearchList.forEach(item => {
        const sentiment = item.sentiment; // 后端返回的小数情感数据 (0到1之间)
        if (sentiment >= 0.7) {
          this.sentimentData[app].positive += 1;
        } else if (sentiment <= 0.3) {
          this.sentimentData[app].negative += 1;
        } else {
          this.sentimentData[app].neutral += 1;
        }
      });
      this.drawSentimentChart(); // 每次更新情感分析数据后绘制图表
    },

    // 使用 ECharts 绘制柱状图
    drawSentimentChart() {
      const sentimentChart = echarts.init(document.getElementById('sentimentChart'));

    const option = {
    title: {
        text: '情感分析统计',
        left: 'center',
        textStyle: {
        color: '#FFFFFF', // 设置标题字体为白色
        fontSize: 18,
        fontWeight: 'bold'
        },
        padding: [5, 0, 10, 0] // 增加标题与图表的间距
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
        type: 'shadow'
        }
    },
    legend: {
        data: ['积极', '消极', '中性'],
        top: 'top',
        textStyle: {
        color: '#FFFFFF', // 设置图例字体为白色
        fontSize: 14
        },
        padding: [30, 0, 20, 0] // 增加图例与图表的间距
    },
    xAxis: {
        type: 'category',
        data: ['微博', '百度', '贴吧'],
        axisLabel: {
        textStyle: {
            color: '#FFFFFF', // 设置横坐标字体为白色
        }
        },
        axisLine: {
        lineStyle: {
            color: '#FFFFFF' // 设置横坐标轴线为白色
        }
        }
    },
    yAxis: {
        type: 'value',
        min: 0,
        axisLabel: {
        textStyle: {
            color: '#FFFFFF', // 设置纵坐标字体为白色
        }
        },
        axisLine: {
        lineStyle: {
            color: '#FFFFFF' // 设置纵坐标轴线为白色
        }
        }
    },
    series: [
        {
        name: '积极',
        type: 'bar',
        data: [
            this.sentimentData.wb.positive,
            this.sentimentData.baidu.positive,
            this.sentimentData.tieba.positive 
        ],
        itemStyle: {
            color: '#1E90FF' 
        }
        },
        {
        name: '消极',
        type: 'bar',
        data: [
            this.sentimentData.wb.negative,
            this.sentimentData.baidu.negative,
            this.sentimentData.tieba.negative
        ],
        itemStyle: {
            color: '#4682B4' // 设置消极情感柱状图的颜色为红色
        }
        },
        {
        name: '中性',
        type: 'bar',
        data: [
            this.sentimentData.wb.neutral,
            this.sentimentData.baidu.neutral,
            this.sentimentData.tieba.neutral
        ],
        itemStyle: {
            color: '#5F9EA0' 
        }
        }
    ]
    };

    sentimentChart.setOption(option);
    },

    // 获取后端词云数据
    async fetchWordCloudData() {
      try {
        const response = await this.$axios.get('/hot_wordcloud'); // 获取词云数据接口
        if (response.data.code === 0) {
          this.wordcloudData = response.data.data.wordcloud_data; // 存储词云数据
          this.drawWordCloud(); // 绘制词云
        } else {
          alert('获取词云数据失败');
        }
      } catch (error) {
        alert('请求词云数据发生错误：' + error.message);
      }
    },

      // 绘制词云图
        drawWordCloud() {
          // 截取前 maxWordCount 条数据
        const limitedData = this.wordcloudData.slice(0, this.maxWordCount);

        const data = limitedData; // 使用截取后的数据

        // 词云图配置
        const chart = echarts.init(document.getElementById('wordcloudChart'));
        const option = {
            tooltip: {
            show: true,
            formatter: function (params) {
                return params.name + ": " + params.value;
            }
            },
            series: [{
            type: 'wordCloud',
            gridSize: 8, // 控制词云图的网格大小，值越大词语之间的间距越大
            sizeRange: [15, 30], // 控制词语的大小范围
            rotationRange: [0, 0], // 控制词语的旋转角度范围
            shape: 'circle', // 控制词云图的形状，可选值为 'circle', 'cardioid', 'diamond', 'triangle-forward', 'triangle', 'pentagon', 'star'

            
            width: '70%',
            height: '70%',
            right: 'center',
            bottom: 'center',
            textStyle: {
                color: function () {
                // 随机生成颜色
                return "rgb(" +
                    [
                    Math.round(Math.random() * 55 + 200), // 红色分量：200-255
                    Math.round(Math.random() * 55 + 200), // 绿色分量：200-255
                    Math.round(Math.random() * 55 + 200), // 蓝色分量：200-255
                    ].join(",") + ")";
                }
            },
            // 控制布局以防止超出边界
            wordCloud: {
                rotationRange: [-45, 90], // 限制旋转角度，避免过多倾斜导致超出边界
                width: '100%',
                height: '100%',
                
                // 设置最大和最小的字体大小，确保不会太大或太小
                sizeRange: [30, 60]
            },
            data: data.map(item => ({
                name: item.name,
                value: item.value
            }))
            }]
        };
        chart.setOption(option);
    }
  }
};
</script>

  
  <style scoped>

  .main-container {
    width: 100%;
    height: 180%; 
    margin: 0; 
    padding: 0;
    text-align: center; 
    display: flex;
  width: 100%;
  height: 100vh; /* 使用 vh 单位确保占满整个视口高度 */
  background: linear-gradient(45deg, #1e5959,  #247b7b, #27aeb0);
  background-size: 400% 400%;
  animation: gradient 20s ease infinite;
  background-color: rgba(255, 255, 255, 0.3); 
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
  .content {
    flex: 1;
    padding-left: 150px;
    width: 100%;
    overflow-y: auto;
  }

  .container-analyze {
    background-color: #ffffff00;
    margin-top: 70px;
    
    display: flex; /* 使用弹性布局实现横向排列 */
    justify-content: space-between; /* 容器之间均匀分布 */
    /* margin: 0 auto; */
    width: 100%; /* 整体宽度 */
    height: 53%;
}

.sentiment {
  margin-left: 10px;
    width: 47%;
    height: 100%;
    /* border: 2px solid #747a83; */
    margin-bottom: 10px;
    /* height: 12rem; width: 24rem;  */
    color:white; padding: 1rem;
    box-shadow: 0 0 3rem rgba(100,200,255,.5) inset;
    background: rgba(106, 150, 148, 0.216);
    border-radius: 10px;
}
#sentimentChart {
  width: 100%;
  height: 90%;
}

.wordcloud {
  margin-left: 90px;
  margin-right: 45px;
    width: 50%;
    height: 100%;
    /* border: 2px solid #747a83; */
    margin-bottom: 10px;
    color:white; padding: 1rem;
    box-shadow: 0 0 3rem rgba(100,200,255,.5) inset;
    background: rgba(106, 150, 148, 0.216);
    border-radius: 10px;
}
#wordcloudChart {
  width: 95%;
  height: 90%;
}

  .container-wrapper { 
  margin-top: 15px;
  display: flex; /* 使用弹性布局实现横向排列 */
  justify-content: space-between; /* 容器之间均匀分布 */
  /* margin: 0 auto; */
  width: 97%; /* 整体宽度 */
  height: 99%;
}
.wb-container,
.tieba-container,
.baidu-container {
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1; /* 三个容器均分宽度 */
  margin-top: 2%; 
  margin: 0 15px; /* 设置容器之间的间距 */
  position: relative;
  width: 100%;
  height: 95vh;
   /* 自定义滚动条样式 */
   scrollbar-width: none; 
   color:white; padding: 1rem;
    box-shadow: 0 0 3rem rgba(100,200,255,.5) inset;
}
.wb-container,
.tieba-container,
.baidu-container {
                padding-top: 0%;
                background: linear-gradient(to left, #2CD5FF, #2CD5FF) left top no-repeat,
                linear-gradient(to bottom, #2CD5FF, #2CD5FF) left top no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) right top no-repeat,
                linear-gradient(to bottom, #2CD5FF, #2CD5FF) right top no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) left bottom no-repeat,
                linear-gradient(to bottom, #2CD5FF, #2CD5FF) left bottom no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) right bottom no-repeat,
                linear-gradient(to left, #2CD5FF, #2CD5FF) right bottom no-repeat;
                background-size: 4px 20px, 20px 4px, 4px 20px, 20px 4px;
                border-image: linear-gradient(rgba(5, 162, 189, 0.774), rgba(249, 249, 249, 0.9), rgba(5, 162, 189, 0.774));
                border-image-slice: 1;
                border-width: 2px;
                border-style: solid;
                position: relative;
            }
.wb-container h1,
.tieba-container h1,
.baidu-container h1 {
    position: sticky; /* 使用sticky固定在容器顶部 */
    display: inline-block;
    width: 35%;
    background:#3058aa9e;
    font-size: 14px;
    top: 0;
    left: 32%;
    padding: 4px 0px;
    color: #f6fcfd;
    border-radius: 0 0 10px 10px;
    z-index: 10; 
    }

  .button {
    padding: 6px 8px;
    position: sticky; /* 使用sticky固定在容器顶部 */
    font-size: 10px;
    color: #fff;
    background-color: #05286C;;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 0px;
    margin-left: 200px;
    z-index: 10; 
  }
  
  .button:hover {
    background-color: #0056b3;
  }
  
  .tech-button {
    margin-bottom: 0px;
    margin-left: 200px;
    /* 布局 */
    padding: 10px 14px;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    
    /* 文字 */
    font-size: 11px;
    font-weight: 500;
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

  .search-list {
    list-style-type: none;
    padding: 0;
    margin-top: 20px;
  }
  
  .search-item {
    background-color: #ffffff00;
    margin: 1px 0;
    padding: 5px;
    border-radius: 2px;
    text-align: left;
    display: flex;
    justify-content: flex-start;
  }
  
  .search-item .hot-search-details {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-right: 20px;
  }
  
  .order-box {
    margin-bottom: 5px;
  }
  
  .order {
    display: inline-block;
    background-color: rgba(104, 149, 222, 0);
    color: white;
    padding: 5px 7px;
    font-size: 13px;
  }
  
  .order.highlight {
    background-color: #4fda7600; /* 使用更加醒目的背景色 */
    font-size: 15px;  /* 增大前三项的字体 */
    color: #34de9d;
  }
  
  .title {
    display: flex;
    align-items: center; /* 让 label 和 title 水平对齐 */
  }
  
  .title a {
    color: #fffefe;
    font-size: 15px;
    text-decoration: none;
    margin-right: 10px; /* 给 title 和 label 之间留一些空间 */
  }
  
  .title a:hover {
    text-decoration: underline;
  }
  
  .label {
    display: inline-block;
    background-color: red;
    color: white;
    padding: 5px 5px;
    border-radius: 6px;
    font-size: 10px;
  }

  .label-baidu {
    display: inline-block;
    background-color: rgba(255, 128, 0, 0.948);
    color: white;
    width: 100px;
    padding: 5px 10px;
    border-radius: 10px;
    font-size: 10px;
  }

  .label-tieba {
    display: inline-block;
    background-color: rgba(207, 140, 6, 0.937);
    color: white;
    padding: 5px 10px;
    border-radius: 10px;
    font-size: 10px;
  }
  </style>