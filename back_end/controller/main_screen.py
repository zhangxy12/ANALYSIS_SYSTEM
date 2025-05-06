import asyncio
import heapq
from datetime import datetime
import schedule
import time
import logging
import os
import sys
from threading import Thread

import requests
from cnsenti import Sentiment
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
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
from renmin_crawler.main import fetch_renmin_data
from tieba_crawler.main import fetch_posts

# 配置日志
# 使用绝对路径确保日志目录创建在正确位置
current_dir = os.path.dirname(os.path.abspath(__file__))
# 回退到项目根目录
root_dir = os.path.dirname(os.path.dirname(current_dir))
log_dir = os.path.join(root_dir, 'logs')

# 确保日志目录存在
try:
    os.makedirs(log_dir, exist_ok=True)
    # 在日志文件名中添加当前日期时间信息
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(log_dir, f'main_screen_{current_time}.log')

    print(f"日志目录: {log_dir}")
    print(f"日志文件路径: {log_path}")

    # 配置日志处理器
    file_handler = logging.FileHandler(log_path, encoding='utf-8', mode='a')
    console_handler = logging.StreamHandler(sys.stdout)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 获取logger并设置级别
    logger = logging.getLogger("main_screen_scheduler")
    logger.setLevel(logging.INFO)

    # 清除已有的处理器（避免重复）
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("=" * 50)
    logger.info("日志系统初始化成功，日志文件: %s", log_path)
    logger.info("=" * 50)

except Exception as e:
    print(f"日志系统初始化失败: {e}")
    # 设置一个基本的日志配置以防失败
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("main_screen_scheduler")
    logger.error(f"日志系统初始化失败: {e}")

main_router = APIRouter(tags=['可视化大屏api'])


# 添加情感分析函数
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


# 添加直接获取数据库连接的函数
def get_direct_mongo_db():
    """
    直接获取MongoDB连接，不使用依赖注入，供定时任务使用
    """
    try:
        # 使用host和port方式连接，兼容现有配置
        client = AsyncIOMotorClient(host=mongo_conf.HOST, port=mongo_conf.PORT)
        # 获取数据库连接
        db = client[mongo_conf.DB_NAME]
        logger.info(f"数据库连接成功: {mongo_conf.DB_NAME}")
        return db
    except Exception as e:
        logger.error(f"数据库连接失败: {e}", exc_info=True)
        raise


