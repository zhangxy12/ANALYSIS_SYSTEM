<template>
  <div class="container">
    <nav>
      <ul class="mcd-menu">
        <!-- 返回首页 -->
        <li>
          <a @click="ToHome" :class="{ active: activePath === '/home' }">
            <i class="fa fa-arrow-left"></i>
            <strong>退出</strong>
          </a>
        </li>
        <!-- 可视化大屏 -->
        <li>
          <a @click="ToMain" :class="{ active: activePath === '/mainscreen' }">
            <i class="fa fa-fire"></i>
            <strong>舆情大屏</strong>
          </a>
        </li>
        <!-- 热点事件 -->
        <li>
          <a @click="ToHot" :class="{ active: activePath === '/hot' }">
            <i class="fa fa-fire"></i>
            <strong>热点事件</strong>
          </a>
        </li>
        <!-- 总览搜索 -->
        <li>
          <a @click="ToAllView" :class="{ active: activePath === '/all_view' }">
            <i class="fa fa-search"></i>
            <strong>总览搜索</strong>
          </a>
        </li>
        <!-- 谣言分析 -->
        <li>
          <a @click="ToRumor" :class="{ active: activePath === '/Rumor' }">
            <i class="fa fa-bullhorn"></i>
            <strong>谣言分析</strong>
          </a>
        </li>

        <!-- 详细舆情 -->
        <li>
          <a @click="toggleSubMenu" :class="{ active: subMenuOpen }">
            <i class="fa fa-file-text-o"></i>
            <strong>详细舆情</strong>
            <!-- <i class="fa fa-sort-down"></i> -->
          </a>
          <ul v-if="subMenuOpen" class="sub-menu-row">
            <!-- 微博 -->
            <li><a @click="ToWB" :class="{ active: activePath === '/wb' }"><i class="fa fa-weibo"></i><small>微博</small></a></li>
            <!-- 微信 -->
            <li><a @click="ToWX" :class="{ active: activePath === '/wx' }"><i class="fa fa-weixin"></i><small>微信</small></a></li>
            <!-- 人民网 -->
            <li><a @click="ToRM" :class="{ active: activePath === '/rm' }"><i class="fa fa-globe"></i><small>人民网</small></a></li>
            <!-- 贴吧 -->
            <li><a @click="ToTB" :class="{ active: activePath === '/tb' }"><i class="fa fa-comments-o"></i><small>贴吧</small></a></li>
          </ul>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
export default {
  name: "side_border",
  data() {
    return {
      subMenuOpen: false,
      activePath: this.$route.path
    };
  },
  methods: {
    ToHome() {
      if (this.activePath!== "/home") {
        this.$router.push({
          path: "/home"
        });
        this.activePath = "/home";
      }
    },
    ToMain() {
      if (this.activePath!== "/mainscreen") {
        this.$router.push({
          path: "/mainscreen"
        });
        this.activePath = "/mainscreen";
      }
    },
    ToAllView() {
      if (this.activePath!== "/all_view") {
        this.$router.replace({
          path: "/all_view"
        });
        this.activePath = "/all_view";
      }
    },
    ToRumor() {
      if (this.activePath!== "/Rumor") {
        this.$router.replace({
          path: "/Rumor"
        });
        this.activePath = "/all_view";
      }
    },
    ToHot() {
      if (this.activePath!== "/hot") {
        this.$router.push({
          path: "/hot"
        });
        this.activePath = "/hot";
      }
    },
    ToWB() {
      if (this.activePath!== "/wb") {
        this.$router.push({
          path: "/wb"
        });
        this.activePath = "/wb";
      }
      this.subMenuOpen = false;
    },
    ToWX() {
      if (this.activePath!== "/wx") {
        this.$router.push({
          path: "/wx"
        });
        this.activePath = "/wx";
      }
      this.subMenuOpen = false;
    },
    ToRM() {
      if (this.activePath!== "/rm") {
        this.$router.push({
          path: "/rm"
        });
        this.activePath = "/rm";
      }
      this.subMenuOpen = false;
    },
    ToTB() {
      if (this.activePath!== "/tb") {
        this.$router.push({
          path: "/tb"
        });
        this.activePath = "/tb";
      }
      this.subMenuOpen = false;
    },
    toggleSubMenu() {
      this.subMenuOpen =!this.subMenuOpen;
    }
  }
};
</script>

<style scoped>
html, body {
  height: 100%; /* 确保 html 和 body 元素高度为 100% */
  margin: 0;
  padding: 0;
}

.container {
  width: 150px; /* 确保侧边栏宽度足够 */
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  background: #070d7b00;
  color: white;
  box-sizing: border-box;
  display: flex;
  flex-direction: column; /* 使用列布局 */
}
.mcd-menu {
  flex: 1;
  height: 100%;
  list-style: none;
  padding: 0;
  margin: 0;
  background: #070d7b00; /* 蓝色系背景 */
  font-family: 'Open Sans', Arial, sans-serif;
}

.mcd-menu li {
  position: relative;
}

.mcd-menu li a {
  display: flex; /* 修改为 flex 布局 */
  align-items: center; /* 垂直居中对齐 */
  text-decoration: none;
  padding: 15px 25px;
  color: white;
  transition: background-color 0.3s;
}

.mcd-menu li a i {
  margin-right: 5px; /* 图标和文字之间的间距 */
}

.sub-menu-row {
  display: flex;
  flex-wrap: wrap;
  list-style-type: none;
  padding: 0;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}

.sub-menu-row li {
  margin: 0 18px; /* 可以根据需要调整间距 */
}

.sub-menu-row li a {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.sub-menu-row li a i {
  margin-right: 8px; /* 图标和文字之间的间距 */
}

.mcd-menu li a:hover {
  color: aqua;
}

.mcd-menu li a.active {
  box-shadow: 0 0 10px rgba(187, 197, 209, 0.8); /* 添加边框阴影效果 */
  color: aqua;
}

.mcd-menu li a i {
  display: block;
  font-size: 24px;
  margin-bottom: 5px;
  text-align: center;
}

.mcd-menu li a strong {
  display: block;
  text-align: center;
}
.mcd-menu li a small {
  display:block;
  text-align: center;
}

.mcd-menu li ul {
  display: none;
  position: absolute;
  left: 0; /* 修改为 0，使其与父元素左对齐 */
  top: 100%; /* 使其出现在父元素下方 */
  background: #192d5200; /* 子菜单背景颜色 */
  list-style: none;
  padding: 0;
  margin: 0;
  width: 150px; /* 调整宽度与父元素一致 */
}

.mcd-menu li ul li a {
  padding: 10px 15px;
  
}

.mcd-menu li:hover > ul {
  display: block;
}
</style>