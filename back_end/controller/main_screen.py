import asyncio
import heapq
from datetime import datetime

import requests
from cnsenti import Sentiment
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from bert_class.predict import TextClassifier
from celery_task.config import mongo_conf
from celery_task.utils.my_cloud import MyCloud
from celery_task.worker import main_screen_task_schedule
from config import weibo_conf
from dependencise import get_mongo_db
from hot_realtime.baidu_hot import fetch_baidu_hot
from hot_realtime.tieba_hot import fetch_tieba_hot
from hot_realtime.weibo_hot import fetch_weibo_hot
from models import RESTfulModel
from wechat_crawler.main import search_wechat_articles
from renmin_crawler.main import fetch_renmin_data  # 导入人民网爬虫
from tieba_crawler.main import fetch_posts

main_router = APIRouter(tags=['可视化大屏api'])


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


@main_router.get('/all_hot', response_model=RESTfulModel,
                 description='获取所有热搜事件', summary='返回热搜数据')
async def get_hot(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 获取数据库中最新日期的记录
        latest_record = await mongo_db["HOT"].find_one(sort=[("date", -1)])

        if latest_record and latest_record["date"] == current_date:
            # 如果最新记录的日期是今天，直接返回最新记录的数据
            result_data = {
                "weibo": latest_record.get("weibo", []),
                "tieba": latest_record.get("tieba", []),
                "baidu": latest_record.get("baidu", [])
            }
            return RESTfulModel(code=0, message="成功", data=result_data)
        else:
            # 获取各个APP的热搜数据
            app1_hot = fetch_weibo_hot()
            app2_hot = fetch_tieba_hot()
            app3_hot = fetch_baidu_hot()

            # 准备要插入的数据
            data_to_insert = {
                "date": current_date,
                "weibo": app1_hot,
                "tieba": app2_hot,
                "baidu": app3_hot
            }
            print(data_to_insert)
            # 将数据插入数据库
            await mongo_db["HOT"].insert_one(data_to_insert)

            # 再次获取最新记录（即刚插入的今天的数据）
            latest_record = await mongo_db["HOT"].find_one(sort=[("date", -1)])

            if latest_record:
                result_data = {
                    "weibo": latest_record.get("weibo", []),
                    "tieba": latest_record.get("tieba", []),
                    "baidu": latest_record.get("baidu", [])
                }
                return RESTfulModel(code=0, message="成功", data=result_data)
            else:
                return RESTfulModel(code=0, message="成功，但未找到当天数据", data={})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_hot_word', response_model=RESTfulModel,
                 description='获取所有热搜事件的词云', summary='返回热搜数据词云')
async def get_hot_word(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 检查 HOT_WORD 中是否有当天的数据
        existing_record = await mongo_db["HOT_WORD"].find_one({"date": current_date})

        if existing_record:
            # 如果有当天的数据，直接返回该数据
            wordcloud_data = existing_record["wordcloud_data"]
            return RESTfulModel(code=0, message="成功", data=wordcloud_data)

        # 从数据库 HOT 中获取当天的热搜数据
        today_records = await mongo_db["HOT"].find({"date": current_date}).to_list(length=None)
        if not today_records:
            # 如果 HOT 中没有当天的数据，返回空数据
            return RESTfulModel(code=0, message="成功", data=[])

        # 提取所有热搜的 title 数据
        all_hot_titles = []
        for record in today_records:
            for platform in ['weibo', 'tieba', 'baidu']:
                for item in record.get(platform, []):
                    all_hot_titles.append(item.get('title', ''))

        # 调用 MyCloud 生成词云数据
        cloud = MyCloud(content=all_hot_titles)
        wordcloud_data = cloud.GetWordCloud()

        # 准备要插入到 HOT_WORD 集合的数据
        data_to_insert = {
            "date": current_date,
            "wordcloud_data": wordcloud_data
        }

        # 将词云数据插入到数据库 HOT_WORD 中
        await mongo_db["HOT_WORD"].insert_one(data_to_insert)

        return RESTfulModel(code=0, message="成功", data=wordcloud_data)

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_hot_class', response_model=RESTfulModel,
                 description='获取所有热搜事件的文本分类', summary='返回热搜数据文本分类')
