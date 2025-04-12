"""
情感分析任务
"""
from celery_task.utils import mongo_client
from celery_task.config import mongo_conf
from datetime import datetime
from collections import Counter

def mood_analyze_wx(wx: dict, tag_task_id: str):
    """
    对微信数据的 summary 字段进行情感分析，并将结果存储到 wx_mood 数据库中
    :param wx: wx信息，包含了所有微信文章的数据
    :param tag_task_id: 话题任务id
    :return:
    """
    # 获取微信文章数据
    wx_data = wx.get('data', [])  # 使用 get 方法避免键不存在的错误

    # 统计情感分布
    sentiment_counter = Counter()
    sentiment_by_date = {}  # 用于存储每一天的情感统计

    for article in wx_data:
        sentiment = article.get('sentiment', 'neutral')  # 获取情感分析结果（默认值为中性）
        sentiment_counter[sentiment] += 1

        # 统计按日期变化的情感
        publish_time = article.get('time')
        if publish_time:
            try:
                # 将日期字符串转换为日期对象，使用仅包含年月日的格式
                date_obj = datetime.strptime(publish_time, '%Y-%m-%d').date()
                date_str = str(date_obj)
                if date_str not in sentiment_by_date:
                    sentiment_by_date[date_str] = Counter()
                sentiment_by_date[date_str][sentiment] += 1
            except ValueError:
                print(f"日期格式错误: {publish_time}，跳过该条数据。")

    # 对日期进行从最远到最近排序
    sorted_dates = sorted(sentiment_by_date.keys(), reverse=False)  # 显式指定升序排序
    sorted_sentiment_by_date = {date: dict(sentiment_by_date[date]) for date in sorted_dates}

    # 情感分析结果统计
    statistics = {
        'total_sentiment': dict(sentiment_counter),
        'sentiment_by_date': sorted_sentiment_by_date
    }

    # 更新 wx_mood 数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.WX_MOOD].update_one(query_by_task_id, update_data, upsert=True)


def mood_analyze_rm(rm: dict, tag_task_id: str):
    """
    对人民网数据的 content 字段进行情感分析，并将结果存储到 rm_mood 数据库中
    :param rm: rm信息，包含了所有rmw文章的数据
    :param tag_task_id: 话题任务id
    :return:
    """
    # 获取文章数据
    rm_data = rm.get('data', [])  # rm['data'] 存储了所有rmw文章的数据

    # 统计情感分布
    sentiment_counter = Counter()
    sentiment_by_date = {}  # 用于存储每一天的情感统计

    for article in rm_data:
        sentiment = article.get('sentiment', 'neutral')  # 获取情感分析结果（默认值为中性）
        sentiment_counter[sentiment] += 1

        # 统计按日期变化的情感
        publish_time = article.get('displayTime')
        if publish_time:
            try:
                # 将日期字符串转换为日期对象
                date_obj = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S').date()
                date_str = str(date_obj)
                if date_str not in sentiment_by_date:
                    sentiment_by_date[date_str] = Counter()
                sentiment_by_date[date_str][sentiment] += 1
            except ValueError:
                print(f"日期格式错误: {publish_time}，跳过该条数据。")

    # 对日期进行从最远到最近排序
    sorted_dates = sorted(sentiment_by_date.keys(), reverse=False)  # 显式指定升序排序
    sorted_sentiment_by_date = {date: dict(sentiment_by_date[date]) for date in sorted_dates}

    # 情感分析结果统计
    statistics = {
        'total_sentiment': dict(sentiment_counter),
        'sentiment_by_date': sorted_sentiment_by_date
    }

    # 更新 rm_mood 数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.RM_MOOD].update_one(query_by_task_id, update_data, upsert=True)


def mood_analyze_tb(tb: dict, tag_task_id: str):
    """
    对tb数据的 content 字段进行情感分析，并将结果存储到 tb_mood 数据库中
    :param tb: tb信息，包含了所有tb文章的数据
    :param tag_task_id: 话题任务id
    :return:
    """
    # 获取文章数据
    tb_data = tb.get('data', [])  # tb['data'] 存储了所有tb文章的数据

    # 统计情感分布
    sentiment_counter = Counter()
    sentiment_by_date = {}  # 用于存储每一天的情感统计

    for article in tb_data:
        sentiment = article.get('sentiment', 'neutral')  # 获取情感分析结果（默认值为中性）
        sentiment_counter[sentiment] += 1

        # 统计按日期变化的情感
        publish_time = article.get('time')
        if publish_time:
            try:
                # 将日期字符串转换为日期对象
                date_obj = datetime.strptime(publish_time, '%Y-%m-%d %H:%M').date()
                date_str = str(date_obj)
                if date_str not in sentiment_by_date:
                    sentiment_by_date[date_str] = Counter()
                sentiment_by_date[date_str][sentiment] += 1
            except ValueError:
                print(f"日期格式错误: {publish_time}，跳过该条数据。")

    # 对日期进行从最远到最近排序
    sorted_dates = sorted(sentiment_by_date.keys(), reverse=False)  # 显式指定升序排序
    sorted_sentiment_by_date = {date: dict(sentiment_by_date[date]) for date in sorted_dates}

    # 情感分析结果统计
    statistics = {
        'total_sentiment': dict(sentiment_counter),
        'sentiment_by_date': sorted_sentiment_by_date
    }

    # 更新 tb_mood 数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.TB_MOOD].update_one(query_by_task_id, update_data, upsert=True)
