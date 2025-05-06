<template> 
  <div class="wbAnalyze">
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
          <div class="blog_hot">
            <BlogHot />
          </div>
          <div class="topic_hot">
            <TopicHot />
          </div>
        </div>
        <div class="right">
          <div class="word">
            <WordCloud />
          </div>
          <div class="graph">
            <RelationGraph />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import SideBorder from "../components/Side_border";
import BlogHot from "../components/wbAnalyze/Blog_hot";
import DefaultPanel from "../components/wbAnalyze/Default_panel";
import RelationGraph from "../components/wbAnalyze/Relation_graph";
import Search from "../components/wbAnalyze/Search";
import TopicHot from "../components/wbAnalyze/post_time.vue";
import WordCloud from "../components/wbAnalyze/Word_cloud";

export default {
  name: "wbAnalyze",
  components: {
    BlogHot,
    DefaultPanel,
    RelationGraph,
    Search,
    TopicHot,
    WordCloud,
    // SideBorder,
  },
};
</script>

<style scoped>
/* 主容器 */
.wbAnalyze {
  display: flex;
  width: 100%;
  height: 100%; /* 使其填满整个视口 */
  background: linear-gradient(to right, #086264, #229fe2d6);
}

/* .side {
  width: 50px; /* 固定宽度 */
  /* height: 100%; /* 高度自适应 */


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
  height: 100%; /* 高度自适应 */
}

.center {
  flex: 1; /* 中间区域自适应宽度 */
  margin: 0 10px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.right {
  width: 23%; /* 右侧栏宽度 */
  height: 100%; /* 高度自适应 */
  position: relative;
  display: flex;
  flex-direction: column;
  /* 保证右侧区域的组件不被推到下方 */
  margin-top: 0;
  flex-shrink: 0; /* 保证右侧区域不会被压缩 */
}

.word {
  height: 40%; 
}

/* 每个小组件的容器 */
.blog_hot,
.topic_hot {
  
  width: 100%;
  margin-bottom: 10px;
  
  flex: 1; /* 自适应高度 */
  min-height: 200px; /* 最小高度，避免内容过少时组件变得过小 */
}

.topic_hot {
  height: 300px; 
  margin-top: 50px;
}


.graph {
  margin-top: 30%;
  height: 700px; 
}

@media (max-width: 768px) {
  .wbAnalyze {
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
    margin: 10px 0;
  }
}
</style>
