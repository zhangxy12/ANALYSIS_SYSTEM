<template>
  <div class="participation_list">
    <div class="participation_list_title">人员列表(按参与度排序)</div>
    <div class="participation_list_person_lists">
      <div
        class="participation_list_person_list"
        v-for="person in person_list"
        :key="person.index"
      >
        <div class="nf">
          <div class="person_head">
            <img :src="person.head" alt="" />
          </div>
          <div class="person_info">
            <div class="person_name">
              {{ person.nickname }}(@{{ person.nickname }})
            </div>
            <div class="person_time">{{ person.birthday }}</div>
            <div class="person_city">{{ person.location }}</div>

          </div>
        </div>
        <div class="mark">
          <span class="marks" v-for="(mark, index) in person.marks" :key="index">
            {{mark.name}}
          </span>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "participation_list",
  data() {
    return {
      person_list: [],
    };
  },
  methods: {
    getPersonList() {
      let query = this.$route.query;
      this.$axios.get("user_mark?tag_task_id=" + query.tag_task_id).then((res) => {
        console.log(res.data.data)
        this.person_list = res.data.data;
      });
    },
  },
  mounted() {
      this.getPersonList();
  },
};
</script>

<style scoped>
.participation_list_title {
  position: relative;
  margin: 10% auto;
  width: 25vw;
  font-size: 1.3rem;
  font-weight: 600;
  text-align: center;
}
.participation_list_person_lists {
  width: 25vw;
  height: 92vh;
  overflow: auto;
}

/* 自定义滚动条样式 */
.participation_list_person_lists::-webkit-scrollbar {
  width: 8px; /* 滚动条宽度 */
  height: 8px;
}

.participation_list_person_lists::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #18c7c7, #267d80); /* 滑块的渐变蓝色 */
  border-radius: 6px; /* 圆角处理 */
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2); /* 内阴影效果 */
}

.participation_list_person_lists::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #3399ff, #004c99); /* 滑块在鼠标悬停时变深 */
}

.participation_list_person_lists::-webkit-scrollbar-track {
  background: #f0f4f800; /* 滚动条轨道的背景色 */
  border-radius: 6px; /* 圆角处理 */
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1); /* 内阴影效果 */
}

.participation_list_person_list {
  height: 13vh;
  border-top: 1px solid #aaa;
}
.nf {
  display: flex;
}
.person_head img {
  margin: 20px 0 0 20px;
  height: 60px;
  width: 60px;
  border-radius: 50%;
}
.person_info {
  margin: 25px 0 0 20px;
  flex: 1;
}
.person_name {
  margin-bottom: 5px;
  color: deepskyblue;
}
.person_time {
  color: #aaa;
  font-size: 1rem;
}
.person_city {
  color: #aaa;
  font-size: 1rem;
}
.mark {
  margin: 10px 0 0 10px;
  font-size: 18px;
  font-weight: 600;
  color: #62acfc;
}
</style>
