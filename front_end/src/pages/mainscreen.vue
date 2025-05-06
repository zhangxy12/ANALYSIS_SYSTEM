<template>
  <div id="data-view">
    <dv-full-screen-container>
      <top-header />

      <!-- 添加数据加载状态提示 -->
      <!-- <div v-if="showDataAlert" class="data-alert">
        <el-alert
          title="数据正在准备中"
          type="info"
          description="系统将在每天凌晨2点自动更新数据，请稍后查看。"
          show-icon
          :closable="false">
        </el-alert>
      </div> -->

      <div class="main-content">
        <div class="big-data">
          <!-- 左侧 -->
          <div class="left">
              <dv-border-box-13 style="height: 180px;">
              <div class="allCount" style="height: 180px;">
                <allCount :refresh="refresh" @data-status="updateDataStatus('allCount', $event)" />
              </div>
            </dv-border-box-13>
            <dv-border-box-6 :color="['lightskyblue']">
              <div class="mood">
                <mood :refresh="refresh" @data-status="updateDataStatus('mood', $event)" />
              </div>
            </dv-border-box-6>

            <dv-border-box-12>
              <div class="allApps">
                <allApps :refresh="refresh" @data-status="updateDataStatus('allApps', $event)" />
              </div>
            </dv-border-box-12>

          </div>

          <!-- 中间 -->
          <div class="center">
            <!-- 中间内容 -->
            <div class="allIp">
              <allIp :refresh="refresh" @data-status="updateDataStatus('allIp', $event)" />
            </div>

            <dv-border-box-12>
              <div class="allPost">
                <allPost :refresh="refresh" @data-status="updateDataStatus('allPost', $event)" />
              </div>
            </dv-border-box-12>

          </div>

          <!-- 右侧 -->
          <div class="right">
              
            <dv-border-box-13>
              <div class="hot-search">
                <hotsearch :refresh="refresh" @data-status="updateDataStatus('hotsearch', $event)" />
              </div>
            </dv-border-box-13>
            <dv-border-box-6 :color="['lightskyblue']"> 
              <div class="word">
                <word :refresh="refresh" @data-status="updateDataStatus('word', $event)" />
              </div>
            </dv-border-box-6 >
            <dv-border-box-12>
              <div class="class">
                <classChart :refresh="refresh" @data-status="updateDataStatus('classChart', $event)" />
              </div>
            </dv-border-box-12>
          </div>
        </div>
      </div>
    </dv-full-screen-container>
  </div>
</template>

<script>
import topHeader from '../components/mainscreen/topHeader'
import hotsearch from '../components/mainscreen/hotsearch'
import word from '../components/mainscreen/word'
import classChart from '../components/mainscreen/classChart'
import mood from '../components/mainscreen/mood'
import allCount from '../components/mainscreen/allCount'
import allApps from '../components/mainscreen/allApps'
import allPost from '../components/mainscreen/allPost'
import allIp from '../components/mainscreen/ip'
import axios from 'axios'

export default {
  name: 'DataView',
  components: {
    topHeader,
    hotsearch,
    word,
    classChart,
    mood,
    allCount,
    allApps,
    allPost,
    allIp,
  },
  data() {
    return {
      refresh: false,
      timer: null,
      componentDataStatus: {}, // 用于跟踪每个组件的数据状态
    }
  },
  computed: {
    showDataAlert() {
      // 检查是否有任何组件需要数据
      return Object.values(this.componentDataStatus).includes(false);
    }
  },
  created() {
    // 设置定时刷新，每5分钟刷新一次
    this.timer = setInterval(() => {
      this.refresh = !this.refresh
    }, 5 * 60 * 1000)
  },
  beforeDestroy() {
    // 组件销毁前清除定时器
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    // 更新组件数据状态
    updateDataStatus(component, hasData) {
      this.$set(this.componentDataStatus, component, hasData);
    }
  }
}
</script>

<style>
#data-view {
  width: 100%;
  height: 100%;
  background-color: #030409;
  color: #fff;
}

#dv-full-screen-container {
  background-image: url('../background/bg.png');
  background-size: 100% 100%;
  box-shadow: 0 0 3px blue;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.big-data {
  display: flex;
  flex: 1;
  justify-content: space-between;
}

.left {
  width: 25%;
  height:82%;
  display: flex;
  flex-direction: column;
}

.center {
  width: 50%;
  height:82%;
  display: flex;
  flex-direction: column;
}

.right {
  margin-right: 20px;
  width: 25%;
  height:82%;
  display: flex;
  flex-direction: column;
}

.word {
  height: 200px;
}
.mood {
  height: 200px;
}
.allCount{
  height: 150px;
}
.allPost{
  height: 200px;
}

/* .data-alert {
  padding: 10px 20px;
  background-color: rgba(0,0,0,0.5);
  margin-bottom: 10px;
} */
</style>