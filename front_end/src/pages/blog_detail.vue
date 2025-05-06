<template>
  <div class="blog_detail">
    <!-- <div class="side">
      <SideBorder />
    </div> -->
    <div class="detail_contain">
      <div class="blog_detail_left">
        <div class="left_blog_info">
          <BlogInfo />
        </div>
        <div class="left_essential_node">
          <SentimentTrand />
        </div>
      </div>
      <div class="blog_detail_center">
        <div class="center_locationh">
          <Location />
        </div>
        <div class="center_Info" style="height: 45%;">
          <Info />
        </div>
      </div>
      <div class="blog_detail_right">
        <div class="right_cloud_graph">
          <CloudGraph />
        </div>
        <div class="right_hot_point">
          <SentimentAna />
        </div>
      </div>
    </div>
  </div>
</template>


<script>
// import SideBorder from "../components/Side_border";
import BlogInfo from "../components/blog_detail/blog_info";
import CloudGraph from "../components/blog_detail/cloud_graph";

import SentimentTrand from "../components/blog_detail/sentiment_trand";
import SentimentAna from "../components/blog_detail/sentiment_ana";
import Location from "../components/blog_detail/location";
import Info from "../components/blog_detail/information_extraction";

export default {
  name: "blog_detail",
  components: {
  
    BlogInfo,
    CloudGraph,
 
    SentimentTrand,
    SentimentAna,
    Location,
    Info,
  },
};
</script>

<style>
.blog_detail {
  width: 100%;
  display: flex;
  height: 100%;
}

.blog_detail_left,
.blog_detail_right {
  float: left;
  height: 100%;
  position: relative;
}

.side {
  width: 50px;
}

.detail_contain {
  background-color: #eee;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row; /* 保证布局为行排列 */

  background: linear-gradient(to right, #086264, #229fe2d6);
}

/* 左侧内容 */
.blog_detail_left {
  width: 30%; /* 左侧区域宽度 */
  height: 100%; /* 使其高度为总高度的 50% */
  padding-right: 10px; /* 添加右侧间距 */
}

/* 中间部分 */
.blog_detail_center {
  position: relative;
  width: 37%;
  height: 100%; 
  float: left;
  margin: 0 10px;
}
.center_location_Info {
  display: flex;
  flex-direction: column; /* 垂直排列 */
  height: 40%; /* 占满父容器的高度 */
}

/* Location 部分 */
.center_location {
  
  height: 60%;
}

/* Ifno 部分 */
.center_Info {
  margin-top: 10px;
  height: 40%;
}

/* 右侧内容 */
.blog_detail_right {
  width: 30%; /* 右侧区域宽度 */
  padding-left: 10px; /* 添加左侧间距 */
  height: 100%; /* 右侧区域的高度为 100% */
}

</style>