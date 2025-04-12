import json
from datetime import datetime
from datetime import timedelta
from typing import Dict

import requests
from bson.json_util import dumps
from cnsenti import Sentiment
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from celery_task.config import mongo_conf
from celery_task.rumor.RumorSearch import search_and_save_rumors, crawl_and_save_rumor_details
from celery_task.utils.my_cloud import MyCloud
from config import weibo_conf
from dependencise import get_mongo_db
from models.dto.restful_model import RESTfulModel
from renmin_crawler.main import fetch_renmin_data  # 导入人民网爬虫
from rumor_detect.predict import Predictor
from tieba_crawler.main import fetch_posts
from wechat_crawler.main import search_wechat_articles

rumor_router = APIRouter(tags=['谣言分析api'])


@rumor_router.post('/rumor_search')
async def rumor_search(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    print("rumor")
    try:
        # 获取 rumors 集合的第一条记录
        first_rumor = await mongo_db['rumors'].find_one(projection={"_id": 0}, sort=[("date", -1)])
        if first_rumor:
            # 字段名为 'date'，并且其格式为 YYYY-MM-DD
            rumor_date_str = first_rumor.get('date')
            if rumor_date_str:
                rumor_date = datetime.strptime(rumor_date_str, '%Y-%m-%d')
                yesterday = datetime.now() - timedelta(days=1)
                if rumor_date.date() == yesterday.date():
                    # 如果第一条记录的日期是昨日，则不调用 search_and_save_rumors 函数
                    cursor = mongo_db['rumors'].find(projection={"_id": 0})
                    rumors_data = [doc async for doc in cursor]
                    return {"message": "谣言搜索并存储成功", "data": rumors_data}

        # 如果第一条记录的日期不是昨日，或者没有记录，则调用 search_and_save_rumors 函数
        await search_and_save_rumors(mongo_db)
        # 查询所有保存到 rumors 集合的数据，排除 _id 字段
        cursor = mongo_db['rumors'].find(projection={"_id": 0})
        rumors_data = [doc async for doc in cursor]
        return {"message": "谣言搜索并存储成功", "data": rumors_data}
    except Exception as e:
        return {"message": f"出现错误: {str(e)}"}


@rumor_router.post('/rumor_detail')
async def rumor_detail(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取 rumor_detail 集合的第一条记录
        first_detail = await mongo_db['rumor_detail'].find_one(projection={"_id": 0}, sort=[("date", -1)])
        if first_detail:
            # 日期字段名为 'date'，并且其格式为 YYYY-MM-DD
            detail_date_str = first_detail.get('date')
            if detail_date_str:
                detail_date = datetime.strptime(detail_date_str, '%Y-%m-%d')
                yesterday = datetime.now() - timedelta(days=1)
                if detail_date.date() == yesterday.date():
                    # 如果第一条记录的日期是昨日，则不调用 crawl_and_save_rumor_details 函数
                    cursor = mongo_db['rumor_detail'].find(projection={"_id": 0})
                    details_data = await cursor.to_list(length=None)
                    return {"message": "谣言详情爬取并保存成功", "data": details_data}

        # 如果第一条记录的日期不是昨日，或者没有记录，则调用 crawl_and_save_rumor_details 函数
        await crawl_and_save_rumor_details(mongo_db)
        # 查询所有保存到 rumor_detail 集合的数据，排除 _id 字段
        cursor = mongo_db['rumor_detail'].find(projection={"_id": 0})
        details_data = await cursor.to_list(length=None)
        return {"message": "谣言详情爬取并保存成功", "data": details_data}
    except Exception as e:
        return {"message": f"出现错误: {str(e)}"}


@rumor_router.get('/rumor_word', response_model=RESTfulModel)
async def rumor_details_word_cloud(db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取 rumor_detail 集合
        detail_collection = db['rumor_detail']

        # 查询所有文档
        cursor = detail_collection.find()
        all_documents = [doc async for doc in cursor]

        # 合并所有谣言和真相内容到一个列表
        content = []
        for doc in all_documents:
            rumor = doc.get('rumor', "")
            truth = doc.get('truth', "")
            if rumor:
                content.append(rumor)
            if truth:
                content.append(truth)

        # 定义要去除的词语列表
        words_to_remove = ["谣言", "辟谣", "近日", "来源", "发生", "核实", "信息", "目前", "发布", "出现", "引发",
                           "公众", "表示", "网传", "网民", "内容", "相关"]

        # 对内容列表中的每个字符串进行处理，去除指定词语
        filtered_content = []
        for text in content:
            for word in words_to_remove:
                text = text.replace(word, "")
            filtered_content.append(text)

        # 生成词云，使用过滤后的内容
        cloud = MyCloud(filtered_content)
        wordcloud_data = cloud.GetWordCloud()

        # 返回成功的数据
        return RESTfulModel(code=0, message="成功", data={"wordcloud_data": wordcloud_data})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data={})


# 初始化预测器
predictor = Predictor('./rumor_detect/best_model.pkl')


@rumor_router.get('/rumor_detect')
async def rumor_detect(text: str, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 调用预测器进行判断
        is_rumor = predictor.predict(text)
        result = 1 if is_rumor else 0
        # 返回成功的数据
        return RESTfulModel(code=0, message="成功", data={"is_rumor": result})
    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data={})


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


@rumor_router.get('/rumorAnalyse', response_model=RESTfulModel,
                  description='根据前端传来的key进行多平台搜索谣言', summary='搜索多个平台有关谣言的内容')
async def multi_platform_search(key: str, cursor: int = 1, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 先检查数据库 rumor_ana 中是否存在该 key 的内容
        print(key)
        query = {"rumor_ana": key}
        existing_data = await mongo_db[mongo_conf.RUMOR_ANA].find_one(query)

        if existing_data:
            # 若存在，直接返回数据
            existing_data.pop("_id", None)  # 移除 _id 字段
            return RESTfulModel(code=0, data=json.loads(dumps(existing_data)))

        # 若不存在，进行搜索
        tag = key

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
            "key": tag,
            "weibo": weibo_dict,
            "renmin": renmin_data,
            "tieba": tieba_data,
            "wechat": wechat_articles
        }

        # 存入数据库
        update = {"$set": combined_data}
        await mongo_db[mongo_conf.RUMOR_ANA].update_one(query, update, upsert=True)

        return RESTfulModel(code=0, data=json.loads(dumps(combined_data)))

    except Exception as e:
        print("Error occurred:", e)
        return RESTfulModel(code=500, message="服务器错误，请稍后再试。")


@rumor_router.get('/rumorPost', response_model=RESTfulModel,
                  description='根据前端传来的key进行谣言发布统计', summary='统计多个平台有关谣言的发布时间')
async def post(key: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 构建查询条件
        query = {"rumor_ana": key}
        # 从数据库中查找符合条件的文档
        result = await mongo_db[mongo_conf.RUMOR_ANA].find_one(query)

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
        await mongo_db[mongo_conf.RUMOR_ANA].update_one(
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


@rumor_router.get('/rumorTruth', response_model=RESTfulModel,
                  description='根据前端传来的 key 返回真相', summary='根据前端传来的 key 返回真相')
async def truth(key: str, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    collection = mongo_db["rumor_detail"]
    result = await collection.find_one({"rumor": key})
    if result:
        ans = result["truth"]
        return RESTfulModel(code=200, data={"truth": ans})
    return RESTfulModel(code=404, message="未找到数据")
