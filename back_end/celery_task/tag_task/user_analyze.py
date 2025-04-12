"""
用户分析任务
"""
from celery_task.utils import mongo_client
from celery_task.config import mongo_conf
from datetime import datetime
from collections import Counter

def user_analyze_wx(wx: dict, tag_task_id: str):
    """
    对微信数据的 source 字段进行分析，并将结果存储到 wx_user 数据库中
    :param wx: wx信息，包含了所有微信文章的数据
    :param tag_task_id: 话题任务id
    :return:
    """
    # 获取微信文章数据
    wx_data = wx['data']  # wx['data'] 存储了所有微信文章的数据

    # 提取所有 source 字段的值，过滤掉空字符串和仅含空格的字符串
    sources = [item.get('source') for item in wx_data if 'source' in item and item.get('source', '').strip()]

    # 统计每个 source 出现的次数
    source_counter = Counter(sources)

    # 获取出现次数最多的前五个 source
    top_five_sources = source_counter.most_common(5)

    # 构建统计数据
    statistics = [{"name": source, "count": count} for source, count in top_five_sources]

    # 更新 wx_user 数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.WX_USER].update_one(query_by_task_id, update_data, upsert=True)


def origin_analyze_rm(rm: dict, tag_task_id: str):
    """
    对数据的 originName 字段进行分析，并将结果存储到 rm_origin 数据库中
    :param rm: rm信息，包含了所有微信文章的数据
    :param tag_task_id: 话题任务id
    :return:
    """
    # 获取文章数据
    rm_data = rm['data']

    # 提取所有 originName 字段的值，过滤掉空格字符串
    originNames = [item.get('originName') for item in rm_data if
                   'originName' in item and item.get('originName').strip()]

    # 统计每个 originName 出现的次数
    originName_counter = Counter(originNames)

    # 获取出现次数最多的前五个 originName
    top = originName_counter.most_common(10)

    # 构建统计数据
    statistics = [{"name": source, "count": count} for source, count in top]

    # 更新 rm_origin 数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.RM_ORIGIN].update_one(query_by_task_id, update_data, upsert=True)