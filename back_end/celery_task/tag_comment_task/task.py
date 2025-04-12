"""
task，将模型与数据处理部分分离
计划仅由本文件提供task任务
"""
import time
import json
from collections import Counter, defaultdict

import pymongo
import requests
from bson import ObjectId

from celery_task.config import mongo_conf
from celery_task.tieba_crawler.tb_comments import crawl_tieba_comments
from celery_task.utils import mongo_client

from celery_task import celeryapp
from celery_task.tag_comment_task.process import get_path_tree_part
from celery_task.utils.gsdmmCluster.cluster_extract import cluster_extract
from celery_task.tag_comment_task.my_cloud import preContent, preContent_tb
from celery_task.tag_comment_task.myRank import startRank
from celery_task.tag_comment_task.repost_spider import spider_list
from celery_task.utils.my_db import Mongo
from snownlp import SnowNLP

# 新增情感分析字段到数据库
import logging
from datetime import datetime


def add_sentiment_analysis_to_comments(tag_comment_task_id):
    comments = mongo_client.db[mongo_conf.COMMENT_TASK].find({"tag_comment_task_id": tag_comment_task_id})

    for comment in comments:
        # 检查detail是否存在且包含comments
        if "detail" in comment and "comments" in comment["detail"]:
            if comment["detail"]["comments"]:  # 如果comments数组不为空
                updated_comments = []
                for i, cmt in enumerate(comment["detail"]["comments"]):
                    try:
                        sentiment = analyze_sentiment(cmt["content"])  # 情感分析
                    except ZeroDivisionError as e:
                        # 记录详细错误日志，便于排查问题
                        logging.error(f"在分析评论 {cmt['content']} 的情感时出现除零错误，具体错误: {str(e)}")
                        # 这里可以根据业务需求返回一个合适的默认情感分析结果，比如设置为中性且分数为0.5
                        sentiment = {"sentiment": "neutral", "score": 0.5}
                    cmt["sentiment_analysis"] = sentiment  # 将分析结果保存到评论字段中
                    updated_comments.append(cmt)

                # 更新数据库
                mongo_client.db[mongo_conf.COMMENT_TASK].update_one(
                    {"tag_comment_task_id": tag_comment_task_id},
                    {"$set": {"detail.comments": updated_comments}}
                )
            else:
                # 记录评论为空的情况
                print(f"Warning: No comments found for task {tag_comment_task_id}")
        else:
            # 记录缺少comment或detail字段的情况
            print(f"Warning: No 'comments' field found for task {tag_comment_task_id}")


def add_sentiment_analysis_to_comments_tb(tag_comment_task_id):
    print("mood_begin1")
    comments = mongo_client.db[mongo_conf.TB_COMMENT_TASK].find({"tag_comment_task_id": tag_comment_task_id})

    for comment in comments:
        # 检查detail是否存在且包含comments
        if "detail" in comment and "comments" in comment["detail"]:
            if comment["detail"]["comments"]:  # 如果comments数组不为空
                updated_comments = []
                for i, cmt in enumerate(comment["detail"]["comments"]):
                    try:
                        sentiment = analyze_sentiment(cmt["content"])  # 对评论内容进行情感分析
                    except ZeroDivisionError as e:
                        # 记录详细错误日志，便于排查问题
                        logging.error(f"在分析评论 {cmt['content']} 的情感时出现除零错误，具体错误: {str(e)}")
                        # 这里可以根据业务需求返回一个合适的默认情感分析结果，比如设置为中性且分数为0.5
                        sentiment = {"sentiment": "neutral", "score": 0.5}
                    cmt["sentiment_analysis"] = sentiment  # 将分析结果保存到评论字段中

                    updated_comments.append(cmt)

                # 更新数据库
                mongo_client.db[mongo_conf.TB_COMMENT_TASK].update_one(
                    {"tag_comment_task_id": tag_comment_task_id},
                    {"$set": {"detail.comments": updated_comments}}
                )
            else:
                # 记录评论为空的情况
                print(f"Warning: No comments found for task {tag_comment_task_id}")
        else:
            # 记录缺少comment或detail字段的情况
            print(f"Warning: No 'comments' field found for task {tag_comment_task_id}")


