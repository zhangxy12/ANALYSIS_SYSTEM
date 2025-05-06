<template>
  <div class="blog_hot">
    <div class="blog_hot_top">
      <svg class="icon" aria-hidden="true">
        <use xlink:href="#icon-redu"></use>
      </svg>
      <span>帖子详情</span>
    </div>
    <div class="ten_hot_blogs">
      <div class="hot_blog" v-for="(hot_blog, index) in hot_blogs" :key="index">
        <div v-if="index == 0" class="serial_number red">{{ index + 1 }}</div>
        <div v-if="index == 1" class="serial_number orange">
          {{ index + 1 }}
        </div>
        <div v-if="index == 2" class="serial_number green">{{ index + 1 }}</div>
        <div v-if="index > 2" class="serial_number">{{ index + 1 }}</div>
        <div class="blog_text" @click="ToBolgDetail(hot_blog.url)">
          {{ hot_blog.title | snippet }}
        </div>
        <!-- <div
          class="proportional_bar"
          :style="{ '--width': hot_blog.hot_proportion }"
        ></div>
        <div class="blog_redu">{{ hot_blog.hot_count }}</div> -->
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
  //定义过滤器
  filters: {
    snippet(value) {
      if (value.length > 35) return value.slice(0, 35) + "...";
      return value;
    },
  },
  methods: {
    requsetHotBlog(id) {
      this.$axios
        .get("tb_detail?tag_task_id="+id)
        .then((res) => {
          this.hot_blogs = res.data.data;
          console.log(this.hot_blogs)
        //   for (let index in this.hot_blogs) {
        //     this.total_hot =
        //       this.total_hot + Number(this.hot_blogs[index].hot_count);
        //   }
        //   for (let index in this.hot_blogs) {
        //     this.hot_blogs[index].hot_proportion = (
        //       (this.hot_blogs[index].hot_count / this.total_hot) *
        //       100
        //     ).toFixed(1);
        //     this.hot_blogs[index].hot_proportion += "%";
        //   }
        });
    },
    ToBolgDetail(url) {
      this.$router.push({
        path: "/tb_detail",
        query :{
          tag_task_id: this.tag_task_id,
          url: url
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

<style scpoed>
.blog_hot {
  position: relative;
  background-color: rgba(255, 255, 255, 0);
  height: 57%;
  color: #ffffff;
  
  border-radius: 10px;
  /*box-shadow: 0 4px 8px rgba(231, 228, 228, 0.5); /* 增加阴影效果 */
  backdrop-filter: blur(3px); /* 添加磨砂玻璃效果 */
  -webkit-backdrop-filter: blur(10px); /* Safari 兼容 */
  

}

.blog_hot_top {
  border: none;
  margin: 0 0 0 20px;
  position: relative;
  height: 16%;
  
}
.learnmore{
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
  float: top;
  margin: 1% 0;
  width: 100%;
  height: 8%;
  border: none;
}
.serial_number,
.blog_text,
.blog_redu,
.proportional_bar {
  border: none;
  display: inline-block;
}
.serial_number {
  margin-right: 20px;
  width: 20px;
  text-align: center;
  border-radius: 50%;
  color: #fff;
  background-color: #ccc;
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
  width: 80%;
}
.blog_text:hover{
  border: none;
  cursor: pointer;
  color: #0fbcf9;
  letter-spacing: 1px;
}
.proportional_bar {
  border: none;
  height: 50%;
  width: 30%;
  background-color: #f5f7f800;
  /* border-radius: 6px; */
  margin-right: 5px;
}
.proportional_bar::before {
  content: "";
  display: block;
  padding-left: 5px;
  height: 16px;
  max-width: var(--width);
  background-color: #b3e2f3;
  bottom: -28px;
  border-radius: 6px;
  border: none;
  
}
.proportional_bar::before {
  background-image: linear-gradient(90deg, #06725b, #6bf2d0);
}
.proportional_bar::before {
  animation-duration: 1.2s;
  animation-fill-mode: forwards;
  animation-timing-function: ease-in-out;
}
.proportional_bar::before {
  animation-name: slide;
}
@keyframes slide {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}
</style>