# 添加定时任务函数
async def fetch_all_data():
    """每天凌晨2点执行的数据获取任务"""
    try:
        logger.info("开始执行大屏数据定时更新任务")
        # 使用直接获取连接的方式，而不是依赖注入
        mongo_db = get_direct_mongo_db()
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 获取热搜数据
        logger.info("获取各平台热搜数据")
        try:
            app1_hot = fetch_weibo_hot()
            logger.info(f"成功获取微博热搜，数量: {len(app1_hot)}")
        except Exception as e:
            logger.error(f"获取微博热搜失败: {e}")
            app1_hot = []

        try:
            app2_hot = fetch_tieba_hot()
            logger.info(f"成功获取贴吧热搜，数量: {len(app2_hot)}")
        except Exception as e:
            logger.error(f"获取贴吧热搜失败: {e}")
            app2_hot = []

        try:
            app3_hot = fetch_baidu_hot()
            logger.info(f"成功获取百度热搜，数量: {len(app3_hot)}")
        except Exception as e:
            logger.error(f"获取百度热搜失败: {e}")
            app3_hot = []

        if not app1_hot and not app2_hot and not app3_hot:
            logger.error("所有平台热搜获取失败，中止任务")
            return

        # 更新HOT集合
        try:
            await mongo_db["HOT"].update_one(
                {"date": current_date},
                {"$set": {
                    "weibo": app1_hot,
                    "tieba": app2_hot,
                    "baidu": app3_hot
                }},
                upsert=True
            )
            logger.info("成功更新HOT集合")
        except Exception as e:
            logger.error(f"更新HOT集合失败: {e}")
            return

        # 更新词云数据
        logger.info("生成并更新词云数据")
        all_hot_titles = []
        for platform, data in [('weibo', app1_hot), ('tieba', app2_hot), ('baidu', app3_hot)]:
            for item in data:
                all_hot_titles.append(item.get('title', ''))

        try:
            cloud = MyCloud(content=all_hot_titles)
            wordcloud_data = cloud.GetWordCloud()

            await mongo_db["HOT_WORD"].update_one(
                {"date": current_date},
                {"$set": {"wordcloud_data": wordcloud_data}},
                upsert=True
            )
            logger.info(f"成功更新词云数据，词汇数: {len(wordcloud_data)}")
        except Exception as e:
            logger.error(f"更新词云数据失败: {e}")

        # 更新文本分类数据
        logger.info("更新文本分类数据")
        try:
            # 初始化文本分类器
            classifier = TextClassifier()
            # 初始化分类结果计数器
            class_count = {label: 0 for label in classifier.labels}
            # 对每个title进行文本分类
            for title in all_hot_titles:
                if title:
                    category = classifier.classify_text(title)
                    class_count[category] += 1

            await mongo_db["HOT_CLASS"].update_one(
                {"date": current_date},
                {"$set": {"class_count": class_count}},
                upsert=True
            )
            logger.info(f"成功更新分类数据: {class_count}")
        except Exception as e:
            logger.error(f"更新分类数据失败: {e}")

        # 更新情感分析数据
        logger.info("更新情感分析数据")
        try:
            # 情感占比统计
            total_count = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0

            for platform, data in [('weibo', app1_hot), ('tieba', app2_hot), ('baidu', app3_hot)]:
                for item in data:
                    sentiment_score = analyze_sentiment(item.get('title', ''))
                    total_count += 1
                    if sentiment_score == 1:
                        positive_count += 1
                    elif sentiment_score == 0:
                        negative_count += 1
                    else:
                        neutral_count += 1

            if total_count > 0:
                positive_ratio = positive_count / total_count
                negative_ratio = negative_count / total_count
                neutral_ratio = neutral_count / total_count
            else:
                positive_ratio = 0
                negative_ratio = 0
                neutral_ratio = 0

            # 获取正面和负面高频词
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

            analysis_result = {
                "sentiment_ratio": {
                    "positive": positive_ratio,
                    "negative": negative_ratio,
                    "neutral": neutral_ratio
                },
                "top_positive_words": formatted_positive,
                "top_negative_words": formatted_negative
            }

            await mongo_db["HOT_MOOD"].update_one(
                {"date": current_date},
                {"$set": {"analysis_result": analysis_result}},
                upsert=True
            )
            logger.info("成功更新情感分析数据")
        except Exception as e:
            logger.error(f"更新情感分析数据失败: {e}")

        # 更新多平台搜索数据
        logger.info("更新多平台搜索数据")
        try:
            tags = []
            for platform, data in [('weibo', app1_hot), ('tieba', app2_hot), ('baidu', app3_hot)]:
                for item in data[:3]:  # 取前三个热点
                    title = item.get('title')
                    if title:
                        tags.append(title)

            logger.info(f"使用热搜标签: {tags}")
            all_wechat_articles = []
            all_weibo_dict = []
            all_renmin_data = []
            all_tieba_data = []

            # 对每个tag进行搜索
            for tag in tags:
                # 获取微信数据
                try:
                    wechat_articles = search_wechat_articles(tag, 1)
                    all_wechat_articles.extend(wechat_articles)
                    logger.info(f"微信搜索'{tag}'成功，获取{len(wechat_articles)}条数据")
                except Exception as e:
                    logger.error(f"微信搜索'{tag}'失败: {e}")

                # 获取微博数据
                try:
                    weibo_url = f"{weibo_conf.BASEPATH}/weibo_curl/api/search_tweets?keyword={tag}&cursor=1&is_hot=1"
                    logger.info(f"微博API请求: {weibo_url}")
                    weibo_response = requests.get(weibo_url)
                    weibo_response.raise_for_status()
                    weibo_dict = weibo_response.json().get('data')
                    if weibo_dict and "result" in weibo_dict:
                        all_weibo_dict.extend(weibo_dict["result"])
                        logger.info(f"微博搜索'{tag}'成功，获取{len(weibo_dict['result'])}条数据")
                    else:
                        logger.warning(f"微博搜索'{tag}'返回无效数据: {weibo_dict}")
                except Exception as e:
                    logger.error(f"微博搜索'{tag}'失败: {e}")

                # 获取人民网数据
                try:
                    renmin_data = fetch_renmin_data(tag, 1)
                    all_renmin_data.extend(renmin_data)
                    logger.info(f"人民网搜索'{tag}'成功，获取{len(renmin_data)}条数据")
                except Exception as e:
                    logger.error(f"人民网搜索'{tag}'失败: {e}")

                # 获取贴吧数据
                try:
                    tieba_data = fetch_posts(tag, 1, [])
                    all_tieba_data.extend(tieba_data)
                    logger.info(f"贴吧搜索'{tag}'成功，获取{len(tieba_data)}条数据")
                except Exception as e:
                    logger.error(f"贴吧搜索'{tag}'失败: {e}")

            # 统计数据来源和数量
            source_count = {
                "wechat": len(all_wechat_articles),
                "weibo": len(all_weibo_dict),
                "renmin": len(all_renmin_data),
                "tieba": len(all_tieba_data)
            }
            logger.info(f"多平台数据统计: {source_count}")

            # 准备当前日期的数据
            current_data = {
                "date": current_date,
                "source_count": source_count
            }

            # 查找ALL_POST集合中的文档
            all_post_record = await mongo_db["ALL_POST"].find_one()

            if all_post_record:
                # 如果文档存在，更新data数组
                data_list = all_post_record.get("data", [])
                found = False
                for index, data in enumerate(data_list):
                    if data["date"] == current_date:
                        # 如果当天数据已存在，更新source_count
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
                logger.info("成功更新ALL_POST集合")
            else:
                # 如果文档不存在，插入新文档
                await mongo_db["ALL_POST"].insert_one({"data": [current_data]})
                logger.info("成功创建ALL_POST集合")

            search_result = {
                "source_count": source_count,
            }

            await mongo_db["ALL_RES"].update_one(
                {"date": current_date},
                {"$set": {"search_result": search_result}},
                upsert=True
            )
            logger.info("成功更新ALL_RES集合")
        except Exception as e:
            logger.error(f"更新多平台搜索数据失败: {e}")

        # 更新IP数据（获取评论IP分布）
        logger.info("更新IP数据")
        try:
            # 获取当天热搜的前三条作为tag
            hot_tags = []
            for platform, data in [('weibo', app1_hot), ('tieba', app2_hot), ('baidu', app3_hot)]:
                for item in data[:1]:  # 每个平台取1条，共3条
                    if item and item.get('title'):
                        hot_tags.append(item.get('title'))

            # 调用任务获取评论IP数据
            for tag in hot_tags:
                if tag:
                    try:
                        task = main_screen_task_schedule.delay(date=current_date, tag=tag)
                        logger.info(f"启动IP数据收集任务: {task.id}, tag: {tag}")
                    except Exception as e:
                        logger.error(f"启动IP数据收集任务失败, tag: {tag}, 错误: {e}")
        except Exception as e:
            logger.error(f"更新IP数据失败: {e}")

        logger.info("大屏数据定时更新任务完成")

    except Exception as e:
        logger.error(f"定时任务执行出错: {e}", exc_info=True)


