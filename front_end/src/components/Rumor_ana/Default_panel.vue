<template>
    <div class="default_panel">
      <!-- <div class="refresh" @click="refresh">
        <svg class="icon" aria-hidden="true">
          <use xlink:href="#icon-shuaxin"></use>
        </svg>
      </div> -->
      <div class="default_panel_top" style="height: 7%;">
        <span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-kanban" viewBox="0 0 16 16">
  <path d="M13.5 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-11a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zm-11-1a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>
  <path d="M6.5 3a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm-4 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1zm8 0a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1z"/>
</svg>
        </span>
        <span class="title_text"> 谣言详情 </span>
      </div>
      <div v-if="s_text_show" class="topics" style="height: 86%;">

        <!-- 微信搜索结果 -->
        <div v-if="results.wechat" class="wechat_results">
          <div class="result" v-for="(item, index) in filterItems(results.wechat, 'wechat')" :key="index">
            <div class="item-container">
              <div class="item-title">
                <a :href="`https://weixin.sogou.com${item.url}`" target="_blank">{{ item.title }}</a>
              </div>
              <div class="item-sentiment" :class="getSentimentClass(item.sentiment)">
                {{ getSentimentLabel(item.sentiment) }}
              </div>
              <div class="item-source">
                来源: 微信 {{ item.source }}
              </div>
              <div class="item-time">{{ item.time }}</div>
            </div>
          </div>
        </div>
  
        <!-- 微博搜索结果 -->
        <div v-if="results.weibo" class="weibo_results">
          <div class="result" v-for="(item, index) in filterItems(results.weibo, 'weibo')" :key="index">
            <div class="item-container">
              <div class="item-title">
                {{ item.text.slice(0, 20) + "..." | snippet }}
              </div>
              <div class="item-sentiment" :class="getSentimentClass(item.sentiment)">
                {{ getSentimentLabel(item.sentiment) }}
              </div>
              <div class="item-source">来源: 微博</div>
              <div class="item-time">{{ item.created_at }}</div>
            </div>
          </div>
        </div>

        <!-- 人民网搜索结果 -->
        <div v-if="results.renmin" class="renmin_results">
          <div class="result" v-for="(item, index) in filterItems(results.renmin, 'renmin')" :key="index">
            <div class="item-container">
              <div class="item-title">
                <a :href="item.url" target="_blank">{{ item.title }}</a>
              </div>
              <div class="item-sentiment" :class="getSentimentClass(item.sentiment)">
                {{ getSentimentLabel(item.sentiment) }}
              </div>
              <div class="item-source">来源: 人民网</div>
              <div class="item-time">{{ item.displayTime }}</div>
            </div>
          </div>
        </div>
  
        <!-- 贴吧搜索结果 -->
        <div v-if="results.tieba" class="tieba_results">
          <div class="result" v-for="(item, index) in filterItems(results.tieba, 'tieba')" :key="index">
            <div class="item-container">
              <div class="item-title">
                <a :href="item.url" target="_blank">{{ item.title }}</a>
              </div>
              <div class="item-sentiment" :class="getSentimentClass(item.sentiment)">
                {{ getSentimentLabel(item.sentiment) }}
              </div>
              <div class="item-source">来源: 贴吧</div>
              <div class="item-time">{{ item.time }}</div>
            </div>
          </div>
        </div>
  
        
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        key: '',
        s_text_show: true,
        results: {},
        key_word: '',
        currentKeyWord: '',
        searchResult: false,
        loading: false
      };
    },
    mounted() {
      this.key = this.$route.query.key;
      console.log(this.key);
      if (this.key) {
        this.key_word = this.key;
        this.search();
      }
    },
    methods: {
      async search() {
        this.loading = true; // 开始加载，显示加载动画
        if (!this.key_word) {
          this.$message.error("请输入搜索关键词！");
          return;
        }
  
        // 如果当前关键词和之前的不同，进行搜索
        if (this.key_word!== this.currentKeyWord) {
          this.searchResult = true;
          this.results = {}; // 清空旧结果
          this.currentKeyWord = this.key_word; // 更新当前搜索关键词
        }
  
        const results = { renmin: [], weibo: [], tieba: [], wechat: [] };
        let cursor = 1; // 从第一页开始
        let hasMoreData = true; // 标记是否还有更多数据
  
        try {
          while (hasMoreData && cursor <= 1) { // 只爬取指定页数
            const response = await this.$axios.get(
              `/rumor/rumorAnalyse?key=${this.key_word}&cursor=${cursor}`
            );
            const pageData = response.data.data;
            console.log(pageData)
  
            if (!pageData.renmin &&!pageData.weibo &&!pageData.tieba &&!pageData.wechat) {
              this.$message.warning(`第 ${cursor} 页没有更多结果`);
              break;
            }
  
            // 合并数据并添加情感标签
            if (pageData.renmin) {
              pageData.renmin.forEach(item => {
                item.sentiment = item.sentiment || 0; // 获取后端返回的情感得分
              });
              results.renmin.push(...pageData.renmin);
            }
  
            if (pageData.tieba) {
              pageData.tieba.forEach(item => {
                item.sentiment = item.sentiment || 0; // 获取后端返回的情感得分
              });
              results.tieba.push(...pageData.tieba);
            }
  
            if (pageData.wechat) {
              pageData.wechat.forEach(item => {
                item.sentiment = item.sentiment || 0; // 获取后端返回的情感得分
              });
              results.wechat.push(...pageData.wechat);
            }
  
            if (pageData.weibo?.result) {
              pageData.weibo.result.forEach(item => {
                item.sentiment = item.sentiment || 0; // 获取后端返回的情感得分
              });
              results.weibo.push(...pageData.weibo.result);
            }
  
            // 判断是否继续爬取
            hasMoreData = pageData.renmin?.length > 0 || pageData.weibo?.result?.length > 0 || pageData.tieba?.length > 0 || pageData.wechat?.length > 0;
            cursor++; // 下一页
          }
  
          this.results = results;
  
          if (results.renmin.length === 0 && results.weibo.length === 0 && results.tieba.length === 0 && results.wechat.length === 0) {
            this.$message.error("没有找到相关结果");
          }
  
        } catch (error) {
          console.error("搜索失败", error);
          this.$message.error("搜索失败，请稍后再试！");
        } finally {
          this.loading = false; // 加载完成，隐藏加载动画
        }
      },
      refresh() {
        this.search();
      },
      filterItems(items, source) {
        // 这里可以添加过滤逻辑，目前直接返回原数据
        return items;
      },
      getSentimentClass(sentiment) {
        if (sentiment === 1) {
          return 'positive';
        } else if (sentiment === 0) {
          return 'negative';
        } else {
          return 'neutral';
        }
      },
      getSentimentLabel(sentiment) {
        if (sentiment === 1) {
          return '积极';
        } else if (sentiment === 0) {
          return '消极';
        } else {
          return '中立';
        }
      },
    },
    filters: {
      snippet(value) {
        return value;
      }
    }
  };
  </script>
  
  
  
  <style scpoed>
  .delete i {
    color: #ffffff; /* 设置图标颜色为白色 */
  }
  .default_panel {
    height: 100%;
    width: 100%;
    background-color: #ffffff00;
    color: #ffff;
    border: 2px solid #fefeff6a; /* 深色边框 */
    border-radius: 10px;
    border: 2px solid #669ef3a5; /* 深色边框 */
    border-radius: 10px;
    
    box-sizing: border-box;
    background: #3aba9e08; /* 背景颜色 */
    box-shadow: 0 0 15px rgba(233, 229, 238, 0.304), 0 0 25px rgba(63, 154, 87, 0.4); /* 外阴影 */
  }
  .default_panel_top {
    padding-top: 20px;
    height: 50px;
    text-align: center;
    font-size: 20px;
  }
 
  .line {
    margin-top: 4px;
    background-color: #eee;
    border: 1px solid #eee;
    width: 110%;
  }

  
