<template>
    <div class="all_view">
      <div class="side">
        <SideBorder />
      </div>
  
      <div class="main-content">
      <!-- 顶部搜索区域 -->
      <div class="search-area">
        <div class="input-wrapper">
          <div class="input">
            <input type="text" v-model="key_word" class="key" placeholder="搜索话题" />
          </div>
          <div class="action-buttons">
            <button @click="search" class="tech-button">搜索</button>
          </div>

          <!-- 历史搜索框 -->
        <div class="history-panel" >
          <div class="history-header">
            <span>搜索历史</span>
          </div>
          <div class="history-list">
            <div class="history-item" v-for="(topic, index) in historySearchTopics" :key="index">
              <span @click="searchHistory(topic)">{{ topic }}</span>
              <i class="el-icon-close" @click.stop="deleteHistory(topic)"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
      

        <div class="filter-bar">
        <!-- 时间筛选 -->
        <div class="filter-group">
          <span class="filter-label">时间：</span>
          <button 
            v-for="time in timeFilters" 
            :key="time.value"
            @click="toggleFilter('time', time.value)"
            :class="{active: selectedTime === time.value}"
          >
            {{ time.label }}
          </button>
        </div>

        <!-- 情感筛选 -->
        <div class="filter-group">
          <span class="filter-label">情感：</span>
          <button 
            v-for="sentiment in sentimentFilters" 
            :key="sentiment.value"
            @click="toggleFilter('sentiment', sentiment.value)"
            :class="{active: selectedSentiment === sentiment.value}"
          >
            {{ sentiment.label }}
          </button>
        </div>

        <!-- 来源筛选 -->
        <div class="filter-group">
          <span class="filter-label">来源：</span>
          <button
            v-for="source in sourceFilters"
            :key="source.value"
            @click="toggleFilter('source', source.value)"
            :class="{active: selectedSources.includes(source.value)}"
          >
            {{ source.label }}
          </button>
        </div>
      </div>

         <!-- 加载动画 -->
         <div v-if="loading" class="loading-overlay">
          <div class="wavy">
            <span style="--i:1;">l</span>
            <span style="--i:2;">o</span>
            <span style="--i:3;">a</span>
            <span style="--i:4;">d</span>
            <span style="--i:5;">i</span>
            <span style="--i:6;">n</span>
            <span style="--i:7;">g</span>
            <span style="--i:8;">.</span>
            <span style="--i:9;">.</span>
            <span style="--i:10;">.</span>
          </div>
        </div>

        <!-- 搜索结果 -->
        <div class="searchResult" v-show="searchResult">
          <div class="title">
            有关{{ key_word }}的话题
            <button @click="renderCharts" class="tech-button">去分析</button>
            <button @click="goToDetailPage" class="tech-button">查看详情</button>
            <div class="close" @click="searchResult = false">
              <i class="el-icon-close"></i>
            </div>
          </div>
  
          <!-- 人民网搜索结果 -->
          <div v-if="results.renmin" class="renmin_results">
            <div class="result" v-for="(item, index) in filterItems(results.renmin, 'renmin')" :key="index">
              <!-- <div class="result" v-for="(item, index) in results.renmin" :key="index"> -->
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
              <!-- </div> -->
            </div>
          </div>
  
          <!-- 贴吧搜索结果 -->
          <div v-if="results.tieba" class="tieba_results">
            <div class="result" v-for="(item, index) in filterItems(results.tieba, 'tieba')" :key="index">
              <!-- <div class="result" v-for="(item, index) in results.tieba" :key="index"> -->
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
              <!-- </div> -->
            </div>
          </div>

          <!-- 微信搜索结果 -->
          <div v-if="results.wechat" class="wechat_results">
            <div class="result" v-for="(item, index) in filterItems(results.wechat, 'wechat')" :key="index">
              <!-- <div class="result" v-for="(item, index) in results.wechat" :key="index"> -->
                <div class="item-container">
                  <div class="item-title">
                      <a :href="`https://weixin.sogou.com${item.url}`"  target="_blank">{{ item.title }}</a>
                  </div>
                  <div class="item-sentiment" :class="getSentimentClass(item.sentiment)">
                    {{ getSentimentLabel(item.sentiment) }}
                  </div>
                  <div class="item-source">
                      来源: 微信 {{ item.source }}
                  </div>
                  <div class="item-time">{{ item.time }}</div>
                </div>
              <!-- </div> -->
            </div>
          </div>
  
          <!-- 微博搜索结果 -->
          <div v-if="results.weibo" class="weibo_results">
            <div class="result" v-for="(item, index) in filterItems(results.weibo, 'weibo')" :key="index">
              <!-- <div class="result" v-for="(item, index) in results.weibo" :key="index"> -->
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
              <!-- </div> -->
            </div>
          </div>

        </div>

        <!-- 分析图表 -->
      <div class="analysis-charts" v-if="showAnalysis">
        <div class="close-charts" @click="closeAnalysis">
          <i class="el-icon-circle-close"></i>
        </div>
        <!-- 信息来源占比图（饼状图） -->
        <div class="chart-container">
          <div ref="sourceChart" style="width: 100%; height: 260px;"></div>
        </div>

        <!-- 发布时间折线图 -->
        <div class="chart-container">
          <div ref="timeLineChart" style="width: 100%; height: 260px;"></div>
        </div>

        <!-- 情感分析占比图 -->
        <div class="chart-container">
          <div ref="sentimentChart" style="width: 100%; height: 260px;"></div>
        </div>

        <!-- 情感分析随时间变化折线图 -->
        <div class="chart-container">
          <div ref="sentimentTimeChart" style="width: 100%; height: 260px;"></div>
        </div>
    </div>
    </div>  
    </div>
  </template>
  
  <script>
  import SideBorder from "../components/Side_border";
  import * as echarts from 'echarts';
  import axios from "axios";

  export default {
    name: "search",
    
    data() {
      return {
        key_word: "",
        loading: false, // 控制加载状态
        searchResult: true,
        results: {},
        showAnalysis: false, // 用来控制图表的显示
        timeFilters: [
          { label: '一周内', value: 'week' },
          { label: '一个月内', value: 'month' },
          { label: '一年内', value: 'year' }
        ],
        sentimentFilters: [
          { label: '积极', value: 'positive' },
          { label: '中性', value: 'neutral' },
          { label: '消极', value: 'negative' }
        ],
        sourceFilters: [
          { label: '微博', value: 'weibo' },
          { label: '人民网', value: 'renmin' },
          { label: '微信', value: 'wechat' },
          { label: '贴吧', value: 'tieba' }
        ],
        selectedTime: null,
        selectedSentiment: null,
        selectedSources: [],
        //historySearchList: [], // 历史搜索列表
        historySearchTopics: [], // 新的历史搜索主题列表
        currentKeyWord: ""
      };
    },
    components: {
      SideBorder,
    },
    // 组件挂载后调用 getHistorySearch 方法
    mounted() {
    this.$nextTick(() => {
        this.getHistorySearch();
    });
    },
    

    filters: {
      snippet(value) {
        if (value.length > 200) return value.slice(0, 200) + "...";
        return value;
      }
    },
    
    methods: {
      goToDetailPage() {
      // 使用 this.$router.push 进行路由跳转并传递话题参数
      this.$router.push({
        path: '/all_detail',
        query: {
          key: this.key_word
        }
      });
    },
    
      // 获取情感标签
      getSentimentLabel(sentiment) {
        if (sentiment > 0.7) return '积极';
        if (sentiment < 0.3) return '消极';
        return '中性';
      },
  
      // 获取情感标签的CSS类
      getSentimentClass(sentiment) {
        if (sentiment > 0.7) return 'positive';
        if (sentiment < 0.3) return 'negative';
        return 'neutral';
      },
  
      async search() {
        this.loading = true; // 开始加载，显示加载动画
        if (!this.key_word) {
          this.$message.error("请输入搜索关键词！");
          return;
        }
  
        // 如果当前关键词和之前的不同，进行搜索
        if (this.key_word !== this.currentKeyWord) {
          this.searchResult = true;
          this.results = {}; // 清空旧结果
          this.currentKeyWord = this.key_word; // 更新当前搜索关键词
          // 添加历史搜索记录
          await this.saveHistorySearch(this.key_word);
          await this.getHistorySearch();
        }
  
        const results = { renmin: [], weibo: [], tieba: [], wechat: [] };
        let cursor = 1; // 从第一页开始
        let hasMoreData = true; // 标记是否还有更多数据
  
        try {
          while (hasMoreData && cursor <= 1) { // 只爬取指定页数
            const response = await this.$axios.get(
              `multi_search?tag=${this.key_word}&cursor=${cursor}`
            );
            const pageData = response.data.data;
            console.log(pageData)
  
            if (!pageData.renmin && !pageData.weibo && !pageData.tieba && !pageData.wechat) {
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
        }finally {
        this.loading = false; // 加载完成，隐藏加载动画
      }
      },
       // 获取历史搜索内容
       async getHistorySearch() {
            try {
                const response = await axios.get('/history_topic');
                console.log('response.data.code 的类型：', typeof response.data.code);
                if (response.data.code === 200) {
                  console.log(response.data);
                    // 将获取到的 topic 追加到历史搜索主题列表后面
                    const newTopics = this.historySearchTopics.concat(response.data.data.topic);
                    this.historySearchTopics = [...newTopics];
                    console.log('更新后的 historySearchTopics：', this.historySearchTopics);
                }
            } catch (error) {
                console.error('获取历史搜索内容失败', error);
            }
        },

    // 保存历史搜索记录到后端
    async saveHistorySearch(tag) {
      try {
        const response = await axios.post('/save_history_search', {
          tag: tag
        });
        if (response.data.message === "保存成功") {
          console.log("历史搜索记录保存成功");
        } else {
          console.error("历史搜索记录保存失败");
        }
      } catch (error) {
        console.error("保存历史搜索记录失败", error);
      }
    },

   // 点击展示历史搜索内容
    async searchHistory(tag) {
      this.key_word = tag;
      try {
        const response = await axios.get('/history_search', {
          params: {
            tag: this.key_word
          }
        });
        console.log(response);
        if (response.data.code === 200) {
          // 获取后端返回的数据
          let data = response.data.data;
          // 检查 data 中的 weibo 字段是否为数组，如果不是则将其设为空数组
          if (!Array.isArray(data.weibo)) {
            data.weibo = [];
          }
          this.results = data;
          console.log(this.results);
        }
      } catch (error) {
        console.error("获取历史搜索失败", error);
      }
    },

    // 删除历史搜索内容
    async deleteHistory(tag) {
      try {
        const response = await axios.get('/history_del', {
          params: {
            tag: tag
          }
        });
        console.log(response);
        if (response.data.code === 200) {
          this.historySearchTopics = this.historySearchTopics.filter(item => item !== tag);
        } else {
          this.$message.error("删除历史记录失败");
        }
      } catch (error) {
        console.error("删除历史搜索失败", error);
        this.$message.error("删除历史记录失败");
      }
    },

      // 筛选切换逻辑
  toggleFilter(type, value) {
    switch(type) {
      case 'time':
        this.selectedTime = this.selectedTime === value ? null : value
        break
      case 'sentiment':
        this.selectedSentiment = this.selectedSentiment === value ? null : value
        break
      case 'source':
        if (this.selectedSources.includes(value)) {
          this.selectedSources = this.selectedSources.filter(s => s !== value)
        } else {
          this.selectedSources = [...this.selectedSources, value]
        }
        break
    }
  },

  // 过滤逻辑
  filterItems(items, sourceType) {
    const now = new Date()
    return items.filter(item => {
      // 时间过滤
      if (this.selectedTime) {
        const itemDate = new Date(
          sourceType === 'weibo' ? item.created_at : 
          sourceType === 'renmin' ? item.displayTime : 
          item.time
        )
        const timeDiff = now - itemDate
        
        const ranges = {
          week: 7 * 24 * 60 * 60 * 1000,
          month: 30 * 24 * 60 * 60 * 1000,
          year: 365 * 24 * 60 * 60 * 1000
        }
        if (timeDiff > ranges[this.selectedTime]) return false
      }

      // 情感过滤
      if (this.selectedSentiment) {
        const sentimentValue = item.sentiment || 0
        const sentimentMap = {
          positive: sentimentValue > 0.7,
          neutral: sentimentValue >= 0.3 && sentimentValue <= 0.7,
          negative: sentimentValue < 0.3
        }
        if (!sentimentMap[this.selectedSentiment]) return false
      }

      // 来源过滤
      if (this.selectedSources.length > 0 && 
          !this.selectedSources.includes(sourceType)) {
        return false
      }

      return true
    })
  },

      renderCharts() {
      this.showAnalysis = true; // 显示图表

      this.$nextTick(() => {
    // 在这里初始化 ECharts 图表
    const renminCount = this.results.renmin? this.results.renmin.length : 0;
    const weiboCount = this.results.weibo? this.results.weibo.length : 0;
    const tiebaCount = this.results.tieba? this.results.tieba.length : 0;
    const wechatCount = this.results.wechat? this.results.wechat.length : 0;

    const total = renminCount + weiboCount + tiebaCount + wechatCount;
    console.log(this.$refs.sourceChart);
    if (this.$refs.sourceChart) {
      const sourceChart = this.$echarts.init(this.$refs.sourceChart);
      const sourceOption = {
        title: {
          text: '信息来源占比',
          left: 'center',
          top: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal',
            color: '#fff'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [
          {
            name: '信息来源',
            type: 'pie',
            radius: '50%',
            data: [
              { value: renminCount, name: '人民网' },
              { value: weiboCount, name: '微博' },
              { value: tiebaCount, name: '贴吧' },
              { value: wechatCount, name: '微信' },
            ],
            color: ['#a4e2c6', '#48c0a3', '#549688', '#1685a9'],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      sourceChart.setOption(sourceOption);
    } else {
      console.error('sourceChart element not found');
    }

    const timeData = this.calculateTimeData();
    const timeLineChart = this.$echarts.init(this.$refs.timeLineChart);
    const timeLineOption = {
        title: {
            text: '发布时间趋势',
            left: 'center',
            top: 'top',
            textStyle: {
                color: '#fff'
            }
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['人民网', '微博', '贴吧', '微信'],
            top: '10%',
            textStyle: {
                color: '#fff'
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: timeData.labels,
            axisLabel: {
                color: '#fff'
            }
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: '{value} 条',
                color: '#fff'
            },
            axisTick: {
                alignWithLabel: true
            },
            minInterval: 1 // 设置最小刻度间隔为1，确保显示整数
        },
        grid: {
            top: '15%',
            left: '10%',
            right: '8%',
            bottom: '20%'
        },
        series: [
            {
                name: '人民网',
                type: 'line',
                data: timeData.renmin,
                smooth: true,
                color: '#a4e2c6',
                
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0,
                                color: 'rgba(164, 226, 198, 0.5)' // 与折线颜色相同，半透明
                            },
                            {
                                offset: 1,
                                color: 'rgba(164, 226, 198, 0)' // 完全透明
                            }
                        ]
                    }
                }
            },
            {
                name: '微博',
                type: 'line',
                data: timeData.weibo,
                smooth: true,
                color: '#48c0a3',
                
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0,
                                color: 'rgba(72, 192, 163, 0.5)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(72, 192, 163, 0)'
                            }
                        ]
                    }
                }
            },
            {
                name: '贴吧',
                type: 'line',
                data: timeData.tieba,
                smooth: true,
                color: '#549688',
                
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0,
                                color: 'rgba(84, 150, 136, 0.5)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(84, 150, 136, 0)'
                            }
                        ]
                    }
                }
            },
            {
                name: '微信',
                type: 'line',
                data: timeData.wechat,
                smooth: true,
                color: '#1685a9',
                
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0,
                                color: 'rgba(22, 133, 169, 0.5)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(22, 133, 169, 0)'
                            }
                        ]
                    }
                }
            }
        ]
    };
    timeLineChart.setOption(timeLineOption);

      // 情感分析占比图
    const sentimentData = this.calculateSentimentData();
    const sourceSentimentData = this.calculateSourceSentimentData();

    const sentimentChart = this.$echarts.init(this.$refs.sentimentChart);
    const sentimentOption = {
        title: {
            text: '情感分析占比',
            left: 'center',
            top: 'center',
            textStyle: {
                fontSize: 16,
                fontWeight: 'normal',
                color: '#fff'
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [
        // 外圈：总的情感占比
        {
            name: '总情感分析',
            type: 'pie',
            radius: ['52%', '65%'],
            data: sentimentData,
            color: ['#56c184', '#32c596', '#42ca7d'],
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)',
                }
            },
            itemStyle: {
                // 设置边框宽度来实现扇形之间的间隔
                borderWidth: 3, 
                // 边框颜色，这里使用白色，可根据背景色调整
                borderColor: '#15bac000', 
                // 设置外圈圆环的圆角半径
                borderRadius: 15 
            },
        },
        // 内圈：四个来源的情感占比
        {
            name: '来源情感分析',
            type: 'pie',
            radius: ['42%', '50%'],
            data: sourceSentimentData,
            color: [
                '#a4e2c6', '#48c0a3', '#549688', '#1685a9',
                '#a4e2c6', '#48c0a3', '#549688', '#1685a9',
                '#a4e2c6', '#48c0a3', '#549688', '#1685a9',
            ],
            label: {
                show: false,
                formatter: '{b}',
                position: 'inside',
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            },
        }
    ]
    };
    sentimentChart.setOption(sentimentOption);
        
      // 情感分析随时间变化折线图
      const sentimentTimeData = this.calculateSentimentTimeData();
      const sentimentTimeChart = this.$echarts.init(this.$refs.sentimentTimeChart);
      const sentimentTimeOption = {
          title: {
              text: '情感分析随时间变化',
              left: 'center',
              top: 'top',
              textStyle: {
                  color: '#fff'
              }
          },
          tooltip: {
              trigger: 'axis'
          },
          legend: {
              data: ['积极', '中性', '消极'],
              top: '10%',
              textStyle: {
                  color: '#fff'
              }
          },
          xAxis: {
              type: 'category',
              boundaryGap: false,
              data: sentimentTimeData.labels,
              axisLabel: {
                  color: '#fff'
              }
          },
          yAxis: {
              type: 'value',
              axisLabel: {
                  formatter: '{value} 条',
                  color: '#fff'
              },
              axisTick: {
                  alignWithLabel: true
              },
              minInterval: 1 // 设置最小刻度间隔为1，确保显示整数
          },
          series: [
              {
                  name: '积极',
                  type: 'line',
                  data: sentimentTimeData.positive,
                  smooth: true,
                  color: '#a4e2c6',
                 
                  // 添加阴影色块，使用与折线相同颜色的渐变
                  areaStyle: {
                      color: {
                          type: 'linear',
                          x: 0,
                          y: 0,
                          x2: 0,
                          y2: 1,
                          colorStops: [
                              {
                                  offset: 0,
                                  color: 'rgba(164, 226, 198, 0.5)'
                              },
                              {
                                  offset: 1,
                                  color: 'rgba(164, 226, 198, 0)'
                              }
                          ]
                      }
                  }
              },
              {
                  name: '中性',
                  type: 'line',
                  data: sentimentTimeData.neutral,
                  smooth: true,
                  color: '#48c0a3',
            
                  // 添加阴影色块，使用与折线相同颜色的渐变
                  areaStyle: {
                      color: {
                          type: 'linear',
                          x: 0,
                          y: 0,
                          x2: 0,
                          y2: 1,
                          colorStops: [
                              {
                                  offset: 0,
                                  color: 'rgba(72, 192, 163, 0.5)'
                              },
                              {
                                  offset: 1,
                                  color: 'rgba(72, 192, 163, 0)'
                              }
                          ]
                      }
                  }
              },
              {
                  name: '消极',
                  type: 'line',
                  data: sentimentTimeData.negative,
                  smooth: true,
                  color: '#549688',
                
                  // 添加阴影色块，使用与折线相同颜色的渐变
                  areaStyle: {
                      color: {
                          type: 'linear',
                          x: 0,
                          y: 0,
                          x2: 0,
                          y2: 1,
                          colorStops: [
                              {
                                  offset: 0,
                                  color: 'rgba(84, 150, 136, 0.5)'
                              },
                              {
                                  offset: 1,
                                  color: 'rgba(84, 150, 136, 0)'
                              }
                          ]
                      }
                  }
              }
          ]
      };
      sentimentTimeChart.setOption(sentimentTimeOption);
    });
  },

    calculateSentimentData() {
      const sentiments = [...this.results.renmin, ...this.results.weibo, ...this.results.tieba, ...this.results.wechat].map(item => item.sentiment);
      const positiveCount = sentiments.filter(sentiment => sentiment > 0.7).length;
      const neutralCount = sentiments.filter(sentiment => sentiment >= 0.3 && sentiment <= 0.7).length;
      const negativeCount = sentiments.filter(sentiment => sentiment < 0.3).length;

      const totalCount = sentiments.length;
      return [
        { value: positiveCount, name: '积极' },
        { value: neutralCount, name: '中性' },
        { value: negativeCount, name: '消极' }
      ];
    },

    // 计算四个来源的情感占比
    // 计算四个来源在各情感下的占比
    calculateSourceSentimentData() {
        const sources = ['renmin', 'weibo', 'tieba', 'wechat'];
        const sourceData = [];

        const allSentiments = {
            positive: [],
            neutral: [],
            negative: []
        };

        sources.forEach(source => {
            const sentiments = this.results[source].map(item => item.sentiment);
            allSentiments.positive.push(sentiments.filter(sentiment => sentiment > 0.7).length);
            allSentiments.neutral.push(sentiments.filter(sentiment => sentiment >= 0.3 && sentiment <= 0.7).length);
            allSentiments.negative.push(sentiments.filter(sentiment => sentiment < 0.3).length);
        });

        const addSourceData = (sentimentType, color) => {
            sources.forEach((source, index) => {
                sourceData.push({
                    value: allSentiments[sentimentType][index],
                    name: `${source} - ${sentimentType}`
                });
            });
        };

        addSourceData('positive', '#a4e2c6');
        addSourceData('neutral', '#48c0a3');
        addSourceData('negative', '#549688');

        return sourceData;
    },

    calculateSentimentTimeData() { 
    const renminSentimentTimes = this.results.renmin.map(item => ({ time: item.displayTime, sentiment: item.sentiment }));
    console.log(renminSentimentTimes);
    const weiboSentimentTimes = this.results.weibo.map(item => ({ time: item.created_at, sentiment: item.sentiment }));
    const tiebaSentimentTimes = this.results.tieba.map(item => ({ time: item.time, sentiment: item.sentiment }));
    const wechatSentimentTimes = this.results.wechat.map(item => ({ time: item.time, sentiment: item.sentiment }));

    const allSentiments = [...renminSentimentTimes, ...weiboSentimentTimes, ...tiebaSentimentTimes, ...wechatSentimentTimes];
    
    // 时间格式化为 'YYYY-MM'
    const formatToMonth = (time) => {
        const date = new Date(time);
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    };

    // 格式化所有时间为月份
    const timeLabels = [...new Set(allSentiments.map(item => formatToMonth(item.time)))].sort();

    const positive = timeLabels.map(label => 
        allSentiments.filter(item => formatToMonth(item.time) === label && item.sentiment > 0.7).length
    );
    
    const neutral = timeLabels.map(label => 
        allSentiments.filter(item => formatToMonth(item.time) === label && item.sentiment >= 0.3 && item.sentiment <= 0.7).length
    );
    
    const negative = timeLabels.map(label => 
        allSentiments.filter(item => formatToMonth(item.time) === label && item.sentiment < 0.3).length
    );

    return {
        labels: timeLabels,
        positive: positive,
        neutral: neutral,
        negative: negative
    };
    },

    calculateTimeData() {
    // 将时间转化为月份（'YYYY-MM'）
    const renminTime = this.results.renmin.map(item => item.displayTime);
    console.log(renminTime);
    const weiboTime = this.results.weibo.map(item => item.created_at);
    const tiebaTime = this.results.tieba.map(item => item.time);
    const wechatTime = this.results.wechat.map(item => item.time);

    // 格式化时间为月份
    const formatToMonth = (time) => {
        const date = new Date(time);
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    };

    // 将所有时间转换为月份
    const timeLabels = [...new Set([...renminTime, ...weiboTime, ...tiebaTime, ...wechatTime].map(formatToMonth))].sort();

    const renmin = timeLabels.map(label => renminTime.filter(item => formatToMonth(item) === label).length);
    const weibo = timeLabels.map(label => weiboTime.filter(item => formatToMonth(item) === label).length);
    const tieba = timeLabels.map(label => tiebaTime.filter(item => formatToMonth(item) === label).length);
    const wechat = timeLabels.map(label => wechatTime.filter(item => formatToMonth(item) === label).length);

    return {
        labels: timeLabels,
        renmin: renmin,
        weibo: weibo,
        tieba: tieba,
        wechat: wechat
    };
    },

    closeAnalysis() {
      this.showAnalysis = false;
    }
  },
  
};
</script>

