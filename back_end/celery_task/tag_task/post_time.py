"""
:统计发布时间构建任务

"""
from collections import defaultdict
from datetime import datetime

import pytz

from celery_task.utils import mongo_client
from celery_task.config import mongo_conf

def get_post_wx(wx: dict, tag_task_id: str):
    """
    统计发布时间函数
    :param wx: wx信息
    :param tag_task_id:话题任务id
    :return:
    """
    # 获取微信文章数据
    wx_data = wx['data']  # wx['data'] 存储了所有微信文章的数据

    # 统计按天和月的发博数量
    time_stats = defaultdict(lambda: defaultdict(int))
    tz = pytz.timezone('Asia/Shanghai')

    # 遍历微信数据并进行时间统计
    for entry in wx_data:
        created_at = entry.get('time')  # 'time' 是文章的发布时间字段
        if created_at:
            # 转换为datetime对象
            try:
                created_time = datetime.strptime(created_at, '%Y-%m-%d')  #  'YYYY-MM-DD' 格式
                created_time = tz.localize(created_time)  # 本地化时间

                # 按天、月进行统计
                day = created_time.strftime('%Y-%m-%d')
                month = created_time.strftime('%Y-%m')

                time_stats['day'][day] += 1
                time_stats['month'][month] += 1
            except ValueError:
                continue  # 如果时间格式有误，则跳过该条数据

    # 构建统计数据字典
    statistics = {
        'day': dict(time_stats['day']),
        'month': dict(time_stats['month']),
    }

    # 更新数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.WX_POST].update_one(query_by_task_id, update_data)

def get_post_rm(rm: dict, tag_task_id: str):
    """
    统计发布时间函数
    :param rm: rm信息
    :param tag_task_id:话题任务id
    :return:
    """
    # 获取rmw文章数据
    rm_data = rm['data']

    # 统计按天和月的发博数量
    time_stats = defaultdict(lambda: defaultdict(int))
    tz = pytz.timezone('Asia/Shanghai')

    # 遍历微信数据并进行时间统计
    for entry in rm_data:
        created_at = entry.get('displayTime')  # 'time' 是文章的发布时间字段
        if created_at:
            # 转换为datetime对象
            try:
                created_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                created_time = tz.localize(created_time)  # 本地化时间

                # 按天、月进行统计
                day = created_time.strftime('%Y-%m-%d')
                month = created_time.strftime('%Y-%m')

                time_stats['day'][day] += 1
                time_stats['month'][month] += 1
            except ValueError:
                continue  # 如果时间格式有误，则跳过该条数据

    # 构建统计数据字典
    statistics = {
        'day': dict(time_stats['day']),
        'month': dict(time_stats['month']),
    }

    # 更新数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.RM_POST].update_one(query_by_task_id, update_data)


def get_post_tb(tb: dict, tag_task_id: str):
    """
    统计发布时间函数
    :param tb: tb信息
    :param tag_task_id:话题任务id
    :return:
    """
    # 获取tb文章数据
    tb_data = tb['data']

    # 统计按天和月的发博数量
    time_stats = defaultdict(lambda: defaultdict(int))
    tz = pytz.timezone('Asia/Shanghai')

    # 遍历微信数据并进行时间统计
    for entry in tb_data:
        created_at = entry.get('time')  # 'time' 是文章的发布时间字段
        if created_at:
            # 转换为datetime对象
            try:
                created_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M')
                created_time = tz.localize(created_time)  # 本地化时间

                # 按天、月进行统计
                day = created_time.strftime('%Y-%m-%d')
                month = created_time.strftime('%Y-%m')

                time_stats['day'][day] += 1
                time_stats['month'][month] += 1
            except ValueError:
                continue  # 如果时间格式有误，则跳过该条数据

    # 构建统计数据字典
    statistics = {
        'day': dict(time_stats['day']),
        'month': dict(time_stats['month']),
    }

    # 更新数据库中的统计数据
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': statistics}}
    mongo_client.db[mongo_conf.TB_POST].update_one(query_by_task_id, update_data)

