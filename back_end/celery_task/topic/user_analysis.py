"""
:用户分析任务

"""
from celery_task.utils.gopup_utils import tendency
from celery_task.utils.my_db import Mongo
import requests
import json
from celery_task.utils.themeCluster.Single_Pass.single_pass_cluster_topic import SinglePassCluster
from celery_task.utils.gopup_utils import user
import random
import time


def topic_user_analysis(weibo_blog_data: dict, topic: str, user_id_list: list):
    user_list = list()
    for user_id in user_id_list:
        try:
            user_url = 'http://127.0.0.1:8000/weibo_curl/api/users_show?user_id={user_id}'.format(user_id=user_id)
            print(f'爬取:{user_id}用户')
            user_dict = json.loads(requests.get(user_url, verify=False).text)
            if user_dict['error_code'] == 0:
                user_list.append(user_dict.get('data').get('result'))
            else:
                user_list.append(user(user_id))
        except:
            print(f'user_id={user_id},用户信息爬取失败')
            time.sleep(random.uniform(5, 15))
    user_mark = SinglePassCluster(topic=topic, blog_data=weibo_blog_data.get('data'),
                                  user_list=user_list)
    user_mark_data = user_mark.single_pass()
    return user_mark_data
