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
        <div class="result" v-for="result in results" :key="result.url">
          <div class="info">
            <div class="text_title">{{ result.title }}</div>
          </div>
          <div class="text">
            {{ result.content | snippet }}
          </div>
          <div class="msg">
            作者: {{ result.author }} |   发布时间: {{ result.time }}
          </div>
          <div class="url">
            <a :href="result.url" target="_blank" class="view-detail">查看详情</a>
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
        results: [],
      };
    },
    filters: {
      // 过滤器: 显示摘要的前200个字符
      snippet(value) {
        if (value.length > 100) return value.slice(0, 100) + "...";
        return value;
      },
    },
    methods: {
      // 搜索人民网文章
      search() {
        this.searchResult = false;  // 初始化时先隐藏结果
        if (this.key_word.trim() === "") return; // 如果关键字为空，不执行搜索
        
        this.$axios
         .get(`search_tb?tag=${this.key_word}&cursor=1`)
         .then((res) => {
            console.log(res);
            // 处理后端返回的数据
            if (res.data && res.data.data) {
              this.results = res.data.data.map((item) => ({
                title: item.title,
                content: item.content,
                author: item.author,
                time: item.time,
                url: item.url,
              }));
              this.searchResult = true;  // 数据加载完后显示结果
            }
          })
         .catch((err) => {
            console.error("搜索失败:", err);
            this.searchResult = false; // 请求失败时隐藏结果
          });
      },
      // 添加任务（分析）
      add() {
        
        this.$confirm('此操作将分析该话题, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
        }).then(() => {
          this.$axios.get('add_task_tb?tag=' + this.key_word).then((res) => {
            console.log(res);
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
  
  <style scoped>
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
    border: 2px solid #fefeff6a;
    border-radius: 10px;
    color: #fff;
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
    color: #8d8787;
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
    z-index: 9;
    overflow: auto;
    border-right: 10px solid #ccc;
    border-left: 10px solid #ccc;
    border: 2px solid #fefeff6a;
    border-radius: 10px;
    color: #fff;
  }
 .searchResult::-webkit-scrollbar {
    display: none;
  }
 .info {
    display: flex;
  }
 .text_title {
    color: #f4f6f8;
    margin-top: 5px;
    margin-left: 20px;
    margin-bottom: 0px;
    font: 20px Helvetica, Verdana, Arial, SimHei, SimSun-ExtB;
    
    font-size: 23px;
  }
 .result {
    padding-top: 3px;
    height: 19vh;
    border-bottom: 2px solid #ffffffb9;
    display: flex;
    flex-direction: column;
  }
 .result:hover {
    background: #e7e7e277;
    box-shadow: #fafafa47 0 0 0;
    cursor: pointer;
  }
 .text {
    font-size: 18px;
    margin: 3px 0 0 20px;
    flex: 1;
    color: #eae6e6;
  }
 .title {
    font-size: 25px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 10px;
    border-bottom: 5px solid #f2f6fabc;
  }
 .close {
    position: absolute;
    top: 1px;
    right: 20px;
    font-size: 25px;
    color: #fffdfd;
    cursor: pointer;
    padding: 2px;
    transition: background-color 0.3s ease, transform 0.2s ease;
  }
 .close:hover {
    background-color: red;
    transform: scale(1.1);
  }
 .msg {
    font-size: 15px;
    margin-top: 2px;
    margin-bottom: 10px;
    margin-left: 20px;
    color: #eae6e6;
  }
 .analyze-btn {
    
    background-color: #37bff9;
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
    /* z-index: 9; */
    background-color: #29a0bb;
    transform: scale(1.05);
  }
  .view-detail {
    color: #f0ecec;
    margin-right: 10px;
    text-decoration: underline;
    text-align: right;
    display: block;
    margin-top: -2px;
    font-size: 15px;
  }
  .view-detail:hover {
    color: rgb(0, 255, 183);
    }
    /* 修改Element Plus提示框的z-index
    .el-message__wrapper,
    .el-confirm {
        z-index: 10000!important;
    } */
</style>