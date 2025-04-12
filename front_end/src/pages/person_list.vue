<template>
  <div class="person_list">
    <!-- <div class="side">
      <SideBorder />
    </div> -->
    <div class="participation_list">
      <ParticipationList />
    </div>
    <div class="participation_graph">
      <ParticipationGraph />
    </div>
  </div>
</template>

<script>
import ParticipationList from "../components/person_list/participation_list";
import ParticipationGraph from "../components/person_list/participation_graph";

export default {
  name: "person_list",
  components: {
    ParticipationList,
    ParticipationGraph,
    
  },
};
</script>

<style scoped>
.person_list {
  display: flex;
  width: 100%;
  height: 120%;
  background-color: #ffffff00;
  background-image: url('../background/7.jpg'); /* 设置背景图片 */
  background-size: cover; /* 让背景图片自适应容器 */
  background-position: center; /* 背景图片居中 */
  background-attachment: fixed; /* 背景固定不随页面滚动 */
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.2); /* 增加一些阴影效果 */
}
.side{
    width: 50px;
}
.participation_list,
.participation_graph {
  float: left;
  position: relative;
  width: 25%;
  height: 100%;
  background-color: #ffffff00;
  margin-left: 0.5%;
  color:#ffff;

  border-radius: 10px;
  box-sizing: border-box;
  
  backdrop-filter: blur(3px); /* 添加磨砂玻璃效果 */
  -webkit-backdrop-filter: blur(10px); /* Safari 兼容 */
}
.participation_graph {
  width: 71%;
  position: relative;
}
</style>