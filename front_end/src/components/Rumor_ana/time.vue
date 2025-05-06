<template>
    <div class="post" style="height: 95%;">
        <div class="post_top">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clock-history" viewBox="0 0 16 16">
  <path d="M8.515 1.019A7 7 0 0 0 8 1V0a8 8 0 0 1 .589.022zm2.004.45a7 7 0 0 0-.985-.299l.219-.976q.576.129 1.126.342zm1.37.71a7 7 0 0 0-.439-.27l.493-.87a8 8 0 0 1 .979.654l-.615.789a7 7 0 0 0-.418-.302zm1.834 1.79a7 7 0 0 0-.653-.796l.724-.69q.406.429.747.91zm.744 1.352a7 7 0 0 0-.214-.468l.893-.45a8 8 0 0 1 .45 1.088l-.95.313a7 7 0 0 0-.179-.483m.53 2.507a7 7 0 0 0-.1-1.025l.985-.17q.1.58.116 1.17zm-.131 1.538q.05-.254.081-.51l.993.123a8 8 0 0 1-.23 1.155l-.964-.267q.069-.247.12-.501m-.952 2.379q.276-.436.486-.908l.914.405q-.24.54-.555 1.038zm-.964 1.205q.183-.183.35-.378l.758.653a8 8 0 0 1-.401.432z"/>
  <path d="M8 1a7 7 0 1 0 4.95 11.95l.707.707A8.001 8.001 0 1 1 8 0z"/>
  <path d="M7.5 3a.5.5 0 0 1 .5.5v5.21l3.248 1.856a.5.5 0 0 1-.496.868l-3.5-2A.5.5 0 0 1 7 9V3.5a.5.5 0 0 1 .5-.5"/>
