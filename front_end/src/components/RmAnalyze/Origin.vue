<template>
    <div class="container" ref="container" style="height: 320px;">
      <div class="title-header"><i class="fa fa-bell"></i>  文章来源</div>
      <div v-for="(item, index) in bubbles" :key="index" class="circle" :style="{ 
        left: item.x + 'px', 
        top: item.y + 'px', 
        width: item.size + 'px', 
        height: item.size + 'px', 
        fontSize: item.numSize + 'px' ,
        backgroundColor: item.color
      }">
        <div class="num">{{ item.count }}</div>
        <!-- <div class="title-box">
          <div class="title">{{ item.name }}</div>
        </div> -->
        <h3>{{ item.name }}</h3>
      </div>
    </div>
  </template>
  
  <script>
  import gsap from "gsap";
  
  export default {
    name: "BubbleChart",
    data() {
      return {
        bubbles: [],
        containerWidth: 0,
        containerHeight: 0
      };
    },
    methods: {
      fetchBubbleData(tagTaskId) {
        this.$axios.get(`/origin_rm?tag_task_id=${tagTaskId}`).then((response) => {
          this.containerWidth = this.$refs.container.offsetWidth;
          this.containerHeight = this.$refs.container.offsetHeight;
          this.bubbles = [];
          response.data.data.data.forEach(item => {
            this.addBubble(item);
          });
          this.applyShakeAnimation();
        });
      },
      getRandomPosition(max) {
        return Math.random() * max; 
      },
      addBubble(newBubble) {
        const blueColors = [
    '#1E90FF', // 道奇蓝
    '#00BFFF', // 深天蓝
    '#87CEEB', // 天蓝
    '#ADD8E6', // 浅蓝
    '#6495ED', // 矢车菊蓝
    '#4169E1'  // 皇家蓝
  ];
  newBubble.color = blueColors[Math.floor(Math.random() * blueColors.length)];
  
        const maxTries = 100;
        let tries = 0;
        let x, y;
        const size = 30 + newBubble.count; // 根据count调整气泡大小
        const numSize = 1+ newBubble.count/8; // 根据count调整字体大小
        do {
          x = this.getRandomPosition(this.containerWidth - size);
          y = this.getRandomPosition(this.containerHeight - size);
          let overlap = false;
          this.bubbles.forEach(bubble => {
            const dx = Math.abs(x - bubble.x - bubble.size / 2);
            const dy = Math.abs(y - bubble.y - bubble.size / 2);
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < (bubble.size + size) / 2) {
              overlap = true;
            }
          });
          if (!overlap) {
            break;
          }
          tries++;
        } while (tries < maxTries);
        if (tries < maxTries) {
          newBubble.x = x;
          newBubble.y = y;
          newBubble.size = size;
          newBubble.numSize = numSize;
          this.bubbles.push(newBubble);
        }
      },
      applyShakeAnimation() {
        this.$nextTick(() => {
          const circles = this.$refs.container.querySelectorAll('.circle');
          circles.forEach((circle) => {
            gsap.fromTo(
              circle,
              { y: -2 },
              {
                y: 2,
                ease: "none",
                yoyo: true,
                repeat: -1,
                delay: Math.random(),
              }
            );
          });
        });
      },
    },
    mounted() {
      this.$bus.$on("send_tag_task_id", (tagTaskId) => {
        this.fetchBubbleData(tagTaskId);
      });
    },
    beforeDestroy() {
      this.$bus.$off("send_tag_task_id");
    },
  };
  </script>
  
  <style scoped>
 .container {
    width: 100%;
    height: 300px;
    background: #f9f9f900;
    border-radius: 10px;
    border: 2px solid #4aaafac3; 
    box-shadow: 0 0 15px rgba(233, 229, 238, 0.304), 0 0 25px rgba(63, 154, 87, 0.4); 
    position: relative; 
  }
  
 .title-header {
    font-size: 17px;
    font-weight: 500;
    text-align: left;
    margin-bottom: 10px;
    color: #ffffff;
    z-index: 9;
  }
  
 .circle {
    margin-top: 20px;
    margin-bottom: 10px;
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    color: #fff;
    text-align: center;
  }
  
 .num {
    font-weight: bold;
  }
  

 .h3 {
    font-size: 10px;
    margin-top: 1px;
    color: #ffffff;
    text-decoration: none; 
    text-decoration-color: transparent;
  }
  
  </style>