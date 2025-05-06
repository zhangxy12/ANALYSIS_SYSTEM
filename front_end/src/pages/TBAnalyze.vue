<template> 
  <div class="TBAnalyze">
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
          <div class="post" style=" height: 30%; ">
            <Post />
          </div> 
          <div class="hot">
            <Detail />
          </div>
        </div>
        <div class="right">
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

import Search from "../components/TBAnalyze/Search";
import DefaultPanel from "../components/TBAnalyze/Default_panel";
import WordCloud from "../components/TBAnalyze/Word_cloud";
import Mood from "../components/TBAnalyze/mood";
import Post from "../components/TBAnalyze/post";
// import Hot from "../components/TBAnalyze/TB_hot";
import Detail from "../components/TBAnalyze/tiezi_detail";

export default {
  name: "TBAnalyze",
  components: {
    Search,
    DefaultPanel,
    WordCloud,
    Mood,
    Post,
    // Hot,
    Detail,
    // SideBorder,
  },
};
</script>

<style scoped>
/* 主容器 */
.TBAnalyze {
  display: flex;
  width: 99%;
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
  height: 102%; 
}

.center {
  width: 50%;
  height: 98%;
  margin: 15px 10px;
  margin-bottom: 0px;
  display:flex;
  flex-direction:column-reverse ;
  
}

.right {
  width: 27%; /* 右侧栏宽度 */
  height: 98%; /* 高度自适应 */
  
  position: relative;
  display: flex;
  flex-direction: column;
  /* 保证右侧区域的组件不被推到下方 */
  margin-top: 0;
  flex-shrink: 0; /* 保证右侧区域不会被压缩 */
}

/* 每个小组件的容器 */
.hot,
.post,
.word,
.mood {
  width: 100%;
  margin-bottom: 0px;
  flex: 1; /* 自适应高度 */
  min-height: 200px; /* 最小高度，避免内容过少时组件变得过小 */
}

.post 
{
 
  margin-bottom: 0px;
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
  .TBAnalyze {
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
