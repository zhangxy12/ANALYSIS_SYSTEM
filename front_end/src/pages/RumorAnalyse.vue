<template> 
  <div class="yyAnalyze">
    
      <!-- 返回按钮 -->
      <a href="/Rumor" class="back-button">
          <i class="fa fa-arrow-left"></i> 返回
      </a>
      <div class="container">
          <h1 class="dashboard-title" style="height: 10%;">谣言分析监控</h1>
          <div class="sub-title neon-text">
              关于「{{ key }}」的谣⾔数据
          </div>
          <div class="main">
              <div class="left">
                  <DefaultPanel />
              </div>
              <div class="center">
                <dv-border-box-2 style="height: 43%;">
                <div v-if="truth" class="truth-container">
                  <p class="truth-title">真相</p>
                  <p class="truth-text">{{ truth.truth }}</p>
                </div>
                <div v-else class="loading-container">
                  <p>正在获取数据，请稍候...</p>
                </div>
                </dv-border-box-2>
                  <div class="post" style=" height:500px; ">
                      <Post />
                  </div> 
              </div>
              <div class="right">
                  <div class="time">
                      <Time />
                  </div>
                  <div class = "apps"> 
                      <Apps />
                  </div>
              </div>
          </div>
      </div>
  </div>
</template>

<script>
import DefaultPanel from "../components/Rumor_ana/Default_panel";
import Time from "../components/Rumor_ana/time";
import Post from "../components/Rumor_ana/post";
import Apps from "../components/Rumor_ana/apps";
import axios from "axios";

export default {
  name: "yyAnalyze",
  components: {
      DefaultPanel,
      Time,
      Post,
      Apps
  },
  data(){
    return {
      key : '',
      truth: null
    }
    
  },
  mounted() {
      this.key = this.$route.query.key;
      this.fetchTruth();
  },
  methods: {
    async fetchTruth() {
      try {
        const response = await axios.get(`/rumor/rumorTruth?key=${this.key}`);
        console.log(response.data.data.truth);
        this.truth = response.data.data;
        if (response.data.code == 200) {
          this.truth = response.data.data;
        }  
        
      } catch (error) {
        console.error("获取真相失败", error);
        this.truth = { truth: "获取真相失败，请检查网络或稍后重试" };
      }
    }
  }
};
</script>

<style scoped>
/* 主容器 */
.yyAnalyze {
  display: flex;
  width: 99%;
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
  width: 99%;
  margin-left: 1%;
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
  display: flex;
  flex: 1; /* 占满剩余空间 */
  margin: 10px;
  height: 88%;
}

.left {
  width: 20%; /* 左侧栏宽度 */
  height: 98%; 
}

.center {
  width: 50%;
  height: 96%;
  margin: 15px 10px;
  margin-bottom: 0px;
  display:flex;
  flex-direction:column ;
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
.time,
.apps {
  width: 100%;
  margin-bottom: 0px;
  flex: 1; /* 自适应高度 */
  min-height: 200px; /* 最小高度，避免内容过少时组件变得过小 */
}

.post {
  margin-bottom: 0px;
  height: 45%;
}

.word {
  height: 30%; 
  margin-bottom: 0;
}

.apps {
  height: 90%; 
  margin-top:0%;
}

@media (max-width: 768px) {
  .yyAnalyze {
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

.truth-container {
  margin: 0px;
  padding: 5px;
  height: 30%;
 
  border-radius: 5px;
}

.truth-title {
  font-size: 24px;
  text-align: center;
  color: white;
  margin-bottom: 10px;
  font-weight: bold;
  text-shadow: 0 0 5px rgba(125, 248, 255, 0.175),
               0 0 10px rgba(125, 249, 255, 0.3);
}

.truth-text {
  margin-left: 20px;
  margin-right: 20px;
  font-size: 18px;
  color: white;
}

.loading-container {
  margin: 10px;
  padding: 10px;
  text-align: center;
  color: white;
}

</style>