def get_sentiment_tb(tag_comment_task_id):
    print("mood_begin2")
    # 初始化情感统计字典
    sentiment_count = defaultdict(int)
    sentiment_by_date = {}  # 用于存储每一天的情感统计

    # 从 TB_COMMENT_TASK 集合中查询指定 tag_comment_task_id 的文档
    comments = mongo_client.db[mongo_conf.TB_COMMENT_TASK].find({"tag_comment_task_id": tag_comment_task_id})

    for comment in comments:
        # 检查 detail 和 comments 字段是否存在
        if "detail" in comment and "comments" in comment["detail"]:
            for cmt in comment["detail"]["comments"]:
                # 统计评论的情感分析结果
                if "sentiment_analysis" in cmt:
                    sentiment = cmt["sentiment_analysis"].get("sentiment")
                    if sentiment:
                        sentiment_count[sentiment] += 1

                        # 统计按日期变化的情感
                        comment_time = cmt.get('comment_time')
                        if comment_time:
                            try:
                                # 将日期字符串转换为日期对象
                                date_obj = datetime.strptime(comment_time, '%Y-%m-%d %H:%M').date()
                                date_str = str(date_obj)
                                if date_str not in sentiment_by_date:
                                    sentiment_by_date[date_str] = Counter()
                                sentiment_by_date[date_str][sentiment] += 1
                            except ValueError:
                                print(f"日期格式错误: {comment_time}，跳过该条数据。")

    # 对日期进行从最远到最近排序
    sorted_dates = sorted(sentiment_by_date.keys(), reverse=False)  # 显式指定升序排序
    sorted_sentiment_by_date = {date: dict(sentiment_by_date[date]) for date in sorted_dates}

    # 情感分析结果统计
    statistics = {
        'total_sentiment': dict(sentiment_count),
        'sentiment_by_date': sorted_sentiment_by_date
    }

    # 构建存储到 TB_COMMENT_MOOD 的数据结构
    query_by_task_id = {'tag_task_id': tag_comment_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.TB_COMMENT_MOOD].update_one(query_by_task_id, update_data, upsert=True)


# 情感分析函数
def analyze_sentiment(text):
    try:
        s = SnowNLP(text)
        sentiment_score = s.sentiments  # 得到情感极性评分 (0到1)，越接近1表示情感越正面
    except ZeroDivisionError as e:
        # 记录详细错误日志
        logging.error(f"在使用SnowNLP处理文本 {text} 进行情感分析时出现除零错误，具体错误: {str(e)}")
        # 返回默认的情感分析结果，这里设置为中性且分数为0.5，可根据业务实际调整
        return {"sentiment": "neutral", "score": 0.5}

    # 根据得分判断情感类型
    if sentiment_score > 0.7:
        return {"sentiment": "positive", "score": sentiment_score}
    elif sentiment_score < 0.3:
        return {"sentiment": "negative", "score": sentiment_score}
    else:
        return {"sentiment": "neutral", "score": sentiment_score}


def init_task(tag_comment_task_dict):
    """
    # 微博评论任务id的储存
    :param tag_comment_task_dict:
    :return:
    """
    tree_id = mongo_client.db[mongo_conf.COMMENT_TREE].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    cluster_id = mongo_client.db[mongo_conf.COMMENT_CLUSTER].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    cloud_id = mongo_client.db[mongo_conf.COMMENT_CLOUD].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    tendency_id = mongo_client.db[mongo_conf.COMMENT_TENDENCY].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    key_node_id = mongo_client.db[mongo_conf.COMMENT_NODE].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})

    tag_comment_task_dict["tree_id"] = str(tree_id.inserted_id)
    tag_comment_task_dict["cluster_id"] = str(cluster_id.inserted_id)
    tag_comment_task_dict["cloud_id"] = str(cloud_id.inserted_id)
    tag_comment_task_dict["tendency_id"] = str(tendency_id.inserted_id)
    tag_comment_task_dict["key_node_id"] = str(key_node_id.inserted_id)

    return tag_comment_task_dict


