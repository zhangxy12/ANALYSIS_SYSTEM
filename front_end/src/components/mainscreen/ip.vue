<template>
  <div>
    <div id="map-chart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      graphData: [],
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
      },
      mapChart: null
    };
  },
  props: {
    refresh: {
      type: Boolean,
      default: false
    }
  },
  watch: {
    refresh() {
      this.fetchDataAndDrawMap();
    }
  },
  mounted() {
    this.fetchDataAndDrawMap();
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

    async fetchDataAndDrawMap() {
      try {
        // 1. 加载china.geojson文件
        const geoJsonResponse = await fetch('/geojson/china.geojson');
        if (!geoJsonResponse.ok) throw new Error('地图文件加载失败');
        const chinaGeoJSON = await geoJsonResponse.json();
        this.$echarts.registerMap('china', chinaGeoJSON);

        // 2. 获取业务数据并规范化地区名称
        const graphResponse = await this.$axios.get('/main/all_ip');
        if (graphResponse.data.code === 200 || graphResponse.data.code === 404) {
          // 对数据进行聚合（相同地区合并计数）
          const dataMap = {};
          if (graphResponse.data.data && graphResponse.data.data.detail) {
            graphResponse.data.data.detail.forEach(item => {
              const normalizedName = this.normalizeRegionName(item.location);
              dataMap[normalizedName] = (dataMap[normalizedName] || 0) + item.count;
            });
          }
          
          // 转换为echarts需要的格式
          this.graphData = Object.keys(dataMap).map(name => ({
            name,
            value: dataMap[name]
          }));
          
          // 检查是否有数据
          const hasData = this.graphData.length > 0;
          // 发送数据状态到父组件
          this.$emit('data-status', hasData);
          
          this.drawMap();
        } else {
          console.error('获取IP数据失败:', graphResponse.data.message);
          this.$emit('data-status', false);
        }
      } catch (error) {
        console.error('初始化失败:', error);
        this.$emit('data-status', false);
      }
    },

    drawMap() {
      // 检查DOM元素
      const chartElement = document.getElementById('map-chart');
      if (!chartElement) {
        console.error('找不到地图DOM元素');
        return;
      }
      
      // 如果已有地图实例，先销毁它
      if (this.mapChart) {
        this.mapChart.dispose();
      }
      
      // 创建新的地图实例
      this.mapChart = this.$echarts.init(chartElement);
      
      // 防止空数据或最大值为0导致渐变色错误
      const maxCount = this.graphData.length > 0 
        ? Math.max(...this.graphData.map(item => item.value)) 
        : 100;  // 设置默认最大值，避免为0
      
      const option = {
        title: {
          text: '地理位置分布',
          left: 'center',
          textStyle: {
            color: '#ffffff',
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} 人',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderColor: '#40a9ff',
          textStyle: {
            color: '#ffffff',
            fontSize: 12
          }
        },
        visualMap: {
          left: 20,
          bottom: 20,
          min: 0,
          max: maxCount || 100,  // 确保最大值不会为0或undefined
          inRange: {
            // 使用固定颜色数组而不是渐变色
            color: ['#9ecae8', '#6baed6', '#4292c6', '#2171b5', '#08519c']
          },
          textStyle: {
            color: '#fff'
          },
          itemWidth: 10,
          itemHeight: 100,
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
          name: '分布数据',
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
            areaColor: '#B0C4DE'
          },
          emphasis: {
            label: {
              color: '#fff',
              fontSize: 12
            },
            itemStyle: {
              areaColor: '#40a9ff'
            }
          },
          layoutCenter: ['50%', '50%'],  // 地图居中显示
          layoutSize: '100%',  // 地图适应父组件大小
          data: this.graphData || []  // 确保data不为undefined
        }]
      };

      this.mapChart.setOption(option);

      const resizeHandler = () => this.mapChart.resize();
      window.addEventListener('resize', resizeHandler);
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', resizeHandler);
        if (this.mapChart) {
          this.mapChart.dispose();
        }
      });
    }
  }
};
</script>

<style scoped>
#map-chart {
  background: #1e1e2f;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}
</style>    