.renmin_results,
.tieba_results,
.wechat_results,
.weibo_results {
  margin-bottom: 1px;
  padding: 8px;
  /* border: 1px solid #ffffff;
  border-radius: 5px; */
}

.result {
  margin-bottom: 1px;
  padding: 10px;
  /* border: 1px solid #eeeeee00;
  border-radius: 5px; */
}

.item-container {
  display: flex;
  flex-direction: column;
}

.item-title a {
  color: #ffffff;
  text-decoration: none;
}

.item-title a:hover {
  text-decoration: underline;
}
.item-sentiment {
  margin-top: 11px;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
  /* align-items: center; */
}
.item-sentiment.positive {
  background-color: #268f3f;
  color: #fff;
}

.item-sentiment.neutral {
  background-color: #3d5162;
  color: #fff;
}

.item-sentiment.negative {
  background-color: #d15662;
  color: #fff;
}

.item-source,
.item-time {
  margin-top: 5px;
  font-size: 14px;
  color: #968d8d;
}

    .refresh {
    float: right;
    }
    .refresh .icon {
    width: 20px;
    height: 20px;
    }
    .loader {
    margin-left: 20px;
    width: 20px;
    height: 49px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    animation: roating 2s linear infinite;
    }
    @keyframes roating {
    0%,
    90% {
    transform: rotate(0deg);
    }
    100% {
    transform: rotate(180deg);
    }
    }
    .loader::after {
    content: "";
    position: absolute;
    width: 1px;
    height: 24px;
    background-color: deepskyblue;
    top: 5px;
    animation: flow 2s linear infinite;
    }
    @keyframes flow {
    10%,
    100% {
    transform: translateY(16px);
    }
    }
    .loader_top,
    .loader_bottom {
    width: 17px;
    height: 17px;
    border-style: solid;
    border-color: rgb(255, 255, 255);
    border-width: 1px 1px 3px 3px;
    border-radius: 50% 100% 50% 30%;
    position: relative;
    overflow: hidden;
    }
    .loader_top {
    transform: rotate(-45deg);
    }
    .loader_bottom {
    transform: rotate(135deg);
    }
    .loader_top::before,
    .loader_bottom::before {
    content: "";
    position: absolute;
    width: inherit;
    height: inherit;
    background-color: deepskyblue;
    animation: 2s linear infinite;
    }
    .loader_top::before {
    border-radius: 0 100% 0 0;
    animation-name: drop-sand;
    }
    @keyframes drop-sand {
    to {
    transform: translate(-12px, 12px);
    }
    }
    .loader_bottom::before {
    border-radius: 0 0 0 35%;
    animation-name: fill-sand;
    transform: translate(12px, -12px);
    }
    @keyframes fill-sand {
    to {
    transform: translate(0, 0);
    }
    }
    .loader_text {
    margin-left: 20px;
    margin-top: 15px;
    background: linear-gradient(to right, #39ec22, #099cb6);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    }
    .analyze {
    display: flex;
    }
    .topic_wait {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    }
    .topic_wait .box {
    position: relative;
    width: 50px;
    height: 50px;
    animation: rotatBox 10s linear infinite;
    }
    @keyframes rotatBox {
    0% {
    transform: rotate(0deg);
    }
    100% {
    transform: rotate(360deg);
    }
    }
    .topic_wait .box .circle {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #38c1ff;
    border-radius: 50%;
    animation: animate 5s linear infinite;
    }
    .topic_wait .box .circle:nth-child(2) {
    background: #ff3378;
    animation-delay: -2.5s;
    }
    @keyframes animate {
    0% {
    transform: scale(1);
    transform-origin: left;
    }
    50% {
    transform: scale(0);
    transform-origin: left;
    }
    50.01% {
    transform: scale(0);
    transform-origin: right;
    }
    100% {
    transform: scale(1);
    transform-origin: right;
    }
    }
    .topic_wait h2 {
    margin-top: 20px;
    font-size: 20px;
    font-weight: 400;
    letter-spacing: 4px;
    color: #ffffff;
    }
    </style>