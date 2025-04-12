<template> 
    <div class="Rumor">
      
      <div class="side">
        <SideBorder />
      </div>
      <div class="content">
    
        <div class="main">
          
          <!-- <div class="center">
            <div class="post">
              <Post />
            </div> 
            <div class="user">
              <User />
            </div>
          </div> -->
          <div class="left">
            <div class="l_a">
              <div class="detect">
              <Detect />
            </div>
          </div>
            <div class="l_b">
              <div class="detail">
              <Detail />
              </div>
          </div>
        </div>
          <div class = "right">
            <div class="r_a">
                <rumorList />
            </div>
          
            <div class="r_b">
            <div class="Word_cloud">
              <WordCloud />
            </div>
          </div>
        </div>
          
          </div>
          

        </div>
      </div>
  </template>
  
  <script>
  import SideBorder from "../components/Side_border";
//   import User from "../components/WXAnalyze/user";
  import rumorList from "../components/Rumor/rumorList";
  import Detail from "../components/Rumor/Detail";
  import WordCloud from "../components/Rumor/Wordcloud";
  import Detect from "../components/Rumor/Detect";
  
  export default {
    name: "Rumor",
    components: {
    rumorList,
    Detail,
    WordCloud,
    Detect,
    SideBorder,
    },
  };
  </script>
  
  <style scoped>
  /* 主容器 */
  .Rumor {
    display: flex;
    width: 100%;
    height: 100%; /* 使其填满整个视口 */
    background: linear-gradient(45deg, #1e5959,  #247b7b, #27aeb0);
  background-size: 400% 400%;
  animation: gradient 8s ease infinite;

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

  .side {
    width: 160px;
  }
  .content {
    background-color: rgba(253, 251, 255, 0); /* 半透明背景色，便于看到背景图片 */
    flex: 1;
    padding-left: 30px;
    width: 95%;
    height: 96%;
    overflow-y: auto;
    /* 自定义滚动条样式 */
   scrollbar-width: none; 
   
  }
  
  .main {
    display: flex;
    flex: 1; /* 占满剩余空间 */
    margin: 10px;
    height: 97%;
    display: flex;
    flex-direction:row;
  }
  
  .left {
    width: 70%; /* 左侧栏宽度 */
    height: 99%; 
    display: flex;
    flex-direction:column;
    margin-right: 10px;
  }
  
  .right {
    width: 30%; /* 右侧栏宽度 */
    height: 99%; /* 高度自适应 */
    position: relative;
    display: flex;
    flex-direction: column;
    /* 保证右侧区域的组件不被推到下方 */
    margin-left: 10px;
    margin-right: 30px;
    flex-shrink: 0; /* 保证右侧区域不会被压缩 */
  }
  .r_a {
    height: 60%; /* 高度自适应 */
  }
  .r_b {
    margin-top: 20px;
    height: 34%; /* 高度自适应 */
    position: relative;
  }
  .l_a {
    margin-top: 3%;
    height: 40%;
    position: relative;
    
  }
  .l_b {
    height: 50%;
  }
  /* 每个小组件的容器 */
  .user,
  .post,
  .word,
  .mood {
    
    width: 100%;
    margin-bottom: 0px;
    flex: 1; /* 自适应高度 */
    min-height: 200px; /* 最小高度，避免内容过少时组件变得过小 */
  }

  .word {
    height: 30%; 
    margin-bottom: 0;
  }
  
  .mood {
    height: 70%; 
    margin-top:0%;
  }
  
  @media (max-width: 768px) {
    .Rumor {
      flex-direction: column;
      height: auto;
    }
  
    .main {
      flex-direction: column;
      height: auto;
      margin: 0;
    }
  
    .left,
    .right {
      width: 100%;
      height: auto;
    }
  
    .center {
      width: 100%;
      height: 100%;
      margin: 10px 0;
    }
  }
  </style>
  