def main_init_task(tag_comment_task_dict):
    """
    # 微博评论任务id的储存
    :param tag_comment_task_dict:
    :return:
    """
    ip_id = mongo_client.db[mongo_conf.TB_COMMENT_IP].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    tag_comment_task_dict["ip_id"] = str(ip_id.inserted_id)

    return tag_comment_task_dict


def init_task_tb(tag_comment_task_dict):
    """
    # 贴吧评论任务id的储存
    :param tag_comment_task_dict:
    :return:
    """
    cloud_id = mongo_client.db[mongo_conf.TB_COMMENT_CLOUD].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    ip_id = mongo_client.db[mongo_conf.TB_COMMENT_IP].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    mood_id = mongo_client.db[mongo_conf.TB_COMMENT_MOOD].insert_one(
        {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})
    # key_node_id = mongo_client.db[mongo_conf.COMMENT_NODE].insert_one(
    #     {"tag_comment_task_id": tag_comment_task_dict["tag_comment_task_id"]})

    tag_comment_task_dict["cloud_id"] = str(cloud_id.inserted_id)
    tag_comment_task_dict["ip_id"] = str(ip_id.inserted_id)
    tag_comment_task_dict["mood_id"] = str(mood_id.inserted_id)
    # tag_comment_task_dict["key_node_id"] = str(key_node_id.inserted_id)

    return tag_comment_task_dict


# 获取微博详细信息
def get_post_detail(weibo_id: str, tag_comment_task_id: str):
    print("get_post_detail beginning")
    response = requests.get("http://127.0.0.1:8000/weibo_curl/api/statuses_show?weibo_id={weibo_id}".
                            format(weibo_id=weibo_id), verify=False)
    weibo_dict = json.loads(response.text)
    mongo_client.db[mongo_conf.COMMENT_TASK].update_one({'tag_comment_task_id': tag_comment_task_id},
                                                        {"$set": {'detail': weibo_dict["data"]["result"]}})


def main_get_post_detail(weibo_id: str, date: str):
    print("get_post_detail beginning")
    response = requests.get("http://127.0.0.1:8000/weibo_curl/api/statuses_show?weibo_id={weibo_id}".
                            format(weibo_id=weibo_id), verify=False)
    try:
        weibo_dict = response.json()
        new_doc = {
            'date': date,
            'weibo_id': weibo_id,
            'detail': weibo_dict["data"]["result"]
        }
        mongo_client.db[mongo_conf.ALL_COMMENT].insert_one(new_doc)
        print(f"成功插入新文档，日期: {date}, 微博ID: {weibo_id}")
    except KeyError:
        print("响应数据中缺少 'data' 或 'result' 键。")
    except json.JSONDecodeError:
        print("无法将响应内容解析为JSON。")
    except Exception as e:
        print(f"插入文档时出现错误: {e}")