<style scoped>
.filter-bar {
  height: 5%;
  margin: 15px 0;
  padding: 7px;
  background: #fafafa00;
  border-radius: 4px;
  display: flex; /* 使用 Flexbox 布局 */
  flex-wrap: wrap; /* 允许换行 */
  align-items: center; /* 垂直居中对齐 */
}

.filter-group {
  display: flex;
  align-items: center;
  margin: 0 10px; /* 调整筛选组之间的间距 */
}

.filter-label {
  font-weight: 600;
  margin-right: 7px;
  color: #ffffff;
}

button {
  margin: 0 3px;
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #ffffffc0;
  cursor: pointer;
  transition: all 0.3s;
}

button.active {
  background: #4fb17a;
  color: rgb(0, 0, 0);
  border-color: #409eff;
}

button:hover {
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.tech-button {
    
    /* 布局 */
    padding: 12px 20px;
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    
    /* 文字 */
    font-size: 15px;
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
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7); /* 半透明黑色背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999; /* 确保在最上层 */
}

.wavy {
  position: relative;
  -webkit-box-reflect: below -12px linear-gradient(transparent, rgba(0, 0, 0, 0.2));
}

.wavy span {
  position: relative;
  display: inline-block;
  color: #fff;
  font-size: 50px;
  text-transform: uppercase;
  letter-spacing: 8px;
  animation: wavyAnimate 1s ease-in-out infinite;
  animation-delay: calc(0.1s * var(--i));
}

