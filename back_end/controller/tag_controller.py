"""
:话题初始页及查询页的api

"""
import json
from datetime import datetime

import pytz
import requests
from bson import ObjectId
from bson.json_util import dumps
from cnsenti import Sentiment
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from celery_task.config import mongo_conf
from celery_task.tag_task.task import init_task, init_wx_task, init_rm_task, init_tb_task
from celery_task.utils.my_cloud import MyCloud
from celery_task.worker import start_task, topic_task_schedule
from config import weibo_conf
from dependencise import get_mongo_db
from exceptions import NotExistException
from hot_realtime.baidu_hot import fetch_baidu_hot
from hot_realtime.tieba_hot import fetch_tieba_hot
from hot_realtime.weibo_hot import fetch_weibo_hot
from models.dto.restful_model import RESTfulModel
from renmin_crawler.main import fetch_renmin_data  # 导入人民网爬虫
from service.tag_hot_extract import update_hot_data
from service.tag_index_service import get_tag_task_list, get_tag_hot_blog, delete_task_by_id, get_word_cloud, \
    get_relation_graph, get_user_mark, delete_task_by_id_wx, get_tag_task_list_wx, get_word_cloud_wx, get_post_time_wx, \
    get_mood_wx, get_user_wx, get_tag_task_list_rm, delete_task_by_id_rm, get_word_cloud_rm, get_mood_rm, \
    get_post_time_rm, get_origin_rm, get_tag_task_list_tb, delete_task_by_id_tb, get_word_cloud_tb, get_mood_tb, \
    get_post_time_tb, get_tiezi_tb, topic_get_user_mark, topic_get_relation_graph
from tieba_crawler.main import fetch_posts
from wechat_crawler.main import search_wechat_articles

tag_router = APIRouter(tags=['话题总览页api'])