# 获取贴吧详细信息
def get_post_detail_tb(url: str, tag_comment_task_id: str):
    print("get_post_detail beginning")
    # 调用爬取评论的函数
    all_comments = crawl_tieba_comments(url)

    # 获取对应文档
    doc = mongo_client.db[mongo_conf.TB_COMMENT_TASK].find_one({'tag_comment_task_id': tag_comment_task_id})

    if doc:
        if 'detail' not in doc:
            # 如果 detail 字段不存在，创建一个空字典
            mongo_client.db[mongo_conf.TB_COMMENT_TASK].update_one(
                {'tag_comment_task_id': tag_comment_task_id},
                {"$set": {'detail': {}}}
            )
        elif not isinstance(doc['detail'], dict):
            # 如果 detail 字段存在但不是字典类型，将原内容保留在新字典的某个字段中
            original_detail = doc['detail']
            mongo_client.db[mongo_conf.TB_COMMENT_TASK].update_one(
                {'tag_comment_task_id': tag_comment_task_id},
                {"$set": {'detail': {'base_value': original_detail}}}
            )

        # 检查 detail 中是否已经存在 comments 字段
        doc = mongo_client.db[mongo_conf.TB_COMMENT_TASK].find_one({'tag_comment_task_id': tag_comment_task_id})
        if 'comments' in doc['detail']:
            # 如果存在，使用 $push 追加新评论
            mongo_client.db[mongo_conf.TB_COMMENT_TASK].update_one(
                {'tag_comment_task_id': tag_comment_task_id},
                {"$push": {'detail.comments': {"$each": all_comments}}}
            )
        else:
            # 如果不存在，使用 $set 创建 comments 字段并赋值
            mongo_client.db[mongo_conf.TB_COMMENT_TASK].update_one(
                {'tag_comment_task_id': tag_comment_task_id},
                {"$set": {'detail.comments': all_comments}}
            )
    else:
        print(f"未找到 tag_comment_task_id 为 {tag_comment_task_id} 的文档。")


# 聚类任务
def run_by_task_id_part(tag_comment_task_id, doc_id):
    post_list = []
    for post in mongo_client.db[mongo_conf.COMMENT_REPOSTS].find({'tag_comment_task_id': tag_comment_task_id}):
        if post['content'].strip() == "" or post['content'].strip() == "转发微博":
            continue

        post_list.append({'_id': post['_id'], 'fulltext': post['content']})
    result = cluster_extract(post_list)
    mydict = result.to_dict(orient='index')
    key_list = list(mydict.keys())
    for key in key_list:
        mydict[str(key)] = mydict.pop(key)
        while '' in mydict[str(key)]["content"]:
            mydict[str(key)]["content"].remove('')
    mongo_client.db[mongo_conf.COMMENT_CLUSTER].update_one({"_id": ObjectId(doc_id)}, {"$set": {"data": mydict}})


def getIP_tb(tag_comment_task_id: str):
    print("getip_begin")
    try:
        # 获取所有评论的地理位置信息
        comments = mongo_client.db[mongo_conf.TB_COMMENT_TASK].find_one({"tag_comment_task_id": tag_comment_task_id})
        if not comments or "detail" not in comments:
            print("没有找到评论数据")
            return

        comment_data = comments.get("detail", {}).get("comments", [])
        print(comment_data)
        # 统计评论者的地理位置
        location_count = Counter()
        for comment in comment_data:
            location = comment.get("ip", None)
            if location:
                location_count[location] += 1

        print(location_count)
        # 将统计结果转为前端可用的格式
        location_data = [{"location": loc, "count": count} for loc, count in location_count.items()]
        print(location_data)
        # 存储结果到 TB_COMMENT_IP 数据库
        mongo_client.db[mongo_conf.TB_COMMENT_IP].update_one({'tag_comment_task_id': tag_comment_task_id},
                                                             {"$set": {'detail': location_data}})

        print(f"统计结果已存储到 {mongo_conf.TB_COMMENT_IP} 数据库中")

    except Exception as e:
        print(f"处理过程中出现错误: {e}")


def main_getIP(date: str):
    print("getip_begin")
    try:
        # 初始化计数器
        location_count = Counter()

        # 遍历所有符合 date 的文档
        comment_docs = mongo_client.db[mongo_conf.ALL_COMMENT].find({"date": date})
        for comment_doc in comment_docs:
            if "detail" not in comment_doc:
                continue
            comment_data = comment_doc["detail"].get("comments", [])
            for comment in comment_data:
                # 获取 publish_tool 字段作为 ip
                ip = comment.get("publish_tool", None)
                if ip:
                    location_count[ip] += 1

        print(location_count)
        # 将统计结果转为前端可用的格式
        location_data = [{"location": loc, "count": count} for loc, count in location_count.items()]
        print(location_data)

        # 检查数据库中是否已有该日期的文档
        existing_doc = mongo_client.db[mongo_conf.ALL_COMMENT_IP].find_one({'date': date})
        if existing_doc:
            existing_details = {item["location"]: item["count"] for item in existing_doc["detail"]}
            for new_item in location_data:
                location = new_item["location"]
                count = new_item["count"]
                if location in existing_details:
                    existing_details[location] += count
                else:
                    existing_details[location] = count
            updated_details = [{"location": loc, "count": cnt} for loc, cnt in existing_details.items()]
            mongo_client.db[mongo_conf.ALL_COMMENT_IP].update_one(
                {'date': date},
                {"$set": {'detail': updated_details}}
            )
        else:
            # 若文档不存在则插入
            mongo_client.db[mongo_conf.ALL_COMMENT_IP].insert_one(
                {'date': date, 'detail': location_data}
            )

        print(f"统计结果已存储到 {mongo_conf.ALL_COMMENT_IP} 数据库中")

    except Exception as e:
        print(f"处理过程中出现错误: {e}")