@keyframes wavyAnimate {
  0% {
    transform: translateY(0);
  }
  20% {
    transform: translateY(-20px);
  }
  40%,
  100% {
    transform: translateY(0);
  }
}

/* 去分析按钮样式 */
.analysis-btn {
  padding: 10px 20px; /* 增加左右内边距 */
  background-color: #3498db;
  color: white;
  display: inline-block;
  border: none;
  cursor: pointer;
  border-radius: 15px;
  font-size: 16px;
}

.analysis-btn:hover {
  background-color: #2980b9; /* 鼠标悬浮时的背景色 */
}
/* 分析图表容器样式 */
.analysis-charts {
  left: 0%;
  margin-top: 1%;
  width: 93%;
  height: 75%;
  position: relative; 
  background-color: rgba(59, 61, 62, 0.685); /* 背景色稍透明，突出图表 */
  backdrop-filter: blur(10px); /* 添加磨砂玻璃效果 */
  border: 11px outset #17cbd899;
  z-index: 100; /* 确保图表位于搜索结果之上 */
  display: flex;
  flex-wrap: wrap;
  justify-content: space-evenly;
}

/* 每个图表容器 */
.chart-container {
  width: 45%; /* 宽度充满父容器 */
  height: 40%;
  margin-bottom: 10px; /* 每个图表之间的间距 */
}

