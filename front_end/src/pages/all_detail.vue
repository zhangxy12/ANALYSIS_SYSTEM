<template> 
  <div class="tpAnalyze">
      <!-- 返回按钮 -->
      <a href="/all_view" class="back-button">
          <i class="fa fa-arrow-left"></i> 返回
      </a>
      <div class="container">
          <h1 class="dashboard-title" style="height: 10%;">话题分析详情</h1>
          <div class="sub-title neon-text">
              关于「{{ key }}」的话题数据
          </div>
          <div class="main" style="width: 100%;">
              <div class="left">
                  <DefaultPanel />
              </div>
              <div class="center">
                <div class = "relation"> 
                      <Relation />
                  </div>   
              </div>
              <div class="right">
                  <div class="time">
                      <Time />
                  </div>
                  <div class="ci" style="height: 56%;">
                      <Ci />
                  </div> 
                  
              </div>
          </div>
      </div>
  </div>
</template>

<script>
import DefaultPanel from "../components/all_detail/Default_panel";
import Time from "../components/all_detail/time";
import Ci from "../components/all_detail/ci";
import Relation from "../components/all_detail/Relation_graph";

export default {
  name: "tpAnalyze",
  components: {
      DefaultPanel,
      Time,
      Ci,
      Relation
  },
  data(){
    return {
      key : ''
    }
    
  },
  mounted() {
      this.key = this.$route.query.key;
      console.log(this.key);
  }
};
</script>

<style scoped>
/* 主容器 */
.tpAnalyze {
  
  display: flex;
  width: 100%;
  height: 100%; /* 使其填满整个视口 */
  background: linear-gradient(45deg, #256d6d,  #247b7b, #27aeb0);
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

.container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 95%;
  background-color: rgba(253, 251, 255, 0); /* 半透明背景色，便于看到背景图片 */
  position: relative;
}

/* 返回按钮样式 */
.back-button {
  position: absolute;
  top: 10px;
  left: 10px;
  display: inline-flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.3s ease;
  z-index: 2; /* 设置返回按钮的 z-index 为 2 */
}

.back-button:hover {
  background-color: rgba(255, 255, 255, 0.4);
}

.back-button i {
  margin-right: 5px;
}

.sub-title {
  font-size: 15px;
  color: #a2f4f8;
  margin-top: 8px;
  padding-left: 15px;
  position: relative;
  text-align: center; /* 副标题也居中 */
}

.neon-text {
  /* text-shadow: 
      0 0 5px rgba(125, 248, 255, 0.175),
      0 0 10px rgba(125, 249, 255, 0.3); */
}

.dashboard-title {
  /* 基础样式 */
  position: relative;
  font-size: 30px; /* 响应式字体 */
  text-align: center;
  padding: 15px 0;
  margin: 0;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
  
  /* 文字渐变效果 */
  background: #ffff;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 200% auto;
  animation: text-glow 5s linear infinite;

  /* 背景光效 */
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    height: 100%;
    background: linear-gradient(
      90deg,
      rgba(0, 240, 255, 0.1) 0%,
      rgba(157, 0, 255, 0.1) 100%
    );
    filter: blur(20px);
    z-index: -1;
  }

  /* 底部装饰线 */
  &::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 3px;
    background: linear-gradient(90deg, transparent, #00f0ff, transparent);
    box-shadow: 0 0 15px #00f0ff;
  }
  z-index: 1; /* 设置 h1 的 z-index 为 1 */
}

/* 文字渐变动画 */
@keyframes text-glow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .dashboard-title {
      font-size: 24px;
      padding: 15px 0;
  }
}

.main {
  margin-left: 2.5%;
  display: flex;
  height: 88%;
  width: 100%;
}

.left {
  width: 20%; /* 左侧栏宽度 */
  height: 98%; 
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
  width: 23%; /* 右侧栏宽度 */
  height: 98%; /* 高度自适应 */
  
}

/* 每个小组件的容器 */
.hot,
.ci,
.time,
.relation {

  width: 100%;
  margin-bottom: 0px;
  flex: 1; /* 自适应高度 */
  min-height: 200px; /* 最小高度，避免内容过少时组件变得过小 */
}

.ci {
  margin-top: 15px;
  
}
.time{
  height: 44%;
}
.word {
  height: 30%; 
  margin-bottom: 0;
}

.relation {
  height: 56%;
  margin-top: 2%; 
  margin-left: 30px;
}

@media (max-width: 768px) {
  .tpAnalyze {
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