# 调度任务
@celeryapp.task(bind=True)
def comment_task_schedule(self, tag_comment_task_dict):
    print(tag_comment_task_dict)
    # 爬虫任务
    print('开始评论爬虫任务')
    self.update_state(state='PROGRESS',
                      meta={'current': "爬虫任务", 'weibo_id': tag_comment_task_dict['weibo_id'],
                            'task_id': tag_comment_task_dict['tag_comment_task_id']})
    get_post_detail(weibo_id=tag_comment_task_dict['weibo_id'],
                    tag_comment_task_id=tag_comment_task_dict['tag_comment_task_id'])
    # spider_list(tag_task_id=tag_comment_task_dict['tag_task_id'], weibo_id=tag_comment_task_dict['weibo_id'],
    #                   tag_comment_task_id=tag_comment_task_dict['tag_comment_task_id'])
    print('评论爬虫任务结束')

    print('开始传播分析-词云任务')
    self.update_state(state='PROGRESS',
                      meta={'current': "传播分析-词云", 'weibo_id': tag_comment_task_dict['weibo_id'],
                            'task_id': tag_comment_task_dict['tag_comment_task_id']})
    preContent(tag_comment_task_id=tag_comment_task_dict['tag_comment_task_id'],
               doc_id=tag_comment_task_dict['cloud_id'])
    print('传播分析-词云任务结束')
    # 执行情感分析任务
    print('开始情感分析任务')
    add_sentiment_analysis_to_comments(tag_comment_task_dict['tag_comment_task_id'])
    print('情感分析任务结束')


#大屏可视化ip
@celeryapp.task(bind=True)
def main_comment_task_schedule(self, tag_comment_task_dict):
    print(tag_comment_task_dict)
    # 爬虫任务
    print('开始评论爬虫任务')
    main_get_post_detail(weibo_id=tag_comment_task_dict['weibo_id'],
                         date=tag_comment_task_dict['date'])

    print('评论爬虫任务结束')

    print('开始传播分析-IP任务')
    print("getIP")
    main_getIP(date=tag_comment_task_dict['date'])
    print('传播分析-IP任务结束')