/* 设置图表具体的容器 */
.chart-container div {
  width: 100%; /* 宽度占满容器 */
  height: 100%; /* 高度占满容器 */
}

.close-charts {
  position: absolute;
  top: 10px;
  right: 10px;
  cursor: pointer;
  font-size: 30px;
  color:rgb(24, 245, 204);
}
.close-charts:hover {
  color: rgb(223, 12, 12); /* 改变颜色为红色 */
}

.main-content {
  margin-left: 150px; /* 留出侧边栏的空间 */
  flex: 1;
  padding: 20px;
  background-color: #fbfbfb00;
}

.all_view {
  display: flex;
  width: 100%;
  height: 100vh; /* 使用 vh 单位确保占满整个视口高度 */
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

/* 搜索区域样式 */
.search-area {
  margin-bottom: 20px;
  position: relative;
}

/* 历史搜索面板 */
.history-panel {
  width: 400px;
  top: 0px;
  background: rgba(40, 50, 60, 0.612);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  backdrop-filter: blur(10px);
  position: absolute;
  right: 140px;
  margin-top: 10px;
  margin-left: 10px;
  /* z-index: 100; */
}

.history-header {
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  color: #26c6da;
}

.history-header i {
  cursor: pointer;
  transition: color 0.3s;
}

.history-header i:hover {
  color: #ff4757;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
  display: flex; /* 使用 flex 布局 */
  flex-wrap: wrap; /* 允许换行 */
  gap: 8px; /* 元素之间的间距 */
}

.history-item {
  display: inline-block; /* 改为 inline-block 使元素可以并排显示 */
  padding: 5px 8px;
  border-radius: 4px;
  background: rgba(255,255,255,0.05);
  transition: all 0.3s;
  cursor: pointer;
  white-space: nowrap; /* 防止文本换行 */
}

.history-item:hover {
  background: rgba(38,198,218,0.15);
  transform: translateY(-2px); /* 稍微上移 */
}

.history-item span {
  flex: 1;
  color: #f8f9fa;
  font-size: 13px;
}

.history-item i {
  color: #a4b0be;
  font-size: 12px;
  margin-left: 8px;
  padding: 2px;
  transition: all 0.3s;
}

.history-item i:hover {
  color: #ff4757;
  transform: scale(1.2);
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.input-wrapper {
  display: flex;
  align-items: center; /* 让输入框和按钮水平对齐 */
  margin-bottom: 10px;
}

.input {
  margin-right: 10px;
  background-color: #ffffff00;
  width: 50%;
  height: 8%;
}

.key {
  padding: 10px;
  width: 100%;
}
.key::placeholder {
  color: white; /* 设置占位符文本的颜色为白色 */
}
.search_button button {
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  display: flex;
  border: none;
  cursor: pointer;
}

.searchResult {
  margin-top: 10%;
  margin-right: 0%;
  width: 75%;
  height: 65%;
  overflow-y: auto;
  background-color: #ffffff00;
  background: linear-gradient(to right, #296a7500, #2d66ac00);
  z-index: 99;
  overflow: auto;
  color:white; padding: 1rem;
    box-shadow: 0 0 3rem rgba(100,200,255,.5) inset;
    background: rgba(106, 150, 148, 0.216);
    border-radius: 10px;
}

.result {
    padding: 2px;
    margin-bottom: 0px;
    /* border: 1px solid #6c6161cf; */
    background-color: #ffffff00;
    height: 40px;
}

.item-container {
    display: flex;
    justify-content: space-between;
    flex-direction: row;
}

.item-title,
.item-source,
.item-time {
    margin-top: 10px;
    margin-left: 20px;
    margin-right: 20px;
    font-size: 16px;
    font-family: Arial, sans-serif;
    color: #fff;
}

.item-sentiment {
  margin-top: 11px;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
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
.item-title {
    flex: 1;
    font-weight: bold;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.item-time {
    margin-left: 10px;
}

.item-source {
    margin-left: 10px;
}

.close {
    position: absolute;
    top: 0;
    right: 0;
    cursor: pointer;
}
a:link {
    color: rgb(253, 248, 249);
    text-decoration: none;
}

a:visited {
    color: rgb(83, 237, 183);
    text-decoration: none;
}

a:hover {
    color: rgb(37, 238, 145);
    text-decoration: none;
}

a:active {
    color: rgb(65, 240, 138);
    text-decoration: none;
}

@media (max-width: 768px) {
 .all_view {
        flex-direction: column;
    }

 .input {
        width: 100%;
    }

 .searchResult{
        width: 100%;
    }
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