async def get_hot_class(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 检查 HOT_CLASS 中是否有当天的数据
        existing_record = await mongo_db["HOT_CLASS"].find_one({"date": current_date})
        if existing_record:
            # 如果有当天的数据，直接返回分类结果
            return RESTfulModel(code=0, message="成功", data=existing_record["class_count"])

        # 检查 HOT 中是否有当天的数据
        hot_today_record = await mongo_db["HOT"].find_one({"date": current_date})
        if not hot_today_record:
            # 如果 HOT 中没有当天的数据，返回空数据
            return RESTfulModel(code=0, message="成功", data=[])

        # 从数据库 HOT 中获取当天的热搜数据
        today_records = await mongo_db["HOT"].find({"date": current_date}).to_list(length=None)

        # 提取所有热搜的 title 数据
        all_hot_titles = []
        for record in today_records:
            for platform in ['weibo', 'tieba', 'baidu']:
                for item in record.get(platform, []):
                    all_hot_titles.append(item.get('title', ''))

        # 初始化文本分类器
        classifier = TextClassifier()

        # 初始化分类结果计数器
        class_count = {label: 0 for label in classifier.labels}

        # 对每个 title 进行文本分类
        for title in all_hot_titles:
            if title:
                category = classifier.classify_text(title)
                class_count[category] += 1

        # 准备要插入到 HOT_CLASS 集合的数据
        data_to_insert = {
            "date": current_date,
            "class_count": class_count
        }

        # 将分类结果插入到数据库 HOT_CLASS 中
        await mongo_db["HOT_CLASS"].insert_one(data_to_insert)

        return RESTfulModel(code=0, message="成功", data=class_count)

    except PyMongoError as pymongo_error:
        # 捕获 PyMongo 相关的异常
        return RESTfulModel(code=500, message=f"数据库操作发生错误: {str(pymongo_error)}", data=[])
    except Exception as e:
        return RESTfulModel(code=500, message=f"发生其他错误: {str(e)}", data=[])


@main_router.get('/all_hot_mood', response_model=RESTfulModel,
                 description='获取所有热搜事件的情感分析，正反面词频统计', summary='返回热搜数据情感分析，正反面词频统计')
async def get_hot_mood(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 检查 HOT_MOOD 中是否有当天的数据
        existing_record = await mongo_db["HOT_MOOD"].find_one({"date": current_date})
        existing_record1 = await mongo_db["HOT_WORD"].find_one({"date": current_date})
        if not existing_record1:
            return RESTfulModel(code=0, message="成功", data=[])

        if existing_record:
            # 如果有当天的数据，直接返回
            return RESTfulModel(code=0, message="成功", data=existing_record["analysis_result"])

        # 检查 HOT 中是否有当天的数据
        hot_today_record = await mongo_db["HOT"].find_one({"date": current_date})
        if not hot_today_record:
            # 如果 HOT 中没有当天的数据，返回空数据
            return RESTfulModel(code=0, message="成功", data=[])

        # 从数据库 HOT 中获取当天的热搜数据
        today_records = await mongo_db["HOT"].find({"date": current_date}).to_list(length=None)

        # 情感占比统计
        total_count = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for record in today_records:
            for platform in ['weibo', 'tieba', 'baidu']:
                for item in record.get(platform, []):
                    sentiment = item.get('sentiment')
                    if sentiment is not None:
                        total_count += 1
                        if sentiment == 1:
                            positive_count += 1
                        elif sentiment == 0:
                            negative_count += 1
                        elif sentiment == 5:
                            neutral_count += 1

        if total_count > 0:
            positive_ratio = positive_count / total_count
            negative_ratio = negative_count / total_count
            neutral_ratio = neutral_count / total_count
        else:
            positive_ratio = 0
            negative_ratio = 0
            neutral_ratio = 0

        # 从数据库 HOT_WORD 中获取当天的词云数据
        wordcloud_record = await mongo_db["HOT_WORD"].find_one({"date": current_date})
        if wordcloud_record:
            wordcloud_data = wordcloud_record["wordcloud_data"]
        else:
            wordcloud_data = []

        # 初始化正面和负面优先队列（小顶堆）
        positive_heap = []
        negative_heap = []

        # 遍历词云数据
        for word_info in wordcloud_data:
            word = word_info['name']
            frequency = word_info['value']
            sentiment_score = analyze_sentiment(word)

            if sentiment_score > 0.5:
                if len(positive_heap) < 5:
                    heapq.heappush(positive_heap, (frequency, word))
                elif frequency > positive_heap[0][0]:
                    heapq.heappop(positive_heap)
                    heapq.heappush(positive_heap, (frequency, word))
            elif sentiment_score < 0.5:
                if len(negative_heap) < 5:
                    heapq.heappush(negative_heap, (frequency, word))
                elif frequency > negative_heap[0][0]:
                    heapq.heappop(negative_heap)
                    heapq.heappush(negative_heap, (frequency, word))

        # 对优先队列进行排序并格式化结果
        top_positive_words = sorted(positive_heap, reverse=True)
        top_negative_words = sorted(negative_heap, reverse=True)

        formatted_positive = [{"name": word, "value": freq} for freq, word in top_positive_words]
        formatted_negative = [{"name": word, "value": freq} for freq, word in top_negative_words]

        # 准备要插入到 HOT_MOOD 集合的数据
        analysis_result = {
            "sentiment_ratio": {
                "positive": positive_ratio,
                "negative": negative_ratio,
                "neutral": neutral_ratio
            },
            "top_positive_words": formatted_positive,
            "top_negative_words": formatted_negative
        }

        data_to_insert = {
            "date": current_date,
            "analysis_result": analysis_result
        }

        # 将分析结果插入到数据库 HOT_MOOD 中
        await mongo_db["HOT_MOOD"].insert_one(data_to_insert)

        return RESTfulModel(code=0, message="成功", data=analysis_result)

    except PyMongoError as pymongo_error:
        # 捕获 PyMongo 相关的异常
        return RESTfulModel(code=500, message=f"数据库操作发生错误: {str(pymongo_error)}", data=[])
    except Exception as e:
        return RESTfulModel(code=500, message=f"发生其他错误: {str(e)}", data=[])


@main_router.get('/all_multi_search', response_model=RESTfulModel,
                 description='多平台搜索', summary='搜索多个平台的相关内容')
async def multi_platform_search(cursor: int = 1, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 检查 ALL_RES 中是否有当天的数据
        existing_record = await mongo_db["ALL_RES"].find_one({"date": current_date})
        if existing_record:
            # 如果有当天的数据，直接返回
            return RESTfulModel(code=0, message="成功", data=existing_record["search_result"])

        # 检查 HOT 中是否有当天的数据
        hot_today_record = await mongo_db["HOT"].find_one({"date": current_date})
        if not hot_today_record:
            # 如果 HOT 中没有当天的数据，返回空数据
            return RESTfulModel(code=0, message="成功", data=[])

        # 从数据库 HOT 中获取对应日期各平台的前三个 title 作为 tag 列表
        hot_record = await mongo_db["HOT"].find_one({"date": current_date})
        tags = []
        platforms = ['weibo', 'tieba', 'baidu']  # 假设的平台
        for platform in platforms:
            platform_data = hot_record.get(platform, [])
            for item in platform_data[:3]:
                title = item.get('title')
                if title:
                    tags.append(title)

        all_wechat_articles = []
        all_weibo_dict = []
        all_renmin_data = []
        all_tieba_data = []

        # 对每个 tag 进行搜索
        for tag in tags:
            # 获取微信数据
            print(f"微信搜索 {tag}：")
            wechat_articles = search_wechat_articles(tag, cursor)
            all_wechat_articles.extend(wechat_articles)

            # 获取微博数据
            print(f"微博搜索 {tag}：")
            weibo_url = f"{weibo_conf.BASEPATH}/weibo_curl/api/search_tweets?keyword={tag}&cursor={cursor}&is_hot=1"
            try:
                weibo_response = requests.get(weibo_url)
                weibo_response.raise_for_status()
                weibo_dict = weibo_response.json().get('data')
                if weibo_dict and "result" in weibo_dict:
                    all_weibo_dict.extend(weibo_dict["result"])
            except requests.RequestException as e:
                print(f"微博请求出错: {e}")

            # 获取人民网数据
            print(f"人民网搜索 {tag}：")
            try:
                renmin_data = fetch_renmin_data(tag, cursor)
                all_renmin_data.extend(renmin_data)
            except Exception as e:
                print(f"人民网数据获取出错: {e}")

            # 获取贴吧数据
            print(f"贴吧搜索 {tag}：")
            try:
                tieba_data = fetch_posts(tag, cursor, [])
                all_tieba_data.extend(tieba_data)
            except Exception as e:
                print(f"贴吧数据获取出错: {e}")

        # 统计数据来源和数量
        source_count = {
            "wechat": len(all_wechat_articles),
            "weibo": len(all_weibo_dict),
            "renmin": len(all_renmin_data),
            "tieba": len(all_tieba_data)
        }

        # 准备当前日期的数据
        current_data = {
            "date": current_date,
            "source_count": source_count
        }

        # 查找 ALL_POST 集合中的文档
        all_post_record = await mongo_db["ALL_POST"].find_one()

        if all_post_record:
            # 如果文档存在，更新 data 数组
            data_list = all_post_record.get("data", [])
            found = False
            for index, data in enumerate(data_list):
                if data["date"] == current_date:
                    # 如果当天数据已存在，更新 source_count
                    data_list[index]["source_count"] = source_count
                    found = True
                    break
            if not found:
                # 如果当天数据不存在，添加新数据
                data_list.append(current_data)
            await mongo_db["ALL_POST"].update_one(
                {"_id": all_post_record["_id"]},
                {"$set": {"data": data_list}}
            )
        else:
            # 如果文档不存在，插入新文档
            await mongo_db["ALL_POST"].insert_one({"data": [current_data]})

        # 准备要插入到 ALL_RES 集合的数据
        search_result = {
            # "search_content": {
            #     "wechat": all_wechat_articles,
            #     "weibo": all_weibo_dict,
            #     "renmin": all_renmin_data,
            #     "tieba": all_tieba_data
            # },
            "source_count": source_count,
        }

        data_to_insert = {
            "date": current_date,
            "search_result": search_result
        }
        print(data_to_insert)
        try:
            result = await mongo_db["ALL_RES"].insert_one(data_to_insert)
            print(f"插入成功，插入的文档 ID: {result.inserted_id}")
        except Exception as e:
            print(f"插入失败: {e}")
            return RESTfulModel(code=1, message=f"插入失败: {e}", data=[])

        return RESTfulModel(code=0, message="成功", data=search_result)

    except PyMongoError as pymongo_error:
        # 捕获 PyMongo 相关的异常
        return RESTfulModel(code=500, message=f"数据库操作发生错误: {str(pymongo_error)}", data=[])
    except Exception as e:
        return RESTfulModel(code=500, message=f"发生其他错误: {str(e)}", data=[])


@main_router.get('/all_apps', response_model=RESTfulModel,
                 description='多平台来源', summary='多个平台的来源')
async def multi_apps(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 去数据库 ALL_RES 里查找相关内容
        record = await mongo_db["ALL_RES"].find_one({"date": current_date})

        if record:
            # 直接获取 search_result 中的 source_count 内容
            search_result = record.get("search_result", {})
            source_count = search_result.get("source_count", {})
            return RESTfulModel(code=0, message="成功", data=source_count)
        else:
            return RESTfulModel(code=0, message="未找到当天的统计数据", data={})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_post', response_model=RESTfulModel,
                 description='多平台发布趋势', summary='多个平台的发布信息')
async def multi_post(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 从数据库 ALL_POST 里查找所有内容
        cursor = mongo_db["ALL_POST"].find()
        # 将查询结果转换为列表
        all_records = await cursor.to_list(length=None)

        # 移除每个文档中的 _id 字段
        for record in all_records:
            record.pop("_id", None)

        return RESTfulModel(code=0, message="成功", data=all_records)

    except PyMongoError as pymongo_error:
        # 捕获 PyMongo 相关的异常
        return RESTfulModel(code=500, message=f"数据库操作发生错误: {str(pymongo_error)}", data=[])
    except Exception as e:
        return RESTfulModel(code=500, message=f"发生其他错误: {str(e)}", data=[])


    # 请修改，先检查all_comment里面是否有今天日期的数据，有的话就直接返回成功，否则从HOT数据库里面获取当日的微博前三条信息tag进行调用函数main_screen_task_schedule来获取，爬取结束之后返回成功信息。


@main_router.get('/start_ip', response_model=RESTfulModel,
                 description='开始 ip 任务', summary='开始话题任务',
                 status_code=status.HTTP_201_CREATED)
async def add_task(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        # 检查 all_comment 数据库中是否有今天日期的数据
        comment_doc = await mongo_db[mongo_conf.ALL_COMMENT].find_one({"date": today})

        if comment_doc:
            # 如果有今天的数据，直接返回成功信息
            return RESTfulModel(code=200, message="已有今天的评论数据，无需爬取", data={})

        # 检查 HOT 数据库中是否有今天的数据
        hot_doc = await mongo_db["HOT"].find_one({"date": today})
        if not hot_doc:
            return RESTfulModel(code=404, message="未找到今日的 HOT 数据，无法开始爬取任务", data={})

        # 如果有今天的 HOT 数据，从 HOT 数据库获取前三条热搜
        hot_docs = mongo_db["HOT"].find({"date": today}).sort("_id", -1).limit(3)
        hot_tags = []
        async for doc in hot_docs:
            hot_tags.append(doc.get("tag"))

        # 确保 hot_tags 不为空
        if not hot_tags:
            return RESTfulModel(code=404, message="未找到今日热搜数据", data={})

        # 依次调用 main_screen_task_schedule 函数进行爬取，并收集任务 ID
        task_ids = []
        for tag in hot_tags:
            task = main_screen_task_schedule.delay(date=today, tag=tag)
            task_ids.append(task.id)

        # 爬取结束后返回成功信息
        return RESTfulModel(code=200, message=f"根据今日热搜 {hot_tags} 爬取任务完成", data={"task_id": task_ids})

    except PyMongoError as pymongo_error:
        # 捕获 PyMongo 相关的异常
        return RESTfulModel(code=500, message=f"数据库操作发生错误: {str(pymongo_error)}", data=[])
    except Exception as e:
        return RESTfulModel(code=500, message=f"发生其他错误: {str(e)}", data=[])


@main_router.get('/all_ip', response_model=RESTfulModel,
                 description='ip', summary='评论ip')
async def ip(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        # 从 ALL_COMMENT_IP 中获取当天的数据
        ip_doc = await mongo_db[mongo_conf.ALL_COMMENT_IP].find_one({"date": today})
        if ip_doc:
            ip_doc.pop("_id", None)  # 移除 MongoDB 的 _id 字段，方便返回
            return RESTfulModel(code=200, message="成功获取当天统计数据", data=ip_doc)
        else:
            return RESTfulModel(code=404, message="未找到当天的统计数据", data={})
    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])
