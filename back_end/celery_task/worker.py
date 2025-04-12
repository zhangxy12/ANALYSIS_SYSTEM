"""

"""
import time
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from pymongo import MongoClient

from celery_task import celeryapp
from celery_task.main_screen.m_spider import main_spider
from celery_task.tag_task.mood_analyze import mood_analyze_wx, mood_analyze_rm, mood_analyze_tb
from celery_task.tag_task.tag_spider_task import spider, spider_wx, spider_rm, spider_tb
from celery import current_task
from celery_task.tag_task.tag_introduce_task import introduce, introduce_wx, introduce_rm, introduce_tb
from celery_task.tag_task.tag_word_cloud_task import word_cloud, word_cloud_wx, word_cloud_rm, word_cloud_tb
from celery_task.tag_task.tag_relaton_task import tag_relation
from celery_task.tag_task.tag_hot_task import hot_task
from celery_task.tag_task.user_analyze import user_analyze_wx, origin_analyze_rm
from celery_task.tag_task.post_time import get_post_wx, get_post_rm, get_post_tb
from celery_task.topic.relation_task_topic import topic_tag_relation
from celery_task.topic.user_analysis import topic_user_analysis
from celery_task.topic.wb_spider import wb_spider
from celery_task.utils.update_task_status import update_task_status, update_task_status_wx, update_task_status_rm, \
    update_task_status_tb
from celery_task.tag_comment_task.task import start_task, start_task_tb, main_start_task
from celery_task.tag_task.tag_user_analysis_task import user_analysis
from celery_task.config import mongo_conf
from celery_task.utils import mongo_client
import asyncio


@celeryapp.task()
def topic_task_schedule(topic: str, tag: str):
    """
    任务管理函数
    :param topic: 话题任务id
    :param tag:话题名
    :return:
    """

    print('开始爬虫任务')
    weibo_data, weibo_post_list, user_id_list = wb_spider(tag, topic)

    print('分析用户成分任务')
    user_mark_data = topic_user_analysis(weibo_data, topic, user_id_list)
    print(user_mark_data)
    print('开始构建转发关系任务')
    topic_tag_relation(weibo_data, topic, user_mark_data)


@celeryapp.task()
def main_screen_task_schedule(date:str, tag: str):
    """
    任务管理函数
    :param tag:话题名
    :param date: 传入的日期
    :return:
    """
    print('开始爬虫任务')

    weibo_data, weibo_post_list = main_spider(date, tag)

    # 开始爬取详细博文任务, 由于分析用户成分任务阻塞时间较长，故而在此处发布博文详细任务的提取
    main_start_comment_task.delay(weibo_post_list, date)



