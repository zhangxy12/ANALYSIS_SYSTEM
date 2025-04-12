<template>
    <div id="data-view">
      <dv-full-screen-container>
        <top-header />
  
        <div class="main-content">
          <div class="big-data">
            <!-- 左侧 -->
            <div class="left">
                <dv-border-box-13 style="height: 180px;">
                <div class="allCount" style="height: 180px;">
                  <allCount />
                </div>
              </dv-border-box-13>
              <dv-border-box-6 :color="['lightskyblue']">
                <div class="mood">
                  <mood />
                </div>
              </dv-border-box-6>

              <dv-border-box-12>
                <div class="allApps">
                  <allApps />
                </div>
              </dv-border-box-12>

            </div>
  
            <!-- 中间 -->
            <div class="center">
              <!-- 中间内容 -->
              <!-- <dv-border-box-12> -->
                <div class="allIp">
                  <allIp />
                </div>
              <!-- </dv-border-box-12> -->


              <dv-border-box-12>
                <div class="allPost">
                  <allPost />
                </div>
              </dv-border-box-12>

            </div>
  
            <!-- 右侧 -->
            <div class="right">
                
              <dv-border-box-13>
                <div class="hot-search">
                  <hotsearch />
                </div>
              </dv-border-box-13>
              <dv-border-box-6 :color="['lightskyblue']"> 
                <div class="word">
                  <word />
                </div>
              </dv-border-box-6 >
              <dv-border-box-12>
                <div class="class">
                  <classChart />
                </div>
              </dv-border-box-12>
            </div>
          </div>
        </div>
      </dv-full-screen-container>
    </div>
  </template>
  
  <script>
  import topHeader from '../components/mainscreen/topHeader'
  import hotsearch from '../components/mainscreen/hotsearch'
  import word from '../components/mainscreen/word'
  import classChart from '../components/mainscreen/classChart'
  import mood from '../components/mainscreen/mood'
  import allCount from '../components/mainscreen/allCount'
  import allApps from '../components/mainscreen/allApps'
  import allPost from '../components/mainscreen/allPost'
  import allIp from '../components/mainscreen/ip'


  export default {
    name: 'DataView',
    components: {
      topHeader,
      hotsearch,
      word,
      classChart,
      mood,
      allCount,
      allApps,
      allPost,
      allIp,

    },
    data() {
      return {}
    },
    methods: {}
  }
  </script>
  
  <style>
  #data-view {
    width: 100%;
    height: 100%;
    background-color: #030409;
    color: #fff;
  }
  
  #dv-full-screen-container {
    background-image: url('../background/bg.png');
    background-size: 100% 100%;
    box-shadow: 0 0 3px blue;
    display: flex;
    flex-direction: column;
  }
  
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .big-data {
    display: flex; /* 使用 flex 布局 */
    flex: 1;
    justify-content: space-between; /* 使子元素在水平方向上均匀分布 */
  }
  
  .left {
    width: 25%;
    height:82%;
    display: flex;
    flex-direction: column;
  }
  
  .center {
    width: 50%;
    height:82%;
    display: flex;
    flex-direction: column;
  }
  
  .right {
    margin-right: 20px;
    width: 25%;
    height:82%;
    display: flex;
    flex-direction: column;
  }
  
  .word {
    height: 200px;
  }
  .mood {
    height: 200px;
  }
  .allCount{
    height: 150px;
  }
  .allPost{
    height: 200px;
  }
  </style>