<template>
  <div class="search">
    <div class="input">
      <input
        type="text"
        v-model="key_word"
        class="key"
        placeholder="搜索话题"
      />
    </div>
    <div class="search_button">
      <button @click="search()">搜索</button>
    </div>
    <div class="searchResult" v-show="searchResult">
      <div class="title">
        有关{{ key_word }}的话题
        <button @click="add()" class="analyze-btn">分析</button>
        <div class="close" @click="searchResult = false">
          <i class="el-icon-close"></i>
        </div>
      </div>
      <div class="result" v-for="result in results" :key="result.weibo_id">
        <div class="userinfo">
          <div class="userAvator">
            <img class="headimg" :src="result.head" alt="" />
          </div>
          <div class="user">
            <div class="username">{{ result.screen_name }}</div>
            <div class="other-info">{{ result.created_at }}</div>
          </div>
        </div>
        <div class="text">
          {{ result.text | snippet }}
        </div>
        <div class="msg">
          评论[{{result.comments_count}}]
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "search",
  data() {
    return {
      key_word: "",
      searchResult: false,
      results: "",
    };
  },
  //定义过滤器超多20个字
  filters: {
    snippet(value) {
      if (value.length > 150) return value.slice(0, 150) + "...";
      return value;
    },
  },
  methods: {
    search() {
      // console.log(this.key_word);
      this.searchResult = true;
      this.$axios.get("search?tag="+ this.key_word + "&cursor=1").then((res) => {
        console.log(res)
        this.results = res.data.data.result;
      });
    },
    add(){
      
      this.$confirm('此操作将分析该话题, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      }).then(() => {
        this.$axios.get('add_task?tag=' + this.key_word).then((res) =>{
          console.log(res)
        });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消分析'
        });
      });
    }
  },
};
</script>

<style scpoed>
.search {
  
  display: flex;
}
.input {
  position: relative;
  top: 5px;
  margin: 0 10px;
  width: 50%;
  height: 70%;
  background-color: #ffffff00;
  border: 1px solid #ccc;
  border: 2px solid #fefeff6a; /* 深色边框 */
  border-radius: 10px;
  color:#fff
}
.key {
  width: 570px;
  height: 24px;
  margin: 7px 10px;
  outline: none;
  border: 0;
  font-size: 20px;
  letter-spacing: 1px;
  background-color: #ffffff00;
  color: #fff;
}
.key::placeholder {
  color: #8d8787; /* 设置placeholder文字为白色 */
}
.search_button {
  margin: 6px;
}
.search_button button {
  background-color: hsla(166, 74%, 51%, 0.753);
  border-radius: 14px;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 1px;
  width: 80px;
  height: 40px;
}
.searchResult {
  position: absolute;
  width: 100%;
  height: 100vh;
  background: linear-gradient(to right, #0e3f46, #2d66acd6);
  z-index: 99;
  overflow: auto;
  border-right: 10px solid #ccc;
  border-left: 10px solid #ccc;
  border: 2px solid #fefeff6a; /* 深色边框 */
  border-radius: 10px;
  color: #fff;
}
.searchResult::-webkit-scrollbar {
  display: none;
}
.userinfo {
  display: flex;
}
.userAvator {
  width: 70px;
  height: 70px;
  margin-right: 15px;
  margin-left: 20px;
}
.headimg{
  width: 70px;
  height: 70px;
  border-radius: 50%;
}
.username {
  color: #f4f6f8;
  margin-top: 15px;
  font: 20px Helvetica,Verdana,Arial,SimHei,SimSun-ExtB;
  margin-bottom: 5px;
}
.result {
  padding-top: 15px solid #346ead89;
  height: 20vh;
  font-size: 15px;
  border-bottom: 2px solid #ffffffb9;
  display: flex;
  flex-direction: column;
}
.other-info{
  color: #fffeff;
}
.result:hover{
  background: #c9c9c3b9;
  box-shadow: #fafafa89 0 0 0;
  cursor: pointer;
}
.text {
  
  margin: 20px 0 0 20px;
  flex: 1;
}
.title {
  font-size: 20px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 10px;
  border-bottom: 5px solid #f2f6fabc;
}
/* 修改关闭按钮的位置和样式 */
.close {
  position: absolute;
  top: 1px;
  right: 20px; /* 使叉叉按钮更靠近右上角 */
  font-size: 25px; /* 增加大小 */
  color: #fffdfd;
  cursor: pointer;
  
  /* border-radius: 100%; */
  padding: 2px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}
.close:hover {
  background-color: red; /* 鼠标悬停时，背景变为红色 */
  transform: scale(1.1); /* 鼠标悬停时按钮略微放大 */
}

.msg{
  margin-bottom: 10px;
  margin-left: 20px;
  color: #ffffff;
}


/* 修改“分析”按钮的样式 */
.analyze-btn {
  background-color: #37bff9; /* 明亮的橙色 */
  color: #fff;
  font-size: 18px;
  padding: 8px 15px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  margin-left: 20px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.analyze-btn:hover {
  background-color: #29a0bb; /* 橙色变暗 */
  transform: scale(1.05); /* 鼠标悬停时放大按钮 */
}

</style>