# tb调度任务
@celeryapp.task(bind=True)
def comment_task_schedule_tb(self, tag_comment_task_dict):
    print(tag_comment_task_dict)
    # 爬虫任务
    print('开始评论爬虫任务')
    self.update_state(state='PROGRESS',
                      meta={'current': "爬虫任务", 'url': tag_comment_task_dict['url'],
                            'task_id': tag_comment_task_dict['tag_comment_task_id']})
    get_post_detail_tb(url=tag_comment_task_dict['url'],
                       tag_comment_task_id=tag_comment_task_dict['tag_comment_task_id'])
    # spider_list(tag_task_id=tag_comment_task_dict['tag_task_id'], weibo_id=tag_comment_task_dict['weibo_id'],
    #                  tag_comment_task_id=tag_comment_task_dict['tag_comment_task_id'])
    print('评论爬虫任务结束')

    print('开始传播分析-词云任务')
    self.update_state(state='PROGRESS',
                      meta={'current': "传播分析-词云", 'url': tag_comment_task_dict['url'],
                            'task_id': tag_comment_task_dict['tag_comment_task_id']})
    preContent_tb(tag_comment_task_id=tag_comment_task_dict['tag_comment_task_id'],
                  doc_id=tag_comment_task_dict['cloud_id'])
    print('传播分析-词云任务结束')

    print('开始传播分析-IP任务')
    self.update_state(state='PROGRESS',
                      meta={'current': "传播分析-IP", 'url': tag_comment_task_dict['url'],
                            'task_id': tag_comment_task_dict['tag_comment_task_id']})
    print("getIP_tb")
    getIP_tb(tag_comment_task_id=tag_comment_task_dict['tag_comment_task_id'])
    print('传播分析-IP任务结束')

    # 执行情感分析任务
    print('开始情感分析任务')
    add_sentiment_analysis_to_comments_tb(tag_comment_task_dict['tag_comment_task_id'])
    get_sentiment_tb(tag_comment_task_dict['tag_comment_task_id'])
    print('情感分析任务结束')


# 初始化微博任务
def start_task(tag_task_id: str, weibo_post=None):
    # todo 错误处理
    # 时间戳->字符串
    time_int = int(time.time())
    time_array = time.localtime(time_int)
    time_style_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)

    tag_comment_task_id = str(time_int) + weibo_post['weibo_id']
    task_dict = {"tag_task_id": tag_task_id, "weibo_id": weibo_post['weibo_id'],
                 "tag_comment_task_id": tag_comment_task_id,
                 'created_time': time_style_str}

    task_dict = init_task(task_dict)

    task = comment_task_schedule.delay(tag_comment_task_dict=task_dict)
    task_dict['celery_id'] = task.id
    # weibo_detail = get_post_detail(weibo_id=weibo_id)
    # task_dict["detail"] = weibo_post
    task_dict["analysis_status"] = "PENDING"
    # mongo_client.db[mongo_conf.COMMENT_TASK].insert_one(task_dict)
    task_dict.pop("_id")
    # print(task_dict)
    return task_dict


def main_start_task(date: str, weibo_post=None):
    # todo 错误处理
    # 时间戳->字符串
    time_int = int(time.time())
    time_array = time.localtime(time_int)
    time_style_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)

    tag_comment_task_id = str(time_int) + weibo_post['weibo_id']
    task_dict = {"date": date, "weibo_id": weibo_post['weibo_id'],
                 "tag_comment_task_id": tag_comment_task_id,
                 'created_time': time_style_str}

    task_dict = main_init_task(task_dict)

    task = main_comment_task_schedule.delay(tag_comment_task_dict=task_dict)
    task_dict['celery_id'] = task.id
    # task_dict["detail"] = weibo_post
    # task_dict["analysis_status"] = "PENDING"
    # mongo_client.db[mongo_conf.ALL_COMMENT].insert_one(task_dict)
    # task_dict.pop("_id")

    return


# 初始化贴吧评论任务
def start_task_tb(tag_task_id: str, tb_post=None):
    # 时间戳->字符串
    time_int = int(time.time())
    time_array = time.localtime(time_int)
    time_style_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)

    tag_comment_task_id = tb_post['url']
    task_dict = {"tag_task_id": tag_task_id, "url": tb_post['url'],
                 "tag_comment_task_id": tag_comment_task_id,
                 'created_time': time_style_str}

    task_dict = init_task_tb(task_dict)

    task = comment_task_schedule_tb.delay(tag_comment_task_dict=task_dict)
    task_dict['celery_id'] = task.id
    # weibo_detail = get_post_detail(weibo_id=weibo_id)
    task_dict["detail"] = tb_post
    task_dict["analysis_status"] = "PENDING"
    mongo_client.db[mongo_conf.TB_COMMENT_TASK].insert_one(task_dict)
    task_dict.pop("_id")
    print(task_dict)
    return task_dict


