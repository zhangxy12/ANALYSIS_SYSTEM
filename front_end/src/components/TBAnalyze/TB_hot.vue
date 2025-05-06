<template>
    <div class="main-container">
      
      <div class="container-wrapper">
        <div class="tieba-container">
            <h1>贴吧热搜</h1>
            <button class="button" @click="fetchHotSearchTieba">刷新</button>
            
            <!-- 热搜列表 -->
            <ul class="search-list">
            <li v-for="(item, index) in hotSearchListTieba" :key="index" class="search-item">
                <div class="hot-search-details">
                <div class="order-box">
                    <span :class="['order', { 'highlight': index < 3 }]"> No.{{ item.seq }}</span>
                </div>
                </div>
    
                <div class="title">
                <a :href="item.url" target="_blank">{{ item.title }}</a>
                <span v-if="item.label" class="label-tieba">{{ item.hot }}</span>
                </div>
            </li>
            </ul>
        </div>
      </div>

    </div>
  </template>
  
  <script>
 import axios from 'axios'; // 引入 axios
 import * as echarts from 'echarts'; // 引入 ECharts
  
  export default {
    data() {
      return {
        hotSearchListTieba: [], // 贴吧热搜列表
      };
    },
    
    mounted() {
        this.fetchHotSearchTieba(); // 获取贴吧热搜   
    },
    methods: {
  async fetchHotSearchTieba() {
    
    try {
      const response = await this.$axios.get('/tieba_hot'); // 贴吧容器的路由
      console.log(response);
      if (response.data.code === 0) {
        this.hotSearchListTieba = response.data.data; // 存储到贴吧的列表中
        
      } else {
        alert('获取贴吧热搜数据失败');
      }
    } catch (error) {
      alert('贴吧请求发生错误：' + error.message);
    }
  },

  }
};
</script>

  
  <style scoped>

  .main-container {
    overflow: hidden;
    width: 100%;
    height: 90%; 
    margin: 0; 
    padding: 0;
    background-color: #ffffff00;
    /* background-color: #e05b92d0; */
    /* background: linear-gradient(to right, #242fc2, #416777d6); */
    text-align: center; 
    scrollbar-width:thin;
  }

.tieba-container{
  overflow-y: hidden;
  overflow-x: hidden;
  flex: 1; /* 三个容器均分宽度 */
  margin-top: 2px;
  height: 100%; 
  position: relative;
   /* 自定义滚动条样式 */
    
}

.tieba-container {
    height: 100%;
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
                border: 2px solid #073F97;
                position: relative;
            }

.tieba-container h1 {
    position: sticky; /* 使用sticky固定在容器顶部 */
    display: inline-block;
    width: 35%;
    background:#05286C;
    font-size: 14px;
    top: 0;
    left: 32%;
    padding: 4px 0px;
    color: #19E8FE;
    border-radius: 0 0 10px 10px;
    z-index: 1; 
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
    z-index: 1; 
  }
  
  .button:hover {
    background-color: #0056b3;
  }
  
  .search-list {
    list-style-type: none;
    padding: 0;
    margin-top: 20px;
  }
  
  .search-item {
    background-color: #ffffff00;
    font-size: 10px;
    margin-left: 5px ;
    padding: 0px;
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
    font-size: 12px;
  }
  
  .order-box {
    margin-bottom: 5px;
  }
  
  .order {
    display: inline-block;
    background-color: rgba(104, 149, 222, 0);
    color: white;
    padding: 0px;
    font-size: 10px;
  }
  
  .order.highlight {
    background-color: #4fda7600; /* 使用更加醒目的背景色 */
    font-size: 12px;  /* 增大前三项的字体 */
    color: #ff6200;
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

  .label-tieba {
    display: inline-block;
    background-color: rgba(207, 140, 6, 0.937);
    color: white;
    padding: 5px 10px;
    border-radius: 10px;
    font-size: 10px;
  }
  </style>