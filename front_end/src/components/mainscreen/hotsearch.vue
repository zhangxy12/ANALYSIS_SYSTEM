<template>
    <div>
        <!-- 新增标题 -->
        <h2 ><i class="fa fa-fire" style="color: #fdfcfc;"></i>     热点舆情</h2>
        <!-- 卡片容器 -->
        <div class="radio-button-container">
            <div class="radio-button" v-for="(platform, index) in platforms" :key="index">
                <input type="radio" class="radio-button__input" :id="`radio-${index}`" name="radio-group"
                       :checked="currentPlatform === platform" @change="switchPlatform(platform)">
                <label class="radio-button__label" :for="`radio-${index}`">
                    <span class="radio-button__custom"></span>
                    {{ platform }}
                </label>
            </div>
        </div>
        <!-- 数据展示区域 -->
        <div id="data-display">
            <ul class="data-list">
                <li v-for="(item, idx) in currentData.slice(0, 5)" :key="idx">
                    <a :href="item.url" target="_blank">
                        <!-- 添加序号容器 -->
                        <span class="seq-container" :class="{ 'red-block': idx < 3, 'gray-block': idx >= 3 }">
                            {{ item.seq }}
                        </span>
                        <span class="title-text">{{ item.title }}</span>
                        <span class= "label" v-if="item.label">[{{ item.label }}]</span>
                    </a>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        refresh: {
            type: Boolean,
            default: false
        }
    },
    watch: {
        refresh() {
            this.fetchData();
        }
    },
    data() {
        return {
            currentPlatform: '微博',
            platforms: ['微博', '贴吧', '百度'],
            weiboData: [],
            tiebaData: [],
            baiduData: [],
            currentData: []
        };
    },
    mounted() {
        this.fetchData();
    },
    methods: {
        async fetchData() {
            try {
                const response = await this.$axios.get('/main/all_hot');
                if (response.data.code === 0) {
                    this.weiboData = response.data.data.weibo || [];
                    this.tiebaData = response.data.data.tieba || [];
                    this.baiduData = response.data.data.baidu || [];
                    this.currentData = this.weiboData;
                    
                    // 检查是否有数据，并向父组件发送数据状态
                    const hasData = this.weiboData.length > 0 || this.tiebaData.length > 0 || this.baiduData.length > 0;
                    this.$emit('data-status', hasData);
                } else {
                    console.error('请求失败:', response.data.message);
                    this.$emit('data-status', false);
                }
            } catch (error) {
                console.error('发生错误:', error);
                this.$emit('data-status', false);
            }
        },
        switchPlatform(platform) {
            this.currentPlatform = platform;
            if (platform === '微博') {
                this.currentData = this.weiboData;
            } else if (platform === '贴吧') {
                this.currentData = this.tiebaData;
            } else if (platform === '百度') {
                this.currentData = this.baiduData;
            }
        }
    }
};
</script>

<style scoped>
/* 新增标题样式 */
h2 {
    text-align: center;
    font-size: 18px;
    color: #f2f2f2;
    margin-bottom: 1px;
}

.radio-button-container {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: center;
    margin-bottom: 5px;
}

.radio-button {
    margin-top: 3px;
    display: inline-block;
    position: relative;
    cursor: pointer;
}

.radio-button__input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
}

.radio-button__label {
    display: inline-block;
    padding-left: 30px;
    margin-bottom: 5px;
    position: relative;
    font-size: 13px;
    color: #f2f2f2;
    font-weight: 600;
    cursor: pointer;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.radio-button__custom {
    position: absolute;
    top: 0;
    left: 0;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    border: 2px solid #555;
    transition: all 0.3s ease;
}

.radio-button__input:checked + .radio-button__label .radio-button__custom {
    background-color: #16d7c7;
    border-color: transparent;
    transform: scale(0.8);
    box-shadow: 0 0 20px #1bffeca7;
}

.radio-button__input:checked + .radio-button__label {
    color: #16d7c7;
}

.radio-button__label:hover .radio-button__custom {
    transform: scale(1.2);
    border-color: #16d7c7;
    box-shadow: 0 0 20px #1bffeca7;
}

.data-display {
    margin-left: 20px;
}

/* 数据列表样式 */
.data-list {
    list-style-type: none;
    padding: 0;
    margin: 0;
}

.data-list li {
    margin-bottom: 3px;
}

.data-list li a {
    margin-left: 15px;
    text-decoration: none;
    color: #f0f3f7;
    display: flex;
    align-items: center;
}

/* 减小标题字体大小 */
.title-text {
    font-size: 12px;
}
.label{
    font-size: 12px;
    color :#f73a3a
}
/* 序号容器样式 */
.seq-container {
    display: inline-block;
    width: 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    margin-right: 5px;
    font-size: 12px;
    color: white;
}

/* 前三条红色小色块 */
.red-block {
    background-color: rgba(252, 70, 70, 0.763);
}

/* 其他条灰色小方块 */
.gray-block {
    background-color: rgba(128, 128, 128, 0.593);
}
</style>