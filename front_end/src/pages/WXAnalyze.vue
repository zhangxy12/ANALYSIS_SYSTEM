<template> 
    <div class="WXAnalyze">
      <!-- <div class="side">
        <SideBorder />
      </div> -->
      <div class="container">
        <div class="top">
          <Search />
        </div>
        <div class="main">
          <div class="left">
            <DefaultPanel />
          </div>
          <div class="center">
            <div class="user" style="height: 120%;">
              <User />
            </div>
            <div class="post">
              <Post />
            </div> 
            
          </div>
          <div class="right"style=" width: 360px;">
            <div class="word">
              <WordCloud />
            </div>
            <div class="mood">
              <Mood />
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  // import SideBorder from "../components/Side_border";
  import User from "../components/WXAnalyze/user";
  import DefaultPanel from "../components/WXAnalyze/Default_panel";
  import Mood from "../components/WXAnalyze/mood";
  import Search from "../components/WXAnalyze/Search";
  import Post from "../components/WXAnalyze/post";
  import WordCloud from "../components/WXAnalyze/Word_cloud";
  
  export default {
    name: "WXAnalyze",
    components: {
      User,
      DefaultPanel,
      Mood,
      Search,
      Post,
      WordCloud,
      // SideBorder,
    },
  };
  </script>
  
  <style scoped>
  /* 主容器 */
  .WXAnalyze {
    display: flex;
    width: 100%;
    height: 100%; /* 使其填满整个视口 */
    background: linear-gradient(to right, #086264, #229fe2d6);

  }
  
  .container {
    display: flex;
    flex-direction: column;
    width: 99%;
    height: 95%;
    background-color: rgba(253, 251, 255, 0); /* 半透明背景色，便于看到背景图片 */
  }
  
  .top {
    height: 6%; /* 顶部区域高度 */
  }
  
  .main {
    display: flex;
    flex: 1; /* 占满剩余空间 */
    margin: 10px;
    height: 95%;
  }
  
  .left {
    width: 20%; /* 左侧栏宽度 */
    height: 100%; 
  }
  
  .center {
    width: 50%;
    height: 100%;
    margin: 15px 10px;
    margin-bottom: 0px;
    display: flex;
    flex-direction: column;
    
  }
  
  .right {
    width: 30%; /* 右侧栏宽度 */
    height: 100%; /* 高度自适应 */
    
    position: relative;
    display: flex;
    flex-direction: column;
    /* 保证右侧区域的组件不被推到下方 */
    margin-top: 0;
    flex-shrink: 0; /* 保证右侧区域不会被压缩 */
  }
  
  /* 每个小组件的容器 */
 

  .word,
  .mood {
    
    width: 100%;
    margin-bottom: 0px;
    flex: 1; /* 自适应高度 */
    min-height: 200px; /* 最小高度，避免内容过少时组件变得过小 */
  }
  
  .post 
  {
    margin-top: 1%;
    height: 88%; 
    margin-bottom: 0px;
  }

  .user {
    height: 600px; 
    margin-top:0px;
  }
  
  .word {
    height: 200px; 
    margin-bottom: 0;
  }
  
  .mood {
    height: 70%; 
    margin-top:0%;
  }
  
  @media (max-width: 768px) {
    .WXAnalyze {
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
  