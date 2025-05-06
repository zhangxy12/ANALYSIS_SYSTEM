<template>
  <div class="location">
    <div class="location_title">评论地理位置分布</div>
    <!-- <el-button type="text" @click="show" class="maxTree">点击打开地图</el-button> -->
    <div id="location_graph"></div>
    <!-- <el-dialog title="地理位置大图" :visible.sync="dialogVisible" fullscreen="true">
      <div id="mapChart"></div>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
      </span>
    </el-dialog> -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      graphData: [],
      dialogVisible: false,
      mapConfig: {
        auditNo: 'GS(2024)0650号',
        source: '国家地理信息公共服务平台'
      },
      // 特殊行政区划映射表（不需要加"省"的地区）
      specialRegions: {
        '北京': '北京市',
        '天津': '天津市',
        '上海': '上海市',
        '重庆': '重庆市',
        '内蒙古': '内蒙古自治区',
        '广西': '广西壮族自治区',
        '西藏': '西藏自治区',
        '宁夏': '宁夏回族自治区',
        '新疆': '新疆维吾尔自治区',
        '香港': '香港特别行政区',
        '澳门': '澳门特别行政区',
        '台湾': '台湾省'
      }
    };
  },
  mounted() {
    this.fetchDataAndDrawMap('location_graph');
  },
  methods: {
    // 规范化地区名称
    normalizeRegionName(name) {
      // 如果已经是完整名称（带省/市/区）则直接返回
      if (name.endsWith('省') || name.endsWith('市') || name.endsWith('自治区') || name.endsWith('特别行政区')) {
        return name;
      }

      // 检查特殊行政区
      if (this.specialRegions[name]) {
        return this.specialRegions[name];
      }

      // 普通省份加上"省"后缀
      return name + '省';
    },

    async fetchDataAndDrawMap(containerId) {
      try {
        // 1. 加载 china.geojson 文件
        const geoJsonResponse = await fetch('/geojson/china.geojson');
        if (!geoJsonResponse.ok) throw new Error('地图文件加载失败');
        const chinaGeoJSON = await geoJsonResponse.json();
        this.$echarts.registerMap('china', chinaGeoJSON);

        // 2. 获取业务数据
        let query = this.$route.query;
        // 对 URL 参数进行编码
        const encodedUrl = encodeURIComponent(query.url);
        const apiEndpoint = containerId === 'location_graph' ? '/comment/ip' : '/comment/location_tb';
        const res = await this.$axios.get(`${apiEndpoint}?tag_task_id=${query.tag_task_id}&url=${encodedUrl}`);

        const locationData = containerId === 'location_graph' ? res.data.data.detail : res.data.data;

        // 对数据进行聚合（相同地区合并计数）
        const dataMap = {};
        locationData.forEach(item => {
          const normalizedName = this.normalizeRegionName(item.location);
          dataMap[normalizedName] = (dataMap[normalizedName] || 0) + item.count;
        });

        // 转换为 echarts 需要的格式
        this.graphData = Object.keys(dataMap).map(name => ({
          name,
          value: dataMap[name]
        }));

        this.drawMap(containerId);
      } catch (error) {
        console.error('初始化失败:', error);
      }
    },

    drawMap(containerId) {
      const myChart = this.$echarts.init(document.getElementById(containerId));
      const maxCount = Math.max(...this.graphData.map(item => item.value));

      const option = {
        // title: {
        //   text: '评论地理位置分布',
        //   left: 'center',
        //   textStyle: {
        //     color: '#ffffff',
        //     fontSize: 18,
        //     fontWeight: 'bold'
        //   }
        // },
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} 评论',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#40a9ff',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          }
        },
        visualMap: {
          left: containerId === 'location_graph' ? 20 : '10px',
          bottom: containerId === 'location_graph' ? 20 : undefined,
          top: containerId === 'location_graph' ? undefined : '10%',
          height: containerId === 'location_graph' ? 100 : 10,
          min: 0,
          max: maxCount,
          inRange: {
            color: ['#e0f7e0', '#28da7e']
          },
          textStyle: {
            color: '#fff'
          },
          calculable: true
        },
        graphic: {
          type: 'text',
          left: 50,
          bottom: 0,
          z: 100,
          style: {
            text: `审图号：${this.mapConfig.auditNo} 来源：${this.mapConfig.source}`,
            font: '12px Microsoft YaHei',
            fill: '#fff',
            backgroundColor: 'rgba(0,0,0,0)',
            padding: [6, 10],
            borderRadius: 4
          }
        },
        series: [{
          name: '地理位置分布',
          type: 'map',
          map: 'china',
          roam: true,
          label: {
            show: false, // 不显示省份文字
            color: '#000',
            fontSize: 10
          },
          itemStyle: {
            borderColor: '#40a9ff',
            borderWidth: 1,
            areaColor: '#42ace9c8'
          },
          emphasis: {
            label: {
              color: '#fff',
              fontSize: 12
            },
            itemStyle: {
              areaColor: '#89cd45'
            }
          },
          layoutCenter: ['50%', '50%'],  // 地图居中显示
          layoutSize: '100%',  // 地图适应父组件大小
          data: this.graphData
        }]
      };

      myChart.setOption(option);

      const resizeHandler = () => myChart.resize();
      window.addEventListener('resize', resizeHandler);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', resizeHandler);
        myChart.dispose();
      });
    },

    // 显示地图
    show() {
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.fetchDataAndDrawMap('mapChart');
      });
    }
  }
};
</script>

<style scoped>
.location {
  position: relative;
  top: 1%;
  width: 100%;
  height: 90%;
  background-color: #ffffff00;
  color: #ffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  /* border: 2px solid #669ef3a5; 深色边框 */
  border-radius: 10px;
  box-sizing: border-box;
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(10px);
  overflow: hidden;
}
.location_title {
  margin-left: 20px;
  padding: 5px;
  font-weight: 600;
  letter-spacing: 1px;
}
#location_graph {
  width: 450px;
  height: 310px;
  top: 30px;
  margin-left: 10%;
  margin-bottom: 10%;
}
#mapChart {
  position: relative;
  width: 100%;
  height: 90%;
}
</style>    