def convert_objectid_to_str(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                obj[key] = str(value)  # 将ObjectId转换为字符串
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
            elif isinstance(value, list):
                for item in value:
                    convert_objectid_to_str(item)
    elif isinstance(obj, list):
        for item in obj:
            convert_objectid_to_str(item)


# 使用情感分析函数
def analyze_sentiment(test_text: str) -> float:
    """
    使用 cnsenti 对文本进行情感分析。
    返回值为情感得分（0~1），0 消极， 1 积极， 0.5 中立
    """
    senti = Sentiment()
    if not test_text:
        return 0.5  # 空文本返回中性情感
    res = senti.sentiment_count(test_text)
    if res["pos"] == res["neg"]:
        return 0.5
    elif res["pos"] > res["neg"]:
        return 1
    else:
        return 0


@tag_router.get('/multi_search', response_model=RESTfulModel,
                description='多平台搜索', summary='搜索多个平台的相关内容')
async def multi_platform_search(tag: str, cursor: int = 1, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 先检查数据库 SEARCH_RES 中是否存在该 key 的内容
        print(tag)
        query = {"topic": tag}
        existing_data = await mongo_db[mongo_conf.SEARCH_RES].find_one(query)

        if existing_data:
            # 若存在，直接返回数据
            existing_data.pop("_id", None)  # 移除 _id 字段
            return RESTfulModel(code=0, data=json.loads(dumps(existing_data)))

        # 若不存在，进行搜索

        # 获取微信数据
        print("微信：")
        wechat_articles = search_wechat_articles(tag, cursor)

        # 获取微博数据
        print("微博：")
        weibo_url = f"{weibo_conf.BASEPATH}/weibo_curl/api/search_tweets?keyword={tag}&cursor={cursor}&is_hot=1"
        try:
            weibo_response = requests.get(weibo_url)
            weibo_response.raise_for_status()
            weibo_dict = weibo_response.json().get('data')
        except requests.RequestException as e:
            print(f"微博请求出错: {e}")
            weibo_dict = None

        # 获取人民网数据
        print("人民：")
        try:
            renmin_data = fetch_renmin_data(tag, cursor)
        except Exception as e:
            print(f"人民网数据获取出错: {e}")
            renmin_data = []

        # 获取贴吧数据
        print("贴吧：")
        try:
            tieba_data = fetch_posts(tag, cursor, [])
        except Exception as e:
            print(f"贴吧数据获取出错: {e}")
            tieba_data = []

        # 对每个平台的数据进行情感分析
        if weibo_dict and weibo_dict.get('result'):
            for post in weibo_dict['result']:
                content = post.get('text', '')
                post['sentiment'] = analyze_sentiment(content)

        if renmin_data:
            for post in renmin_data:
                content = post.get('title', '')
                post['sentiment'] = analyze_sentiment(content)

        if tieba_data:
            for post in tieba_data:
                content = post.get('content', '')
                post['sentiment'] = analyze_sentiment(content)

        if wechat_articles:
            for post in wechat_articles:
                content = post.get('title', '')
                post['sentiment'] = analyze_sentiment(content)

        # 合并数据
        combined_data = {
            "topic": tag,
            "weibo": weibo_dict,
            "renmin": renmin_data,
            "tieba": tieba_data,
            "wechat": wechat_articles
        }

        # 存入数据库
        update = {"$set": combined_data}
        await mongo_db[mongo_conf.SEARCH_RES].update_one(query, update, upsert=True)

        return RESTfulModel(code=0, data=json.loads(dumps(combined_data)))

    except Exception as e:
        print("Error occurred:", e)
        return RESTfulModel(code=500, message="服务器错误，请稍后再试。")


@tag_router.get('/history_search', response_model=RESTfulModel,
                description='历史搜索', summary='历史的相关内容')
async def history_search(tag: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        collection = mongo_db[mongo_conf.SEARCH_RES]
        result = await collection.find_one({"topic": tag})
        if result:
            # 移除 MongoDB 自动生成的 _id 字段，因为它不能直接被序列化
            del result['_id']
            return {"code": "200", "data": result}
        else:
            return {"message": "未找到相关历史记录", "data": {}}

    except PyMongoError as e:
        print(f"数据库错误: {e}")
        return {"message": "数据库错误", "error": str(e)}
    except Exception as e:
        print(f"未知错误: {e}")
        return {"message": "未知错误", "error": str(e)}


@tag_router.get('/history_topic', response_model=RESTfulModel,
                description='历史搜索history_topic', summary='历史的相关内容history_topic')
async def history_topic(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取 search_history 集合
        collection = mongo_db["search_history"]
        # 查询所有文档
        cursor = collection.find()
        # 将查询结果转换为列表
        documents = await cursor.to_list(length=None)
        # 提取 topic 字段
        topics = [doc.get("topic") for doc in documents if doc.get("topic")]
        # 构造响应数据
        response_data = {
            "code": "200",
            "data": {
                "topic": topics
            }
        }
        return response_data
    except Exception as e:
        # 处理异常
        return {"message": "查询失败", "error": str(e)}


from typing import Dict


@tag_router.post('/save_history_search', response_model=Dict,
                 description='保存历史搜索', summary='保存历史搜索记录')
async def save_history_search(data: Dict, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        collection = mongo_db["search_history"]
        tag = data.get("tag")
        if tag:
            # 插入或更新历史搜索记录
            await collection.update_one({"topic": tag}, {"$set": {"topic": tag}}, upsert=True)
            return {"message": "保存成功"}
        else:
            return {"message": "缺少关键词"}
    except PyMongoError as e:
        print(f"数据库错误: {e}")
        return {"message": "数据库错误", "error": str(e)}
    except Exception as e:
        print(f"未知错误: {e}")
        return {"message": "未知错误", "error": str(e)}


@tag_router.get('/history_del', response_model=RESTfulModel,
                description='删除历史搜索', summary='删除历史的相关内容')
async def del_history_search(tag: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)) -> Dict:
    try:
        # 删除 search_history 集合中指定 topic 的相关内容
        search_history_collection = mongo_db[mongo_conf.SEARCH_HISTORY]
        search_history_result = await search_history_collection.delete_one({"topic": tag})

        # 删除 search_res 集合中指定 topic 的相关内容
        search_res_collection = mongo_db[mongo_conf.SEARCH_RES]
        search_res_result = await search_res_collection.delete_one({"topic": tag})

        topic_content_collection = mongo_db[mongo_conf.TOPIC_CONTENT]
        topic_content_result = await topic_content_collection.delete_one({"topic": tag})

        topic_user_collection = mongo_db[mongo_conf.TOPIC_USER]
        topic_user_result = await topic_user_collection.delete_one({"topic": tag})

        topic_character_collection = mongo_db[mongo_conf.TOPIC_CHARACTER]
        topic_character_result = await topic_character_collection.delete_one({"topic": tag})

        topic_relation_collection = mongo_db[mongo_conf.TOPIC_RELATION]
        topic_relation_result = await topic_relation_collection.delete_one({"topic": tag})

        # 检查是否至少有一个文档被删除
        if search_history_result.deleted_count > 0 and search_res_result.deleted_count > 0 and topic_content_result.deleted_count > 0 and topic_user_result.deleted_count > 0 and topic_character_result.deleted_count > 0 and topic_relation_result.deleted_count > 0:
            return {"code": "200", "data": {}}
        else:
            return {"code": "404", "data": {}}

    except PyMongoError as e:
        print(f"数据库错误: {e}")
        return {"message": "数据库错误", "error": str(e)}
    except Exception as e:
        print(f"未知错误: {e}")
        return {"message": "未知错误", "error": str(e)}


import heapq
from collections import defaultdict


# 后端接口函数
@tag_router.get('/topic_ci', response_model=RESTfulModel,
                description='对所搜结果进行词频正反面统计', summary='词频正反面统计')
async def topic_ci(tag: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)) -> Dict:
    try:
        query = {"topic": tag}
        existing_data = await mongo_db['search_res'].find_one(query)

        # 检查数据库中是否已经有正反面词语
        if existing_data and 'positive_words' in existing_data and 'negative_words' in existing_data:
            return {
                'code': 0,
                'message': 'success',
                'data': {
                    'positive_words': existing_data['positive_words'],
                    'negative_words': existing_data['negative_words']
                }
            }

        # 提取需要的文本内容
        all_texts = []
        if 'renmin' in existing_data:
            all_texts.extend([item['content'] for item in existing_data['renmin']])
        if 'tieba' in existing_data:
            all_texts.extend([item['content'] for item in existing_data['tieba']])
        if 'wechat' in existing_data:
            all_texts.extend([item['summary'] for item in existing_data['wechat']])
        if 'weibo' in existing_data and 'result' in existing_data['weibo']:
            all_texts.extend([item['text'] for item in existing_data['weibo']['result']])

        # 调用 MyCloud 生成词云数据
        cloud = MyCloud(content=all_texts)
        wordcloud_data = cloud.GetWordCloud()

        # 初始化正面和负面优先队列（小顶堆）
        positive_heap = []
        negative_heap = []

        # 遍历词云数据
        for word_info in wordcloud_data:
            word = word_info['name']
            frequency = word_info['value']
            sentiment_score = analyze_sentiment(word)

            if sentiment_score > 0.5:
                if len(positive_heap) < 15:
                    heapq.heappush(positive_heap, (frequency, word))
                elif frequency > positive_heap[0][0]:
                    heapq.heappop(positive_heap)
                    heapq.heappush(positive_heap, (frequency, word))
            elif sentiment_score < 0.5:
                if len(negative_heap) < 15:
                    heapq.heappush(negative_heap, (frequency, word))
                elif frequency > negative_heap[0][0]:
                    heapq.heappop(negative_heap)
                    heapq.heappush(negative_heap, (frequency, word))

        # 对优先队列进行排序并格式化结果
        top_positive_words = sorted(positive_heap, reverse=True)
        top_negative_words = sorted(negative_heap, reverse=True)

        formatted_positive = [{"name": word, "value": freq} for freq, word in top_positive_words]
        formatted_negative = [{"name": word, "value": freq} for freq, word in top_negative_words]

        # 将正反面词语存入数据库
        await mongo_db['search_res'].update_one(
            query,
            {"$set": {"positive_words": formatted_positive, "negative_words": formatted_negative}},
            upsert=True
        )

        return {
            'code': 0,
            'message': 'success',
            'data': {
                'positive_words': formatted_positive,
                'negative_words': formatted_negative
            }
        }
    except Exception as e:
        return {
            'code': 1,
            'message': str(e),
            'data': {}
        }


@tag_router.get('/topicPost', response_model=RESTfulModel,
                description='根据前端传来的key进行话题发布统计', summary='统计多个平台有关话题的发布时间')
async def post(key: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 构建查询条件
        query = {"topic": key}
        # 从数据库中查找符合条件的文档
        result = await mongo_db[mongo_conf.SEARCH_RES].find_one(query)

        if not result:
            # 如果未找到相关文档，返回空统计结果
            return RESTfulModel(code=0, data={
                "renmin_date_count": {},
                "tieba_date_count": {},
                "wechat_date_count": {},
                "weibo_date_count": {}
            })

            # 检查数据库中是否已经有发布时间和数量的统计信息
        if "renmin_date_count" in result and "tieba_date_count" in result and \
                "wechat_date_count" in result and "weibo_date_count" in result:
            return RESTfulModel(code=0, data={
                "renmin_date_count": result["renmin_date_count"],
                "tieba_date_count": result["tieba_date_count"],
                "wechat_date_count": result["wechat_date_count"],
                "weibo_date_count": result["weibo_date_count"]
            })

        # 初始化各平台日期统计字典
        renmin_date_count: Dict[str, int] = {}
        tieba_date_count: Dict[str, int] = {}
        wechat_date_count: Dict[str, int] = {}
        weibo_date_count: Dict[str, int] = {}

        # 统计人民网数据的发布日期
        for item in result.get("renmin", []):
            display_time = item.get("displayTime", "").split(" ")[0]  # 提取日期部分
            if display_time:
                renmin_date_count[display_time] = renmin_date_count.get(display_time, 0) + 1

        # 统计贴吧数据的发布日期
        for item in result.get("tieba", []):
            time = item.get("time", "").split(" ")[0]  # 提取日期部分
            if time:
                tieba_date_count[time] = tieba_date_count.get(time, 0) + 1

        # 统计微信数据的发布日期
        for item in result.get("wechat", []):
            time = item.get("time", "").split(" ")[0]  # 提取日期部分
            if time:
                wechat_date_count[time] = wechat_date_count.get(time, 0) + 1

        # 统计微博数据的发布日期
        for item in result.get("weibo", {}).get("result", []):
            created_at = item.get("created_at", "").split(" ")[0]  # 提取日期部分
            if created_at:
                weibo_date_count[created_at] = weibo_date_count.get(created_at, 0) + 1

        # 对各平台日期进行排序
        sorted_renmin_date_count = dict(sorted(renmin_date_count.items()))
        sorted_tieba_date_count = dict(sorted(tieba_date_count.items()))
        sorted_wechat_date_count = dict(sorted(wechat_date_count.items()))
        sorted_weibo_date_count = dict(sorted(weibo_date_count.items()))

        # 将统计结果存入数据库
        await mongo_db[mongo_conf.SEARCH_RES].update_one(
            query,
            {
                "$set": {
                    "renmin_date_count": sorted_renmin_date_count,
                    "tieba_date_count": sorted_tieba_date_count,
                    "wechat_date_count": sorted_wechat_date_count,
                    "weibo_date_count": sorted_weibo_date_count
                }
            },
            upsert=True
        )

        return RESTfulModel(code=0, data={
            "renmin_date_count": sorted_renmin_date_count,
            "tieba_date_count": sorted_tieba_date_count,
            "wechat_date_count": sorted_wechat_date_count,
            "weibo_date_count": sorted_weibo_date_count
        })

    except Exception as e:
        print("Error occurred:", e)
        return RESTfulModel(code=500, message="服务器错误，请稍后再试。")


@tag_router.get('/start_topic', response_model=RESTfulModel,
                description='开始话题任务', summary='开始话题任务',
                status_code=status.HTTP_201_CREATED)
async def add_task(topic: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        print(topic)
        # 检查 topic_content 集合中是否存在指定的 topic
        collection = mongo_db['topic_content']
        existing_topic = await collection.find_one({"tag": topic})

        if existing_topic:
            # 如果存在，返回成功提示
            print("话题已经存在")
            return RESTfulModel(code=0, message=f"话题 {topic} 的数据已存在，无需再次执行任务。", data={})
        else:
            # 如果不存在，调用 topic_task_schedule 函数
            init_result = topic_task_schedule.delay(topic, tag=topic)
            return RESTfulModel(code=0, data={"task_id": init_result.id})
    except Exception as e:
        return RESTfulModel(code=1, message=str(e), data={})


@tag_router.get('/topic_user_mark', response_model=RESTfulModel,
                description='话题用户标签', summary='获取用户标签数据')
async def user_mark(topic: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    user_mark_result = await topic_get_user_mark(topic=topic, mongo_db=mongo_db)
    return RESTfulModel(code=0, data=user_mark_result)


@tag_router.get('/topic_relation_graph', response_model=RESTfulModel,
                description='话题网络图的数据', summary='获取网络图数据')
async def relation_graph(topic: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    relation_graph_result = await topic_get_relation_graph(topic, mongo_db)
    return RESTfulModel(code=0, data=relation_graph_result)


# 新建一个API路由，用于获取热搜事件
@tag_router.get('/weibo_hot', response_model=RESTfulModel,
                description='获取热搜事件', summary='返回热搜数据')
async def get_weibo_hot():
    try:
        # 调用 weibo_hot.py 中的函数获取热搜数据
        weibo_hot = fetch_weibo_hot()
        if weibo_hot is None:
            return RESTfulModel(code=500, message="获取热搜数据失败", data=[])

        return RESTfulModel(code=0, message="成功", data=weibo_hot)

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@tag_router.get('/baidu_hot', response_model=RESTfulModel,
                description='获取百度热搜事件', summary='返回热搜数据')
async def get_baidu_hot():
    try:
        baidu_hot = fetch_baidu_hot()
        if baidu_hot is None:
            return RESTfulModel(code=500, message="获取热搜数据失败", data=[])

        return RESTfulModel(code=0, message="成功", data=baidu_hot)

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@tag_router.get('/tieba_hot', response_model=RESTfulModel,
                description='获取tieba热搜事件', summary='返回热搜数据')
async def get_baidu_hot():
    try:
        tieba_hot = fetch_tieba_hot()
        if tieba_hot is None:
            return RESTfulModel(code=500, message="获取热搜数据失败", data=[])

        return RESTfulModel(code=0, message="成功", data=tieba_hot)

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@tag_router.get('/hot_wordcloud', response_model=RESTfulModel, description='获取3个APP的热搜词云数据',
                summary='生成基于APP的词云')
async def get_apps_hot():
    try:
        # 获取各个APP的热搜数据
        app1_hot = fetch_weibo_hot()
        app2_hot = fetch_tieba_hot()
        app3_hot = fetch_baidu_hot()

        # 合并所有APP的热搜数据
        all_hot_words = []
        for app_data in [app1_hot, app2_hot, app3_hot]:
            all_hot_words.extend([entry['title'] for entry in app_data])

        # 调用 MyCloud 生成词云数据
        cloud = MyCloud(content=all_hot_words)
        wordcloud_data = cloud.GetWordCloud()

        # 返回成功的数据
        return RESTfulModel(code=0, message="成功", data={"wordcloud_data": wordcloud_data})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data={})


# 微博
@tag_router.get('/tag_list',
                response_model=RESTfulModel,
                description='获取当前的tag_list',
                summary='获取话题列表'
                )
async def tag_list_get(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    tag_list = await get_tag_task_list(mongo_db)
    return RESTfulModel(code=0, data=tag_list)


@tag_router.get('/delete_task', response_model=RESTfulModel,
                description='删除任务',
                summary='删除指定任务')
async def delete_task(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        task = await delete_task_by_id(tag_task_id, mongo_db)
    except NotExistException as e:
        return RESTfulModel(code=-1, data=e.msg)
    return RESTfulModel(code=0, data=task)


@tag_router.get('/blog_rank',
                response_model=RESTfulModel,
                description='获取选中话题博文热度排名',
                summary='获取Tag中热度前十的博文')
async def blog_rank(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        blog_result = await get_tag_hot_blog(tag_task_id, mongo_db)
    except NotExistException as exc:
        raise exc
    return RESTfulModel(code=0, data=blog_result)


@tag_router.get('/word_cloud', response_model=RESTfulModel,
                description='词云的数据', summary='获取词云')
async def word_cloud(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    word_cloud_result = await get_word_cloud(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=word_cloud_result)


@tag_router.get('/relation_graph', response_model=RESTfulModel,
                description='网络图的数据', summary='获取网络图数据')
async def relation_graph(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    relation_graph_result = await get_relation_graph(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=relation_graph_result)


@tag_router.get('/search', response_model=RESTfulModel,
                description='搜索', summary='搜索某一话题')
def search(tag: str, cursor: int):
    url = weibo_conf.BASEPATH + '/weibo_curl/api/search_tweets?keyword={keyword}&cursor={cursor}&is_hot=1' \
        .format(keyword=tag, cursor=cursor)
    response = requests.get(url)
    weibo_dict = json.loads(response.text).get('data')
    return RESTfulModel(code=0, data=weibo_dict)


@tag_router.get('/add_task', response_model=RESTfulModel,
                description='添加任务', summary='添加该话题到任务队列中',
                status_code=status.HTTP_201_CREATED)
async def add_task(tag: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    init_result = await init_task(tag, mongo_db)
    if init_result:
        init_result.pop('_id')
    return RESTfulModel(code=0, data=init_result)


@tag_router.get('/tag_list_wx',
                response_model=RESTfulModel,
                description='获取当前的tag_list',
                summary='获取话题列表'
                )
async def tag_list_get_wx(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    tag_list = await get_tag_task_list_wx(mongo_db)
    return RESTfulModel(code=0, data=tag_list)


@tag_router.get('/search_wx', response_model=RESTfulModel,
                description='搜索微信', summary='搜索微信某一话题')
async def search_wx(tag: str, cursor: int):
    print("微信：")
    wechat_articles = search_wechat_articles(tag, cursor)
    return RESTfulModel(code=0, data=wechat_articles)


@tag_router.get('/add_task_wx', response_model=RESTfulModel,
                description='添加微信任务', summary='添加该话题到任务队列中',
                status_code=status.HTTP_201_CREATED)
async def add_wx_task(tag: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    init_result = await init_wx_task(tag, mongo_db)
    if init_result:
        init_result.pop('_id')
    print("add_over")
    return RESTfulModel(code=0, data=init_result)


@tag_router.get('/word_cloud_wx', response_model=RESTfulModel,
                description='微信词云的数据', summary='微信获取词云')
async def word_cloudwx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    word_cloud_result = await get_word_cloud_wx(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=word_cloud_result)


@tag_router.get('/delete_task_wx', response_model=RESTfulModel,
                description='删除wx任务',
                summary='删除指定wx任务')
async def delete_task_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        task = await delete_task_by_id_wx(tag_task_id, mongo_db)
    except NotExistException as e:
        return RESTfulModel(code=-1, data=e.msg)
    return RESTfulModel(code=0, data=task)


@tag_router.get('/post_time_statistics_wx', response_model=RESTfulModel,
                description='获取该话题wx发博时间统计数据',
                summary='话题wx发博时间统计')
async def post_time_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    post_time_result = await get_post_time_wx(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=post_time_result)


@tag_router.get('/mood_wx', response_model=RESTfulModel,
                description='获取该话题情感分析数据',
                summary='话题wx情感统计,情感趋势')
async def mood_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    mood_result = await get_mood_wx(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=mood_result)


@tag_router.get('/user_wx', response_model=RESTfulModel,
                description='获取该话题公众号数据',
                summary='话题公众号统计')
async def user_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    user_result = await get_user_wx(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=user_result)


# 人民网
@tag_router.get('/search_rm', response_model=RESTfulModel,
                description='搜索人民网', summary='搜索人民网某一话题')
async def search_rm(tag: str, cursor: int):
    print("人民网：")
    rmw_articles = fetch_renmin_data(tag, cursor)
    return RESTfulModel(code=0, data=rmw_articles)


@tag_router.get('/add_task_rm', response_model=RESTfulModel,
                description='添加人民网任务', summary='添加该话题到任务队列中',
                status_code=status.HTTP_201_CREATED)
async def add_rm_task(tag: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    init_result = await init_rm_task(tag, mongo_db)
    if init_result:
        init_result.pop('_id')
    print("add_over")
    return RESTfulModel(code=0, data=init_result)


@tag_router.get('/tag_list_rm',
                response_model=RESTfulModel,
                description='获取当前的tag_list',
                summary='获取话题列表'
                )
async def tag_list_get_rm(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    tag_list = await get_tag_task_list_rm(mongo_db)
    return RESTfulModel(code=0, data=tag_list)


@tag_router.get('/delete_task_rm', response_model=RESTfulModel,
                description='删除rm任务',
                summary='删除指定rm任务')
async def delete_task_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        task = await delete_task_by_id_rm(tag_task_id, mongo_db)
    except NotExistException as e:
        return RESTfulModel(code=-1, data=e.msg)
    return RESTfulModel(code=0, data=task)


@tag_router.get('/word_cloud_rm', response_model=RESTfulModel,
                description='人民网词云的数据', summary='人民网获取词云')
async def word_cloudrm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    word_cloud_result = await get_word_cloud_rm(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=word_cloud_result)


@tag_router.get('/mood_rm', response_model=RESTfulModel,
                description='获取该话题情感分析数据',
                summary='话题rm情感统计,情感趋势')
async def mood_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    mood_result = await get_mood_rm(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=mood_result)


@tag_router.get('/post_time_statistics_rm', response_model=RESTfulModel,
                description='获取该话题rm发布时间统计数据',
                summary='话题人民网发布时间统计')
async def post_time_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    post_time_result = await get_post_time_rm(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=post_time_result)


@tag_router.get('/origin_rm', response_model=RESTfulModel,
                description='获取该话题来源数据',
                summary='话题来源统计')
async def origin_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    origin_result = await get_origin_rm(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=origin_result)


# 贴吧
@tag_router.get('/search_tb', response_model=RESTfulModel,
                description='搜索贴吧', summary='搜索贴吧某一话题')
async def search_tb(tag: str, cursor: int):
    print("贴吧：")
    tieba_data = []
    tieba_data = fetch_posts(tag, cursor, tieba_data)
    return RESTfulModel(code=0, data=tieba_data)


@tag_router.get('/add_task_tb', response_model=RESTfulModel,
                description='添加贴吧任务', summary='添加该话题到任务队列中',
                status_code=status.HTTP_201_CREATED)
async def add_tb_task(tag: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    init_result = await init_tb_task(tag, mongo_db)
    if init_result:
        init_result.pop('_id')
    print("add_over")
    return RESTfulModel(code=0, data=init_result)


@tag_router.get('/tag_list_tb',
                response_model=RESTfulModel,
                description='获取当前的tag_list',
                summary='获取话题列表'
                )
async def tag_list_get_tb(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    tag_list = await get_tag_task_list_tb(mongo_db)
    return RESTfulModel(code=0, data=tag_list)


@tag_router.get('/delete_task_tb', response_model=RESTfulModel,
                description='删除tb任务',
                summary='删除指定tb任务')
async def delete_task_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        task = await delete_task_by_id_tb(tag_task_id, mongo_db)
    except NotExistException as e:
        return RESTfulModel(code=-1, data=e.msg)
    return RESTfulModel(code=0, data=task)


@tag_router.get('/word_cloud_tb', response_model=RESTfulModel,
                description='tb词云的数据', summary='tb获取词云')
async def word_cloudtb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    word_cloud_result = await get_word_cloud_tb(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=word_cloud_result)


@tag_router.get('/mood_tb', response_model=RESTfulModel,
                description='获取该话题情感分析数据',
                summary='话题tb情感统计,情感趋势')
async def mood_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    mood_result = await get_mood_tb(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=mood_result)


@tag_router.get('/post_time_statistics_tb', response_model=RESTfulModel,
                description='获取该话题tb发布时间统计数据',
                summary='话题人民网发布时间统计')
async def post_time_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    post_time_result = await get_post_time_tb(tag_task_id, mongo_db)
    return RESTfulModel(code=0, data=post_time_result)


@tag_router.get('/tb_detail',
                response_model=RESTfulModel,
                description='获取此话题下的前十帖子',
                summary='获取此话题下的前十帖子')
async def blog_rank_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        blog_result = await get_tiezi_tb(tag_task_id, mongo_db)
    except NotExistException as exc:
        raise exc
    return RESTfulModel(code=0, data=blog_result)


@tag_router.get('/user_mark', response_model=RESTfulModel,
                description='用户标签', summary='获取用户标签数据')
async def user_mark(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    user_mark_result = await get_user_mark(tag_task_id=tag_task_id, mongo_db=mongo_db)
    return RESTfulModel(code=0, data=user_mark_result)


@tag_router.get('/get_detail_blog', response_model=RESTfulModel, summary='获取并分析某位用户的所有微博')
async def get_detail_blog(user_id: str, tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    blog = list()
    for i in range(1, 11, 1):
        url = 'http://127.0.0.1:8000/weibo_curl/api/statuses_user_timeline?user_id={user_id}&cursor={i}' \
            .format(user_id=user_id, i=i)
        print(url)
        response = requests.get(url)
        data = json.loads(response.text)
        print(data)
        if data['error_code'] == 0:
            blog.extend(data['data']['result']['weibos'])
            for weibo in data['data']['result']['weibos']:
                start_task(tag_task_id, weibo)
    mongo_db['detail_blog'].insert_many(blog)


# 新增 API 路由
@tag_router.get('/post_time_statistics', response_model=RESTfulModel,
                description='获取该话题发博时间统计数据',
                summary='话题发博时间统计')
async def post_time_statistics(tag_task_id: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    """
    获取话题的发博时间统计数据，包括按小时、天、月的发博数量
    """
    try:
        # 获取微博数据
        data = await get_weibo_data(tag_task_id, mongo_db)

        # 获取统计数据
        time_stats = await get_post_time_statistics(data)

        return RESTfulModel(code=0, data=time_stats)

    except Exception as e:
        return RESTfulModel(code=-1, data=str(e))


async def get_weibo_data(tag_task_id: str, mongo_db: AsyncIOMotorDatabase):
    """
    根据 tag_task_id 从数据库中获取与话题相关的微博数据
    """
    # 查询条件，按 tag_task_id 查询微博数据
    # 查询 blog 表中的文档
    cursor = mongo_db['blog'].find({"tag_task_id": tag_task_id})
    data = await cursor.to_list(length=None)

    # 提取所有的微博数据
    weibo_data = []
    for doc in data:
        # 每个文档中的 'data' 数组包含多条微博
        weibo_data.extend(doc.get('data', []))

    return weibo_data


async def get_post_time_statistics(data: list) -> dict:
    """
    根据微博的创建时间进行统计，返回时间段内的发博数量
    """
    time_stats = defaultdict(lambda: defaultdict(int))

    # 获取当前时间的时区，确保时间统计正确
    tz = pytz.timezone('Asia/Shanghai')

    for entry in data:
        created_at = entry.get('created_at')
        if created_at:
            # 转换为datetime对象
            created_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M')
            created_time = tz.localize(created_time)  # 本地化时间

            # 按小时、天、月等统计
            hour = created_time.strftime('%Y-%m-%d %H:00')
            day = created_time.strftime('%Y-%m-%d')
            month = created_time.strftime('%Y-%m')

            time_stats['hour'][hour] += 1
            time_stats['day'][day] += 1
            time_stats['month'][month] += 1

    # 返回按小时、天、月的发博数量
    return time_stats
