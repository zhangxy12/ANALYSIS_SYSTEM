import json
from datetime import datetime
from datetime import timedelta
from typing import Dict
import asyncio
import schedule
import time
import logging
import os
import sys
from threading import Thread

import requests
from bson.json_util import dumps
from cnsenti import Sentiment
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient

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
    log_path = os.path.join(log_dir, f'rumor_scheduler_{current_time}.log')

    print(f"谣言分析日志目录: {log_dir}")
    print(f"谣言分析日志文件路径: {log_path}")

    # 配置日志处理器
    file_handler = logging.FileHandler(log_path, encoding='utf-8', mode='a')
    console_handler = logging.StreamHandler(sys.stdout)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 获取logger并设置级别
    logger = logging.getLogger("rumor_scheduler")
    logger.setLevel(logging.INFO)

    # 清除已有的处理器（避免重复）
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("=" * 50)
    logger.info("谣言分析日志系统初始化成功，日志文件: %s", log_path)
    logger.info("=" * 50)

except Exception as e:
    print(f"谣言分析日志系统初始化失败: {e}")
    # 设置一个基本的日志配置以防失败
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("rumor_scheduler")
    logger.error(f"谣言分析日志系统初始化失败: {e}")

rumor_router = APIRouter(tags=['谣言分析api'])


# 添加直接获取数据库连接的函数
def get_direct_mongo_db():
    """
    直接获取MongoDB连接，不使用依赖注入，供定时任务使用
    """
    try:
        # 创建MongoDB客户端
        client = AsyncIOMotorClient(host=mongo_conf.HOST, port=mongo_conf.PORT)
        # 获取数据库连接
        db = client[mongo_conf.DB_NAME]
        logger.info(f"数据库连接成功: {mongo_conf.DB_NAME}")
        return db
    except Exception as e:
        logger.error(f"数据库连接失败: {e}", exc_info=True)
        raise


# 添加定时任务函数
async def fetch_rumor_data():
    """每天凌晨3点执行的谣言数据获取任务"""
    try:
        logger.info("开始执行谣言数据定时更新任务")
        mongo_db = get_direct_mongo_db()

        # 1. 搜索并保存谣言列表
        logger.info("开始获取谣言列表")
        try:
            await search_and_save_rumors(mongo_db)
            logger.info("成功获取并保存谣言列表")
        except Exception as e:
            logger.error(f"获取谣言列表失败: {e}", exc_info=True)

        # 2. 爬取并保存谣言详情
        logger.info("开始获取谣言详情")
        try:
            await crawl_and_save_rumor_details(mongo_db)
            logger.info("成功获取并保存谣言详情")
        except Exception as e:
            logger.error(f"获取谣言详情失败: {e}", exc_info=True)

        logger.info("谣言数据定时更新任务完成")

    except Exception as e:
        logger.error(f"谣言定时任务执行出错: {e}", exc_info=True)


# 在后台线程中运行定时任务
def run_rumor_scheduler():
    try:
        logger.info("启动谣言定时任务调度器")

        # 设置定时任务，每天凌晨3点执行
        schedule.every().day.at("03:00").do(run_rumor_fetch_task)

        # 不再立即执行任务，只在预定时间执行
        logger.info("谣言数据将在每天凌晨3点自动更新")

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                logger.error(f"谣言定时任务调度出错: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"启动谣言定时任务线程失败: {e}", exc_info=True)


# 在单独的函数中执行异步任务
def run_rumor_fetch_task():
    try:
        logger.info("开始执行谣言异步任务")
        # 创建一个新的事件循环来运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # 执行异步任务
        result = loop.run_until_complete(fetch_rumor_data())
        # 关闭事件循环
        loop.close()
        logger.info("谣言异步任务执行完成")
        return result
    except Exception as e:
        logger.error(f"执行谣言异步任务失败: {e}", exc_info=True)
        return None


# 启动定时任务线程
try:
    rumor_scheduler_thread = Thread(target=run_rumor_scheduler, daemon=True)
    rumor_scheduler_thread.start()
    logger.info("谣言定时任务线程已启动")
except Exception as e:
    logger.error(f"启动谣言定时任务线程失败: {e}", exc_info=True)


# 修改API实现，确保只从数据库获取数据，不触发爬取操作

@rumor_router.post('/rumor_search')
async def rumor_search(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 直接从数据库中获取谣言数据，不触发爬虫
        cursor = mongo_db['rumors'].find(projection={"_id": 0}, sort=[("date", -1)])
        rumors_data = [doc async for doc in cursor]

        if not rumors_data:
            # 如果没有数据，返回提示信息
            return {"message": "暂无谣言数据，系统将在每天凌晨3点自动更新", "data": []}

        return {"message": "成功获取谣言数据", "data": rumors_data}
    except Exception as e:
        return {"message": f"出现错误: {str(e)}", "data": []}


@rumor_router.post('/rumor_detail')
async def rumor_detail(mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 直接从数据库中获取谣言详情数据，不触发爬虫
        cursor = mongo_db['rumor_detail'].find(projection={"_id": 0}, sort=[("date", -1)])
        details_data = await cursor.to_list(length=None)

        if not details_data:
            # 如果没有数据，返回提示信息
            return {"message": "暂无谣言详情数据，系统将在每天凌晨3点自动更新", "data": []}

        return {"message": "成功获取谣言详情数据", "data": details_data}
    except Exception as e:
        return {"message": f"出现错误: {str(e)}", "data": []}


@rumor_router.get('/rumor_word', response_model=RESTfulModel)
async def rumor_details_word_cloud(db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        # 获取 rumor_detail 集合
        detail_collection = db['rumor_detail']

        # 查询所有文档
        cursor = detail_collection.find()
        all_documents = [doc async for doc in cursor]

        if not all_documents:
            # 如果没有数据，返回提示信息
            return RESTfulModel(code=0, message="暂无谣言数据，系统将在每天凌晨3点自动更新", data={"wordcloud_data": []})

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
        return RESTfulModel(code=500, message=f"发生错误: {str(e)}", data={"wordcloud_data": []})


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
