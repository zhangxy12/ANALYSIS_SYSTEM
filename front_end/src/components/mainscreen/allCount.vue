<template>
    <div class="platform-article-count">
        <h2><i class="fa fa-cubes"></i>     今日舆情数量（千）</h2>
        <div class="platform-items-wrapper">
            <div class="platform-item" v-for="(count, platform) in platformArticleCounts" :key="platform">
                <span>{{ platformNames[platform] }}</span>
                <dv-decoration-9 style="width:70px;height:70px;" :dur="5">
                    <span>{{ count }}</span>
                </dv-decoration-9>
            </div>
        </div>
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div class="loading" v-if="isLoading">加载中...</div>
    </div>
</template>

<script>
import axios from 'axios';
import { Message } from 'element-ui';

export default {
    props: {
        refresh: {
            type: Boolean,
            default: false
        }
    },
    watch: {
        refresh() {
            this.fetchArticleCounts();
        }
    },
    data() {
        return {
            platformArticleCounts: {
                wechat: 0,
                weibo: 0,
                renmin: 0,
                tieba: 0
            },
            platformNames: {
                wechat: '微信',
                weibo: '微博',
                renmin: '人民网',
                tieba: '贴吧'
            },
            cursor: 1,
            isLoading: false,
            errorMessage: '',
            hasMoreData: true
        };
    },
    mounted() {
        this.fetchArticleCounts();
    },
    methods: {
        async fetchArticleCounts() {
            this.isLoading = true;
            this.errorMessage = '';
            this.hasMoreData = true;
            this.cursor = 1;

            try {
                const response = await axios.get(`/main/all_multi_search?cursor=${this.cursor}`);
                if (response.data.code === 0) {
                    const pageData = response.data.data;
                    const hasData = pageData && pageData.source_count && 
                                   (pageData.source_count.wechat > 0 || 
                                    pageData.source_count.weibo > 0 || 
                                    pageData.source_count.renmin > 0 || 
                                    pageData.source_count.tieba > 0);
                    
                    this.$emit('data-status', hasData);
                    
                    this.platformArticleCounts = {
                        wechat: pageData.source_count.wechat || 0,
                        weibo: pageData.source_count.weibo || 0,
                        renmin: pageData.source_count.renmin || 0,
                        tieba: pageData.source_count.tieba || 0
                    };
                } else {
                    this.errorMessage = response.data.message;
                    Message.warning(this.errorMessage);
                    this.$emit('data-status', false);
                }
            } catch (error) {
                if (error.response) {
                    this.errorMessage = `请求失败，状态码: ${error.response.status}`;
                    Message.error(this.errorMessage);
                } else if (error.request) {
                    this.errorMessage = '网络错误，无法连接到服务器';
                    Message.error(this.errorMessage);
                } else {
                    this.errorMessage = '请求设置错误，请检查代码';
                    Message.error(this.errorMessage);
                }
                console.error('数据请求出错:', error);
                this.$emit('data-status', false);
            }

            this.isLoading = false;
        }
    }
};
</script>

<style scoped>
h2{
    font-size: 18px;
    font-weight: 700;
}
.platform-article-count {
    margin-left: 20px;
    background-color: #f5f5f500;
    border-radius: 5px;
}

.platform-items-wrapper {
    text-align: center;
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.platform-item {
    /* 移除原来的 margin-bottom */
}

.error-message {
    color: red;
    text-align: center;
    margin-top: 10px;
}

.loading {
    color: #999;
    text-align: center;
    margin-top: 10px;
}
</style>    