<template>
  <div class="blog_hot">
    <div class="blog_hot_top">
      <svg class="icon" aria-hidden="true">
        <use xlink:href="#icon-redu"></use>
      </svg>
      <span>博文热度前十</span>
    </div>
    <div class="ten_hot_blogs">
      <div class="hot_blog" v-for="(hot_blog, index) in hot_blogs" :key="index">
        <div v-if="index == 0" class="serial_number red">{{ index + 1 }}</div>
        <div v-if="index == 1" class="serial_number orange">
          {{ index + 1 }}
        </div>
        <div v-if="index == 2" class="serial_number green">{{ index + 1 }}</div>
        <div v-if="index > 2" class="serial_number">{{ index + 1 }}</div>
        <div class="blog_text" @click="ToBolgDetail(hot_blog.weibo_id)">
          {{ hot_blog.text | snippet }}
        </div>
        <div
          class="proportional_bar"
          :style="{ '--width': hot_blog.hot_proportion }"
        ></div>
        <div class="blog_redu">{{ hot_blog.hot_count }}</div>
      </div>
    </div>
    <div class="learnmore">
      
    </div>
  </div>
</template>

<script>
export default {
  name: "blog_hot",
  data() {
    return {
      hot_blogs: [],
      total_hot: 0,
      tag_task_id: ''
    };
  },
  //定义过滤器超多20个字
  filters: {
    snippet(value) {
      if (value.length > 20) return value.slice(0, 20) + "...";
      return value;
    },
  },
  methods: {
    requsetHotBlog(id) {
      this.$axios
        .get("blog_rank?tag_task_id="+id)
        .then((res) => {
          this.hot_blogs = res.data.data;
          console.log(this.hot_blogs)
          for (let index in this.hot_blogs) {
            this.total_hot =
              this.total_hot + Number(this.hot_blogs[index].hot_count);
          }
          for (let index in this.hot_blogs) {
            this.hot_blogs[index].hot_proportion = (
              (this.hot_blogs[index].hot_count / this.total_hot) *
              100
            ).toFixed(1);
            this.hot_blogs[index].hot_proportion += "%";
          }
        });
    },
    ToBolgDetail(weibo_id) {
      this.$router.push({
        path: "/blog_detail",
        query :{
          tag_task_id: this.tag_task_id,
          weibo_id: weibo_id
        }
      });
    },
  },
  mounted() {
    this.$bus.$on("send_tag_task_id", (tag_task_id) => {
      this.tag_task_id = tag_task_id;
      this.requsetHotBlog(tag_task_id);
    });
    // this.requsetHotBlog();
  },
  beforeDestroy() {
    this.$bus.$off("send_tag_task_id");
  },
};
</script>

<style scoped>
.blog_hot {
  position: relative;
  background-color: rgba(255, 255, 255, 0);
  height: 57%;
  color: #ffffff;
  border-radius: 10px;
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(10px);
}

.blog_hot_top {
  border: none;
  margin: 0 0 0 20px;
  position: relative;
  height: 16%;
}

.learnmore {
  border: none;
  position: relative;
  float: top;
  margin: 2% 0;
  height: 20%;
}

.ten_hot_blogs {
  border: none;
  height: 120%;
  position: relative;
  margin-left: 70px;
  margin-top: 10px;
}

.hot_blog {
  display: flex; /* 使用 Flexbox 布局 */
  align-items: center; /* 垂直居中对齐 */
  margin: 1% 0;
  width: 100%;
  height: 8%;
  border: none;
}

.serial_number {
  margin-right: 20px;
  width: 20px;
  text-align: center;
  border-radius: 50%;
  color: #fff;
  background-color: #ccc;
  flex-shrink: 0; /* 防止序号被压缩 */
}

.red {
  background-color: rgb(255, 0, 0);
}

.orange {
  background-color: rgb(255, 153, 0);
}

.green {
  background-color: rgb(0, 255, 13);
}

.blog_text {
  flex: 1; /* 占据剩余空间 */
  margin-right: 10px; /* 添加右侧间距 */
}

.blog_text:hover {
  border: none;
  cursor: pointer;
  color: #0fbcf9;
  letter-spacing: 1px;
}

.proportional_bar {
  height: 50%;
  width: 40%;
  background-color: #f5f7f800;
  margin-left: 10px; /* 添加右侧间距 */
  flex-shrink: 0; /* 防止进度条被压缩 */
  text-align: left; /* 左对齐热度值 */
}

.proportional_bar::before {
  content: "";
  display: block;
  padding-left: 5px;
  height: 16px;
  
  width: var(--width); /* 使用 CSS 变量设置宽度 */
  border-radius: 6px;
  border: none;
  background-image: linear-gradient(90deg, #06725b, #6bf2d0);
  animation-duration: 1.2s;
  animation-fill-mode: forwards;
  animation-timing-function: ease-in-out;
  animation-name: slide;
}


.blog_redu {
  flex-shrink: 0; /* 防止热度值被压缩 */
  text-align: left; /* 左对齐热度值 */
}
</style>