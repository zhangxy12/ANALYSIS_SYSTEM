"""
:更新任务状态

"""
from celery_task.config import mongo_conf
from celery_task.utils import mongo_client


def update_task_status(status: str, tag_task_id: str):
    """
    更新任务状态
    :param tag_task_id:任务id
    :param status: 状态信息
    :return:
    """
    query_by_id = {'tag_task_id': tag_task_id}
    update_data = {'$set': {'status': status}}
    print('任务状态:', status)
    mongo_client.db[mongo_conf.TASK].update_one(query_by_id, update_data)

def update_task_status_wx(status: str, tag_task_id: str):
    """
    更新任务状态
    :param tag_task_id:任务id
    :param status: 状态信息
    :return:
    """
    query_by_id = {'tag_task_id': tag_task_id}
    update_data = {'$set': {'status': status}}
    print('任务状态:', status)
    mongo_client.db[mongo_conf.WX_TASK].update_one(query_by_id, update_data)

def update_task_status_rm(status: str, tag_task_id: str):
    """
    更新任务状态
    :param tag_task_id:任务id
    :param status: 状态信息
    :return:
    """
    query_by_id = {'tag_task_id': tag_task_id}
    update_data = {'$set': {'status': status}}
    print('任务状态:', status)
    mongo_client.db[mongo_conf.RM_TASK].update_one(query_by_id, update_data)

def update_task_status_tb(status: str, tag_task_id: str):
    """
    更新任务状态
    :param tag_task_id:任务id
    :param status: 状态信息
    :return:
    """
    query_by_id = {'tag_task_id': tag_task_id}
    update_data = {'$set': {'status': status}}
    print('任务状态:', status)
    mongo_client.db[mongo_conf.TB_TASK].update_one(query_by_id, update_data)


if __name__ == '__main__':
    update_task_status('SUCCESS', '0e7a55180f19754437032894a709e597')
