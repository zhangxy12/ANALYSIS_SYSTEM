<template>
  <div class="home">
    <img src="../background/4.png" alt="" />
    <div class="table">
      <div class="bg" @click="bgClick">
        <h2 class="main-title">
    <img src="../logo/t.svg" alt="Logo" class="logo" />
    智析万象舆情系统
  </h2>
        <h1>{{ currentTime }}</h1>
        <p>{{ currentDate }}</p>
        <h5>welcome to our system</h5>
        <i class="fa fa-angle-down fa-3x" aria-hidden="true"></i>
        <i class="fa fa-angle-down fa-3x" aria-hidden="true"></i>
        <h6>点击向下滑动</h6>
      </div>

      <div class="up" @click="upClick">
        <i class="fa fa-angle-up fa-3x" aria-hidden="true"></i>
        <i class="fa fa-angle-up fa-3x" aria-hidden="true"></i>
      </div>
    </div>

    <div class="home_container">
      <div class="con">
        <!-- <div class="box">
          <div class="content" @click="goToAllView"> 
          </div>
          <i class="fa fa-home"></i>
        <div>总览</div>
        </div> -->
          
      <div class="box">
        <div class="content" @click="ToUser">
          <i class="fa fa-user"></i>
        </div>
        <div>注册/登录</div>    
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import $ from "jquery";
export default {
  name: "home",
  components: {},
  data() {
    return {
      flag: true,
      timer: "",
      currentDate: "",
      currentTime: "",
      // title: ["早上好", "中午好", "下午好", "晚上好"],
      // content: [
      //   "欢迎!",
      //   "欢迎来到我们的舆情分析系统!",
      //   "欢迎来到我们的舆情分析系统!!",
      //   "斯是陋室，唯吾独馨~",
      // ],
    };
  },
  methods: {
    goToAllView() {
      this.$router.push({
        path: "/all_view",
      });
    },
    bgClick() {
      if (this.flag) {
        $(".table").animate(
          {
            top: -100 + "vh",
          },
          500
        );
        $(".home>img").animate(
          {
            width: 120 + "%",
            height: 120 + "%",
            left: -10 + "%",
          },
          500
        );
        $(".home_container").animate(
          {
            top: -10 + "%",
          },
          500
        );
        this.flag = false;
      }
    },
    upClick() {
      if (!this.flag) {
        $(".table").animate(
          {
            top: 0,
          },
          500
        );
        $(".home>img").animate(
          {
            width: 100 + "%",
            height: 100 + "%",
            left: 0,
          },
          500
        );
        $(".home_container").animate(
          {
            top: 100 + "%",
          },
          500
        );
        this.flag = true;
      }
    },
    
    ToUser() {
      this.$router.push({
        path: "/user",
      });
    },
    
  },
  mounted() {
    const h = this.$createElement;
    let t = 0;
    let hour = new Date().getHours();
    if (5 <= hour && hour <= 11) t = 0;
    else if (11 < hour && hour <= 14) t = 1;
    else if (14 < hour && hour <= 18) t = 2;
    else t = 3;
    // this.$notify({
    //   title: this.title[t],
    //   message: h("i", { style: "color: teal" }, this.content[t]),
    // });
  },
  created() {
    let date = new Date();
    this.currentDate =
      date.getFullYear() +
      "年" +
      (date.getMonth() + 1) +
      "月" +
      date.getDate() +
      "日";
    this.timer = setInterval(() => {
      let date = new Date();
      let hour = date.getHours();
      let minute = date.getMinutes();
      let second = date.getSeconds();
      hour = hour < 10 ? "0" + hour : hour;
      minute = minute < 10 ? "0" + minute : minute;
      second = second < 10 ? "0" + second : second;
      this.currentTime = hour + ":" + minute + ":" + second;
    }, 1000);
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  },
};
</script>