# 在后台线程中运行定时任务
def run_scheduler():
    try:
        logger.info("启动定时任务调度器")

        # 测试日志
        logger.info("测试日志记录")
        logger.warning("测试警告日志")
        logger.error("测试错误日志")

        # 设置定时任务，每天凌晨2点执行
        schedule.every().day.at("02:00").do(run_fetch_task)

        # 不再立即执行任务，只在预定时间执行
        logger.info("大屏数据将在每天凌晨2点自动更新")

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                logger.error(f"定时任务调度出错: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"启动定时任务线程失败: {e}", exc_info=True)


# 在单独的函数中执行异步任务
def run_fetch_task():
    try:
        logger.info("开始执行异步任务")
        # 创建一个新的事件循环来运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # 执行异步任务
        result = loop.run_until_complete(fetch_all_data())
        # 关闭事件循环
        loop.close()
        logger.info("异步任务执行完成")
        return result
    except Exception as e:
        logger.error(f"执行异步任务失败: {e}", exc_info=True)
        return None


# 启动定时任务线程
try:
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("定时任务线程已启动")
except Exception as e:
    logger.error(f"启动定时任务线程失败: {e}", exc_info=True)


# API实现，确保只从数据库获取数据，不触发爬取操作

@main_router.get('/all_hot', response_model=RESTfulModel,
                 description='获取所有热搜事件', summary='返回热搜数据')
async def get_hot(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 只从数据库中获取记录，不再触发爬取
        latest_record = await mongo_db["HOT"].find_one({"date": current_date})

        if latest_record:
            # 如果有当天记录，直接返回数据
            result_data = {
                "weibo": latest_record.get("weibo", []),
                "tieba": latest_record.get("tieba", []),
                "baidu": latest_record.get("baidu", [])
            }
            return RESTfulModel(code=0, message="成功", data=result_data)
        else:
            # 如果没有当天记录，返回空数据
            return RESTfulModel(code=0, message="尚未获取今日数据", data={"weibo": [], "tieba": [], "baidu": []})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_hot_word', response_model=RESTfulModel,
                 description='获取所有热搜事件的词云', summary='返回热搜数据词云')
async def get_hot_word(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 从数据库中获取当天的词云数据
        existing_record = await mongo_db["HOT_WORD"].find_one({"date": current_date})

        if existing_record:
            wordcloud_data = existing_record["wordcloud_data"]
            return RESTfulModel(code=0, message="成功", data=wordcloud_data)
        else:
            # 如果没有当天数据，返回空数据
            return RESTfulModel(code=0, message="尚未获取今日数据", data=[])

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_hot_class', response_model=RESTfulModel,
                 description='获取所有热搜事件的文本分类', summary='返回热搜数据文本分类')
async def get_hot_class(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 从数据库中获取当天的分类数据
        existing_record = await mongo_db["HOT_CLASS"].find_one({"date": current_date})

        if existing_record:
            return RESTfulModel(code=0, message="成功", data=existing_record["class_count"])
        else:
            # 如果没有当天数据，返回空数据
            return RESTfulModel(code=0, message="尚未获取今日数据", data={})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_hot_mood', response_model=RESTfulModel,
                 description='获取所有热搜事件的情感分析，正反面词频统计', summary='返回热搜数据情感分析，正反面词频统计')
async def get_hot_mood(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 从数据库中获取当天的情感分析数据
        existing_record = await mongo_db["HOT_MOOD"].find_one({"date": current_date})

        if existing_record:
            return RESTfulModel(code=0, message="成功", data=existing_record["analysis_result"])
        else:
            # 如果没有当天数据，返回空数据
            return RESTfulModel(code=0, message="尚未获取今日数据", data={
                "sentiment_ratio": {"positive": 0, "negative": 0, "neutral": 0},
                "top_positive_words": [],
                "top_negative_words": []
            })

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_multi_search', response_model=RESTfulModel,
                 description='多平台搜索', summary='搜索多个平台的相关内容')
async def multi_platform_search(cursor: int = 1, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 从数据库中获取当天的搜索结果
        existing_record = await mongo_db["ALL_RES"].find_one({"date": current_date})

        if existing_record:
            return RESTfulModel(code=0, message="成功", data=existing_record["search_result"])
        else:
            # 如果没有当天数据，返回空数据
            return RESTfulModel(code=0, message="尚未获取今日数据",
                                data={"source_count": {"wechat": 0, "weibo": 0, "renmin": 0, "tieba": 0}})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_apps', response_model=RESTfulModel,
                 description='多平台来源', summary='多个平台的来源')
async def multi_apps(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 从数据库中获取当天的多平台来源数据
        record = await mongo_db["ALL_RES"].find_one({"date": current_date})

        if record:
            search_result = record.get("search_result", {})
            source_count = search_result.get("source_count", {})
            return RESTfulModel(code=0, message="成功", data=source_count)
        else:
            return RESTfulModel(code=0, message="尚未获取今日数据", data={})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


@main_router.get('/all_post', response_model=RESTfulModel,
                 description='多平台发布趋势', summary='多个平台的发布信息')
async def multi_post(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 从数据库中获取所有发布趋势数据
        cursor = mongo_db["ALL_POST"].find()
        all_records = await cursor.to_list(length=None)

        if all_records:
            # 移除每个文档中的_id字段
            for record in all_records:
                record.pop("_id", None)
            return RESTfulModel(code=0, message="成功", data=all_records)
        else:
            return RESTfulModel(code=0, message="尚未获取趋势数据", data=[])

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data=[])


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
            return RESTfulModel(code=404, message="尚未获取今日IP数据", data={"date": today, "detail": []})

    except Exception as e:
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data={"date": today, "detail": []})


# 手动触发数据更新的API，现在只返回自动更新信息
@main_router.get('/manual_refresh', response_model=RESTfulModel,
                 description='手动刷新信息', summary='返回数据自动更新信息')
async def manual_refresh():
    try:
        logger.info("收到手动刷新请求，但已被禁用")
        return RESTfulModel(code=0, message="系统已配置为每天凌晨2点自动更新数据，无需手动刷新", data={})
    except Exception as e:
        logger.error(f"手动刷新请求处理失败: {str(e)}", exc_info=True)
        return RESTfulModel(code=500, message=f"请求处理失败: {str(e)}", data={})
