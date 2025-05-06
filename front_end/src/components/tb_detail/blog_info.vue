<template>
  <div class="blog_info">
    <div class="blog_info_title">帖子详情</div>
    <div class="user_info">
      <!-- <div
        class="user_head"
        :style="{ backgroundImage: 'url(' + blog_info.user_head + ')' }"
      ></div> -->
      <div class="other_info">
        <div class="author">
          {{ blog_info.author }}
        </div>
        <div class="blog_time">{{ blog_info.time }}</div>
      </div>
    </div>
    <div class="title">
      {{ blog_info.title }}
    </div>
    <div class="blog_content">
      <span v-if="!show_detail">{{ content }}...</span>
      <span v-if="show_detail">{{ content_total }}</span>
      <div
        v-if="!show_detail"
        class="blog_info_show_detail"
        @click="showDetail"
      >
        展开
      </div>
      <div v-if="show_detail" class="blog_info_show_detail" @click="hideDetail">
        收起
      </div>
      <span v-html="'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'"></span>
      <!-- <span v-for="topic in blog_info.topics" :key="topic.index"
        >#{{ topic }}#</span
      > -->
    </div>
    <div class="follow_info"></div>
    <div class="comments" v-if="blog_info.comments && blog_info.comments.length > 1">
      <div class="comments_title">帖子评论</div>
      <!-- 从第二条评论开始遍历 -->
      
      <div v-for="comment in blog_info.comments.slice(1)" :key="comment.comment_time" class="comment_item">
        <!-- <dv-border-box-6 :color="['lightskyblue']">  -->
        <div class="comment_user_info">
          <div class="comment_user_name">{{ comment.user_name }}</div>
          <div class="comment_ip">{{ comment.ip }}</div>
          <div class="comment_time">{{ comment.comment_time }}</div>
        </div>
        <div class="comment_content">{{ comment.content }}</div>
      <!-- </dv-border-box-6> -->
      </div>
    
    </div>
    <div v-else>暂无更多评论显示</div>
  </div>
</template>

<script>
export default {
  name: "blog_info",
  data() {
    return {
      blog_info: {},
      show_detail: true,
      title: "",
      content: "",
      content_total: "",
    };
  },
  filters: {
    snippet(value) {
      if (value.length > 200) value = value.slice(0, 200) + "...";
      return value;
    },
  },
  methods: {
    getBlogInfo() {
      let query = this.$route.query;
      console.log(query.url);
      // 对 URL 参数进行编码
      const encodedUrl = encodeURIComponent(query.url);

      this.$axios
        .get(`comment/post_detail_tb?tag_task_id=${query.tag_task_id}&url=${encodedUrl}`)
        .then((res) => {
          this.blog_info = res.data.data;
          console.log(this.blog_info);
          // this.blog_info.user_head = res.data.data.original_pics[0];
          this.blog_info.title = res.data.data.title;
          this.blog_info.author = res.data.data.author;
          this.blog_info.time = res.data.data.time;
          this.content = res.data.data.content.slice(0, 150);
          this.content_total = res.data.data.content;

          if (this.content_total != this.content) {
            this.show_detail = false;
          }
        });
    },
    showDetail() {
      this.show_detail = true;
    },
    hideDetail() {
      this.show_detail = false;
    },
  },
  mounted() {
    this.getBlogInfo();
  },
};
</script>

<style scoped>
.blog_info {
  top: 1%;
  position: absolute;
  height: 95%;
  margin-left: 5px;
  margin-bottom: 5px;
  width: 100%;
  background-color: #ffffff00;
  color:#ffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
  border: 2px solid #669ef3a5; /* 深色边框 */
  border-radius: 10px;
  box-sizing: border-box;
  
  backdrop-filter: blur(3px); /* 添加磨砂玻璃效果 */
  -webkit-backdrop-filter: blur(10px); /* Safari 兼容 */
  overflow: hidden;
}
.blog_info_title {
  margin: 10px 20px;
  padding: 0px;
  font-weight: 400;
  letter-spacing: 1px;
}
.title {
  font-size: 22px;
}

.user_info {
  margin-left: 20px;
}
.user_head {
  width: 30px;
  height: 30px;
  background-size: cover;
}
.other_info {
  display: inline-block;
  margin-left: 20px;
  font-size: 12px;
}
.author {
  font-size: 14px;
}
.blog_time {
  color: #aaa;
  font-size: 12px;
}
.blog_content {
  font-size: 16px;
  margin: 5px 10px;
}
.follow_info {
  margin: 10px 20px;
  font-size: 13px;
  color: #aaa;
  padding-bottom: 10px;
}
.blog_info_show_detail {
  display: inline-block;
  color: skyblue;
  cursor: default;
}
.blog_info_show_detail:hover {
  font-weight: 400;
}

.comments {
  height: 380px; /* 可以根据需要调整高度 */
  overflow-y: auto; /* 当内容超出高度时显示垂直滚动条 */
  
  /* margin-top: 20px;
  overflow-y: auto; */
  /* 自定义滚动条样式 */
  scrollbar-width: none; 
}

.comments_title {
  font-weight: bold;
  margin-bottom: 10px;
}

.comment_item {
  padding: 10px;
  border: 1px solid #aaa;
  border-radius: 5px;
  margin-bottom: 10px;
}

.comment_user_info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment_user_name {
  font-weight: bold;
}

.comment_ip {
  color: #dedddd;;
}

.comment_time {
  color: #dedddd;;
}

.comment_content {
  line-height: 1.5;
}
</style>