<style scoped>
.home {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  position: relative;
}
.home > img {
  width: 100vw;
  height: 100vh;
  position: absolute;
  transform: scale(1.6);
  animation: home 1s ease-out forwards;
}
.table {
  width: 100%;
  height: 20vh;
  position: relative;
}
.main-title {
  position: absolute;
  top: 25%;
  left: 50%;
  transform: translateX(-50%);
  font-size: 70px;
  font-weight: 600;
  letter-spacing: 7px;
  color: #fff;
  z-index: 1;
}
.main-title .logo {
  width: 100px; /* 根据需要调整宽度 */
  height: 80px; /* 根据需要调整高度 */
  margin-right: 5px; /* 图片和文字之间的间距 */
}
.bg {
  position: relative;
  width: 100%;
  height: 100vh;
  user-select: none;
}
.bg h1 {
  position: absolute;
  bottom: 0px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 30px;
  font-weight: 600;
  letter-spacing: 10px;
  color: #fff;
  z-index: 1;
  animation: bg_h1 0.5s ease-out forwards;
}
.bg p {
  margin-top: 80px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 20px;
  letter-spacing: 10px;
  color: #fff;
  font-weight: 100;
  z-index: 1;
  animation: bg_p 0.5s ease-out forwards 0.3s;
}
.bg h5 {
  position: absolute;
  top: 1%;
  left: 50%;
  transform: translateX(-50%);
  letter-spacing: 10px;
  color: #fff;
  font-weight: 100;
  z-index: 1;
  opacity: 0;
  animation: bg_h5 0.3s ease-out forwards 0.6s;
}
.bg h6 {
  position: absolute;
  top: 90%;
  left: 50%;
  transform: translateX(-50%);
  letter-spacing: 5px;
  color: #fff;
  font-weight: 100;
  z-index: 1;
  opacity: 0;
  animation: bg_h6 0.3s ease-out forwards 0.6s;
}
.bg i:nth-child(4) {
  z-index: 1;
  color: #fff;
  position: absolute;
  bottom: 2vh;
  left: 50%;
  transform: translateX(-50%);
  animation: bg_i 1s infinite;
}
.bg i:nth-child(5) {
  z-index: 1;
  color: #fff;
  position: absolute;
  bottom: 0vh;
  left: 50%;
  transform: translateX(-50%);
  animation: bg_i 1s 0.5s infinite;
}

@keyframes bg_h1 {
  from {
    top: 60%;
    opacity: 0;
  }
  to {
    top: 50%;
    opacity: 1;
  }
}
@keyframes bg_p {
  from {
    top: 80%;
    opacity: 0;
  }
  to {
    top: 50%;
    opacity: 1;
  }
}
@keyframes bg_h5 {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes bg_h6 {
  from {
    top: 100%;
    opacity: 0;
  }
  to {
    top: 80%;
    opacity: 1;
  }
}
@keyframes home {
  from {
    transform: scale(1.6);
  }
  to {
    transform: scale(1);
  }
}
@keyframes bg_i {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.up i:nth-child(1) {
  z-index: 1;
  color: #fff;
  position: absolute;
  top: 100vh;
  left: 50%;
  transform: translateX(-50%);
  animation: bg_i 1s infinite;
}
.up i:nth-child(2) {
  z-index: 1;
  color: #fff;
  position: absolute;
  top: 102vh;
  left: 50%;
  transform: translateX(-50%);
  animation: bg_i 1s 0.5s infinite;
}
.home_container {
  position: relative;
  top: 100%;
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  color: #fff;
}

.content .fa-user {
    font-size: 32px; /* 增大图标的大小，可根据需求调整 */
}

.box div:nth-child(2) {
    font-size: 20px; /* 增大文字的大小，可根据需求调整 */
}

.home_container .con {
  width: 10%;
  height: 20%;
  border-radius: 20px;
  backdrop-filter: blur(30px);
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr ;
  grid-gap: 20px;
  padding: 20px;
}
.home_container .box {
  display: flex;
  justify-content: space-between;
  flex-direction: column;
  align-items: center;
  padding: 1opx;
  border: 1px solid rgba(255, 255, 255, 0);
  transition: border 0.5s;
  width: 100%;
  height: 100%;
}
.home_container .box:hover {
  border: 1px solid rgba(255, 255, 255, 1);
  transition: border 0.5s;
}
.home_container .content {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}
.icon{
  width: 80px;
  height: 80px;
}
.home_container a img {
  width: 80px;
}
</style>