# 刷新任务
def refresh_task():
    mydb = mongo_client.db[mongo_conf.COMMENT_TASK]
    for item in mydb.find():
        try:
            if item['analysis_status'] != "SUCCESS":
                task = celeryapp.AsyncResult(item['celery_id'])
                if task.state == "PROGRESS":
                    mydb.update_one({"_id": item['_id']},
                                    {"$set": {"analysis_status": task.info.get('current', 0)}})
                else:
                    mydb.update_one({"_id": item['_id']}, {"$set": {"analysis_status": task.state}})
        except Exception:
            print(item['tag_comment_task_id'], '刷新任务失败')
            print(item)


# 获取任务队列
def getTaskList():
    result = {"error_code": 0, "error_msg": "", "data": []}
    # 获取task库,更新task状态
    mydb = mongo_client.db[mongo_conf.COMMENT_TASK]
    for item in mydb.find():
        try:
            if item['analysis_status'] != "SUCCESS":
                task = celeryapp.AsyncResult(item['celery_id'])
                if task.state == "PROGRESS":
                    item['analysis_status'] = task.info.get('current', 0)
                    mydb.update_one({"_id": item['_id']},
                                    {"$set": {"analysis_status": task.info.get('current', 0)}})
                else:
                    item['analysis_status'] = task.state
                    mydb.update_one({"_id": item['_id']}, {"$set": {"analysis_status": task.state}})
            item.pop("_id")
            result["data"].append(item)
        except Exception as e:
            print(e)
            print(item)
    return result


# 删除任务
def deleteTask(tag_comment_task_id):
    mydb = mongo_client.db[mongo_conf.COMMENT_TASK]
    celeryapp.control.revoke(tag_comment_task_id, terminate=True)
    myquery = {"tag_comment_task_id": tag_comment_task_id}
    mydb.delete_one(myquery)
    mongo_client.db[mongo_conf.COMMENT_TREE].delete_one(myquery)
    mongo_client.db[mongo_conf.COMMENT_CLUSTER].delete_one(myquery)


# 统计每天的转发
def spreadTendency(tag_comment_task_id=None, doc_id=None):
    # if task_id is None or task_id.__len__() == 0:
    #     return {"error_code": 1, "error_msg": "缺少task_id"}
    pipeline = [
        {'$project': {'day': {'$substr': ["$created_at", 0, 10]}, 'tag_comment_task_id': '$tag_comment_task_id'}},
        {'$group': {'_id': {'data': '$day', 'tag_comment_task_id': '$tag_comment_task_id'}, 'count': {'$sum': 1}}},
        {'$sort': {"_id.data": 1}},
        {'$match': {'_id.tag_comment_task_id': tag_comment_task_id}}
    ]
    result = []
    mydb = mongo_client.db[mongo_conf.COMMENT_REPOSTS]
    for i in mydb.aggregate(pipeline):
        print('reports:', i)
        result.append({"key": i['_id']["data"], "doc_count": i["count"]})
    mongo_client.db[mongo_conf.COMMENT_TENDENCY].update_one({"tag_comment_task_id": tag_comment_task_id},
                                                            {"$set": {"data": result}})


# 以task_id获取 趋势 内容
def getByTendencyId(tag_comment_task_id=None):
    item = mongo_client.db[mongo_conf.COMMENT_TENDENCY].find_one({"tag_comment_task_id": tag_comment_task_id})
    item.pop("_id")
    data_time = []
    data_count = []
    for i in item["data"]:
        data_time.append(i["key"])
        data_count.append(i["doc_count"])
    data = {"data_time": data_time, "data_count": data_count}
    item["data"] = data
    print(item)
    return item


# 以task_id获取 词云 内容
def getByCloudId(tag_comment_task_id=None):
    # item = mydb['cloud'].find_one({"_id": ObjectId(doc_id)})
    item = mongo_client.db[mongo_conf.COMMENT_CLOUD].find_one({"tag_comment_task_id": tag_comment_task_id})
    item.pop("_id")
    print(item)
    return item