@celeryapp.task()
def task_schedule(tag_task_id: str, tag: str):
    """
    任务管理函数
    :param tag_task_id: 话题任务id
    :param tag:话题名
    :param task_id_dict:各个任务id组成的字典
    :return:
    """

    print('开始爬虫任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "爬虫任务", 'task_id': tag_task_id})
    update_task_status(tag_task_id, 'PROGRESS')
    weibo_data, weibo_post_list, user_id_list = spider(tag, tag_task_id)

    print('开始构建话题基本信息任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建话题基本信息", 'task_id': tag_task_id})
    introduce(weibo_data, tag_task_id)

    print('开始构建词云任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建词云任务", 'task_id': tag_task_id})
    word_cloud(weibo_data, tag_task_id)

    # 开始爬取详细博文任务, 由于分析用户成分任务阻塞时间较长，故而在此处发布博文详细任务的提取
    start_comment_task.delay(weibo_post_list, tag_task_id)

    print('分析用户成分任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': '分析用户成分任务', 'task_id': tag_task_id})
    user_mark_data = user_analysis(weibo_data, tag_task_id, user_id_list)

    print('开始构建转发关系任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建转发关系任务", 'task_id': tag_task_id})
    tag_relation(weibo_data, tag_task_id, user_mark_data)

    print('开始挖掘热度数据任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "挖掘热度信息任务", 'task_id': tag_task_id})
    hot_task(weibo_data['tag'], tag_task_id)

    current_task.update_state(state='SUCCESS',
                              meta={'current': "完成", 'task_id': tag_task_id})
    update_task_status(tag_task_id, 'SUCCESS')


@celeryapp.task()
def start_comment_task(weibo_post_list: list, tag_task_id):
    """
    微博评论分析任务
    :param weibo_post_list: 要分析的博文详细信息
    :param tag_task_id: 任务id
    :return:
    """
    for weibo_post in weibo_post_list:
        start_task(tag_task_id=tag_task_id, weibo_post=weibo_post)
        time.sleep(3)


@celeryapp.task()
def main_start_comment_task(weibo_post_list: list, date):
    """
    微博评论分析任务
    :param weibo_post_list: 要分析的博文详细信息
    :param date: 指定日期
    :return:
    """
    for weibo_post in weibo_post_list:
        main_start_task(date=date, weibo_post=weibo_post)
        time.sleep(3)


@celeryapp.task()
def start_comment_task_tb(tb_post_list: list, tag_task_id):
    """
    tb评论分析任务
    :param tb_post_list: 要分析的博文详细信息
    :param tag_task_id: 任务id
    :return:
    """
    for tb_post in tb_post_list:
        start_task_tb(tag_task_id=tag_task_id, tb_post=tb_post)
        time.sleep(5)


@celeryapp.task()
def test(content: str):
    while True:
        print(content)


#6616523296

@celeryapp.task()
def task_schedule_wx(tag_task_id: str, tag: str):
    """
    wx任务管理函数
    :param tag_task_id: 话题任务id
    :param tag:话题名
    :param task_id_dict:各个任务id组成的字典
    :return:
    """
    print(f"Task ID: {tag_task_id}")  # 调试输出 task_id

    print('开始爬虫任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "爬虫任务", 'task_id': tag_task_id})
    update_task_status_wx('PROGRESS', tag_task_id)
    wx_data = spider_wx(tag, tag_task_id)
    print('爬虫任务结束')

    print('开始构建话题基本信息任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建话题基本信息", 'task_id': tag_task_id})
    introduce_wx(wx_data, tag_task_id)

    print('开始构建词云任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建词云任务", 'task_id': tag_task_id})
    word_cloud_wx(wx_data, tag_task_id)

    print('开始统计发布时间任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建统计发布时间任务", 'task_id': tag_task_id})
    get_post_wx(wx_data, tag_task_id)

    print('开始情感分析任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建情感分析任务", 'task_id': tag_task_id})
    mood_analyze_wx(wx_data, tag_task_id)

    print('开始公众号分析任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建公众号分析任务", 'task_id': tag_task_id})
    user_analyze_wx(wx_data, tag_task_id)

    current_task.update_state(state='SUCCESS',
                              meta={'current': "完成", 'task_id': tag_task_id})
    update_task_status_wx('SUCCESS', tag_task_id)


@celeryapp.task()
def task_schedule_rm(tag_task_id: str, tag: str):
    """
    rm任务管理函数
    :param tag_task_id: 话题任务id
    :param tag:话题名
    :param task_id_dict:各个任务id组成的字典
    :return:
    """
    print(f"Task ID: {tag_task_id}")  # 调试输出 task_id

    print('开始爬虫任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "爬虫任务", 'task_id': tag_task_id})
    update_task_status_rm('PROGRESS', tag_task_id)
    rm_data = spider_rm(tag, tag_task_id)
    print('爬虫任务结束')

    print('开始构建话题基本信息任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建话题基本信息", 'task_id': tag_task_id})
    introduce_rm(rm_data, tag_task_id)

    print('开始构建词云任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建词云任务", 'task_id': tag_task_id})
    word_cloud_rm(rm_data, tag_task_id)

    print('开始情感分析任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建情感分析任务", 'task_id': tag_task_id})
    mood_analyze_rm(rm_data, tag_task_id)

    print('开始统计发布时间任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建统计发布时间任务", 'task_id': tag_task_id})
    get_post_rm(rm_data, tag_task_id)

    print('开始来源分析任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建来源分析任务", 'task_id': tag_task_id})
    origin_analyze_rm(rm_data, tag_task_id)

    current_task.update_state(state='SUCCESS',
                              meta={'current': "完成", 'task_id': tag_task_id})
    update_task_status_rm('SUCCESS', tag_task_id)


@celeryapp.task()
def task_schedule_tb(tag_task_id: str, tag: str):
    """
    tb任务管理函数
    :param tag_task_id: 话题任务id
    :param tag:话题名
    :return:
    """
    print(f"Task ID: {tag_task_id}")  # 调试输出 task_id

    print('开始爬虫任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "爬虫任务", 'task_id': tag_task_id})
    update_task_status_tb('PROGRESS', tag_task_id)
    tb_data, tb_post_list = spider_tb(tag, tag_task_id)
    print('爬虫任务结束')

    print('开始构建话题基本信息任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建话题基本信息", 'task_id': tag_task_id})
    introduce_tb(tb_data, tag_task_id)

    # 开始爬取详细博文任务
    start_comment_task_tb.delay(tb_post_list, tag_task_id)

    print('开始构建词云任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建词云任务", 'task_id': tag_task_id})
    word_cloud_tb(tb_data, tag_task_id)

    print('开始情感分析任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建情感分析任务", 'task_id': tag_task_id})
    mood_analyze_tb(tb_data, tag_task_id)

    print('开始统计发布时间任务')
    current_task.update_state(state='PROGRESS',
                              meta={'current': "构建统计发布时间任务", 'task_id': tag_task_id})
    get_post_tb(tb_data, tag_task_id)

    # print('开始来源分析任务')
    # current_task.update_state(state='PROGRESS',
    #                           meta={'current': "构建来源分析任务", 'task_id': tag_task_id})
    # origin_analyze_rm(tb_data, tag_task_id)

    current_task.update_state(state='SUCCESS',
                              meta={'current': "完成", 'task_id': tag_task_id})
    update_task_status_tb('SUCCESS', tag_task_id)