</svg>
            <span class="stat-title">   舆情引导策略分析</span>
        </div>
        <div class="strategy-analysis">
            <div class="stage">
                <span class="stage-title">开始阶段:</span>
                <span>{{ analysis.start }}</span>
            </div>
            <div class="stage">
                <span class="stage-title">扩散阶段:</span>
                <span>{{ analysis.spread }}</span>
            </div>
            <div class="stage">
                <span class="stage-title">高潮阶段:</span>
                <span>{{ analysis.climax }}</span>
            </div>
            <div class="stage">
                <span class="stage-title">退散阶段:</span>
                <span>{{ analysis.fade }}</span>
            </div>
        </div>
        <div class="guidance-platform">
            <span class="platform-title">舆情主要引导平台:</span>
            <span>{{ dominantPlatform }}</span>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "time",
    data() {
        return {
            radio: 1,
            key: '',
            timeData: {},
            analysis: {
                start: '',
                spread: '',
                climax: '',
                fade: ''
            },
            dominantPlatform: ''
        };
    },
    mounted() {
        this.key = this.$route.query.key;
        this.fetchData();
    },
    methods: {
        async fetchData() {
            try {
                const response = await axios.get(`/rumor/rumorPost?key=${encodeURIComponent(this.key)}`);
                if (response.data.code === 0) {
                    this.timeData = this.filterSixMonthsData(response.data.data);
                    this.analyzeStages();
                    this.findDominantPlatform();
                }
            } catch (error) {
                console.error('获取数据出错:', error);
            }
        },
        filterSixMonthsData(data) {
            const sixMonthsAgo = new Date();
            sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 12);

            const filteredData = {
                renmin_date_count: {},
                tieba_date_count: {},
                wechat_date_count: {},
                weibo_date_count: {}
            };

            const platforms = ['renmin_date_count', 'tieba_date_count', 'wechat_date_count', 'weibo_date_count'];
            platforms.forEach(platform => {
                for (const [date, count] of Object.entries(data[platform])) {
                    const currentDate = new Date(date);
                    if (currentDate >= sixMonthsAgo) {
                        filteredData[platform][date] = count;
                    }
                }
            });

            return filteredData;
        },
        analyzeStages() {
            const allData = {
               ...this.timeData.renmin_date_count,
               ...this.timeData.tieba_date_count,
               ...this.timeData.wechat_date_count,
               ...this.timeData.weibo_date_count
            };
            const sortedDates = Object.keys(allData).sort();

            if (sortedDates.length > 0) {
                this.analysis.start = sortedDates[0];
            }

            let prevCount = 0;
            let stage = 'start';
            let lastDate = null;
            let climaxDate = null;
            let spreadPeak = 0;

            for (const date of sortedDates) {
                const count = allData[date];
                if (count > prevCount) {
                    if (stage === 'start') {
                        stage ='spread';
                    }
                }
                if (count === Math.max(...Object.values(allData))) {
                    stage = 'climax';
                    climaxDate = date;
                }
                if (climaxDate) {
                    break;
                }
                if (count > spreadPeak) {
                    spreadPeak = count;
                    this.analysis.spread = date;
                }
                prevCount = count;
                lastDate = date;
            }

            if (climaxDate) {
                this.analysis.climax = climaxDate;
            }

            // 继续遍历找退散阶段
            let isFade = false;
            for (const date of sortedDates) {
                if (date === climaxDate) {
                    isFade = true;
                    continue;
                }
                if (isFade && allData[date] < allData[climaxDate]) {
                    this.analysis.fade = date;
                    break;
                }
            }

            // 处理最后日期仍处于高潮阶段的情况
            if (lastDate === this.analysis.climax) {
                this.analysis.fade = '未退散';
            }

            // 确保日期依次增加
            if (this.analysis.spread < this.analysis.start) {
                this.analysis.spread = this.analysis.start;
            }
            if (this.analysis.climax < this.analysis.spread) {
                this.analysis.climax = this.analysis.spread;
            }
            if (this.analysis.fade!== '未退散' && this.analysis.fade < this.analysis.climax) {
                this.analysis.fade = '未退散';
            }
        },
        findDominantPlatform() {
            const stageWeights = {
                start: 0.1,
                spread: 0.3,
                climax: 0.6,
                fade: 0.0
            };

            const platformScores = {
                '人民网': 0,
                '贴吧': 0,
                '微信': 0,
                '微博': 0
            };

            const stageDates = {
                start: this.analysis.start,
                spread: this.analysis.spread,
                climax: this.analysis.climax,
                fade: this.analysis.fade
            };

            for (const [stage, date] of Object.entries(stageDates)) {
                if (date && date!== '未退散') {
                    const renminCount = this.timeData.renmin_date_count[date] || 0;
                    const tiebaCount = this.timeData.tieba_date_count[date] || 0;
                    const wechatCount = this.timeData.wechat_date_count[date] || 0;
                    const weiboCount = this.timeData.weibo_date_count[date] || 0;

                    platformScores['人民网'] += renminCount * stageWeights[stage];
                    platformScores['贴吧'] += tiebaCount * stageWeights[stage];
                    platformScores['微信'] += wechatCount * stageWeights[stage];
                    platformScores['微博'] += weiboCount * stageWeights[stage];
                }
            }

            let maxScore = 0;
            for (const [platform, score] of Object.entries(platformScores)) {
                if (score > maxScore) {
                    maxScore = score;
                    this.dominantPlatform = platform;
                }
            }
        }
    }
};
</script>

<style scoped>
.post {
    color: #ffffff;
    /* border-radius: 8px; */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
    border: 2px solid #669ef3a5; /* 深色边框 */
    border-radius: 10px;
    box-sizing: border-box;
    text-align: left; /* 设置整个组件内容左对齐 */
}

.post_top {
    text-align: center;
    margin-bottom: 10px;
    font-size: 18px;
    font-weight: 800;
    width: 99%;
}

.stat-title {
    margin-right: 10px;
}

.radio {
    margin-left: auto;
}

.strategy-analysis {
    display: flex;
    flex-wrap: wrap;
    margin-top: 1px;
}

.stage {
    width: 48%;
    padding: 10px;
    margin-bottom: 1px;
    text-align: left; /* 设置每个阶段内容左对齐 */
}

.stage-title {
    font-weight: bold;
    margin-right: 10px;
}

.guidance-platform {
    width: 48%;
    padding: 10px;
    text-align: left; /* 设置舆情引导平台内容左对齐 */
}

.platform-title {
    font-weight: bold;
    margin-bottom: 10px;
}
</style>