# 以task_id 获取 聚类 内容
def getByClusterId(tag_comment_task_id=None):
    # item = mydb['cluster'].find_one({"tag_comment_task_id": ObjectId(doc_id)})
    item = mongo_client.db[mongo_conf.COMMENT_CLOUD].find_one({"tag_comment_task_id": tag_comment_task_id})
    item.pop("_id")
    print(item)
    return item


# 以task_id 获取 聚类 类别
def getTypeByClusterId(tag_comment_task_id=None):
    item = mongo_client.db[mongo_conf.COMMENT_CLUSTER].find_one({"tag_comment_task_id": tag_comment_task_id})
    item.pop("_id")
    result = []
    for i in item['data']:
        key_count = {'key': item['data'][i]['key'],
                     'doc_count': len(item['data'][i]['id'])}
        result.append(key_count)
    return result


# 以task_id和类别 获取 某一类聚类内容
def getContentByClusterId(tag_comment_task_id=None, content_type=None):
    item = mongo_client.db[mongo_conf.COMMENT_CLUSTER].find_one({"tag_comment_task_id": tag_comment_task_id})
    item.pop("_id")
    result = []
    for i in item['data']:
        if item['data'][i]['key'] == content_type:
            result = item['data'][i]['content']
    result_sort = []

    for content in result:
        content_sort = {"text": content, "score": len(set(content)) / 8}
        for key in content_type.split(" "):
            if key in content:
                content_sort["score"] += 1
        result_sort.append(content_sort)
    result_sort.sort(key=lambda i: i['score'], reverse=True)
    return result_sort[0:10]


# 以task_id和类别 获取 某一类聚类内容
def getPostById(tag_comment_task_id=None):
    item = mongo_client.db[mongo_conf.COMMENT_TASK].find_one({"tag_comment_task_id": tag_comment_task_id})
    result = []
    result.append(item["detail"])
    return result


# 统计关键节点
def statisticsRepost(item, total):
    children_list = [i for i in item["children"].values()]
    total[item['user_name'].strip()] = len(children_list)
    for i in children_list:
        total[item['user_name'].strip()] = total[item['user_name'].strip()] + statisticsRepost(i, total)
    return total[item['user_name'].strip()]


# 获取获取关键节点
def getKeyNode(tag_comment_task_id):
    item = mongo_client.db[mongo_conf.COMMENT_NODE].find_one({"tag_comment_task_id": tag_comment_task_id})
    return item['data']


# 转换tree数据结构-->leader rank 数据结构
def editJson4Graph(item, nodes, edges):
    nodes.add(item['user_name'].strip())
    if item['children']:
        edges[item['user_name'].strip()] = {}
        children_list = [i for i in item["children"].values()]

        for i in children_list:
            editJson4Graph(i, nodes, edges)
            i.pop("children")
            edges[item['user_name'].strip()][i["user_name"].strip()] = i


# leader rank计算
def node(tag_comment_task_id):
    try:
        nodes = set()
        edges = {}
        re_edges = {}
        data = mongo_client.db[mongo_conf.COMMENT_TREE].find_one({'tag_comment_task_id': tag_comment_task_id})
        if data:
            total = {}
            statisticsRepost(data['data'], total)

            editJson4Graph(data['data'], nodes, edges)
            # 去除G节点和根节点
            result_sorted = startRank(edges, re_edges, list(nodes))[2:]
            result_list = []
            for item in result_sorted:
                try:
                    if total[item[0]] != 0:
                        result = {"name": item[0], "count": total[item[0]], "score": item[1]}
                        result_list.append(result)
                except:
                    # todo
                    pass
            mongo_client.db[mongo_conf.COMMENT_NODE].update_one({"tag_comment_task_id": tag_comment_task_id},
                                                                {"$set": {"data": result_list}})
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # mydb['tendency'].insert_one(spreadTendency("1621162456K7okwxcKa"))
    # refresh_task()
    # print(getTaskList())
    # print(node("1622465660KhQes4VMs"))
    run_by_task_id_part('1635758101KDOBs1AO2', '617fb015de0c993aa08e78f0')
