"""
:词云构建任务

"""

from celery_task.utils.my_cloud import MyCloud
from celery_task.utils import mongo_client
from celery_task.config import mongo_conf


def word_cloud(weibo: dict, tag_task_id: str):
    """
    词云构建函数
    :param weibo: 微博信息
    :param tag_task_id:话题任务id
    :return:
    """
    # 读取博文数据
    weibo_list = list()
    for weibo_item in weibo['data']:
        weibo_list.append(weibo_item['text'])

    # 词云构建
    my_cloud = MyCloud(weibo_list)
    word_cloud_list = my_cloud.GetWordCloud()
    if len(word_cloud_list) > 200:
        word_cloud_list = word_cloud_list[0: 200]

    # 存储词云
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': word_cloud_list}}
    mongo_client.db[mongo_conf.CLOUD].update_one(query_by_task_id, update_data)

def word_cloud_wx(wx: dict, tag_task_id: str):
    """
    词云构建函数
    :param wx: wx信息
    :param tag_task_id:话题任务id
    :return:
    """
    # 读取文章数据
    wx_list = list()
    for wx_item in wx['data']:
        wx_list.append(wx_item['summary'])

    # 词云构建
    my_cloud = MyCloud(wx_list)
    word_cloud_list = my_cloud.GetWordCloud()
    if len(word_cloud_list) > 200:
        word_cloud_list = word_cloud_list[0: 200]

    # 存储词云
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': word_cloud_list}}
    mongo_client.db[mongo_conf.WX_CLOUD].update_one(query_by_task_id, update_data)

def word_cloud_rm(rm: dict, tag_task_id: str):
    """
    词云构建函数
    :param rm: rm信息
    :param tag_task_id:话题任务id
    :return:
    """
    # 读取文章数据
    rm_list = list()
    for rm_item in rm['data']:
        rm_list.append(rm_item['content'])

    # 词云构建
    my_cloud = MyCloud(rm_list)
    word_cloud_list = my_cloud.GetWordCloud()
    if len(word_cloud_list) > 200:
        word_cloud_list = word_cloud_list[0: 200]

    # 存储词云
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': word_cloud_list}}
    mongo_client.db[mongo_conf.RM_CLOUD].update_one(query_by_task_id, update_data)


def word_cloud_tb(tb: dict, tag_task_id: str):
    """
    词云构建函数
    :param tb: tb信息
    :param tag_task_id:话题任务id
    :return:
    """
    # 读取文章数据
    tb_list = list()
    for tb_item in tb['data']:
        tb_list.append(tb_item['content'])

    # 词云构建
    my_cloud = MyCloud(tb_list)
    word_cloud_list = my_cloud.GetWordCloud()
    if len(word_cloud_list) > 200:
        word_cloud_list = word_cloud_list[0: 200]

    # 存储词云
    query_by_task_id = {'tag_task_id': tag_task_id}
    update_data = {"$set": {'data': word_cloud_list}}
    mongo_client.db[mongo_conf.TB_CLOUD].update_one(query_by_task_id, update_data)