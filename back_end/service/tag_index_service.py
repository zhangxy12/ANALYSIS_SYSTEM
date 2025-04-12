"""
:话题总览页的数据提取服务

"""
from motor.motor_asyncio import AsyncIOMotorDatabase
import signal
from exceptions import NotExistException
from service.get_task_state import get_task_state, get_task_state_wx, get_task_state_rm, get_task_state_tb
from models.dto.tag_dto.introduce_dto import User, ProgressTask, TagBase
from celery_task import celeryapp
from service.comment_extract import deleteTask, deleteTask_tb


async def get_tag_task_list(mongo_db: AsyncIOMotorDatabase) -> list:
    tag_list_find = mongo_db['tag_task'].find({})
    tag_list = list()
    for tag in await tag_list_find.to_list(length=100):
        status = await get_task_state(tag_task_id=tag['tag_task_id'], mongo_db=mongo_db)
        if status == 'SUCCESS':
            tag_base = await mongo_db['tag_introduce'].find_one({'tag_task_id': tag['tag_task_id']})
            if tag_base:
                user = User(
                    **tag_base['vital_user']
                    # user_id=tag_base['vital_user']['user_id'],
                    #         head=tag_base['vital_user']['head'],
                    #         nickname=tag_base['vital_user']['nickname'],
                    #         birthday=tag_base['vital_user']['birthday'],
                    #         verified_reason=tag_base['vital_user']['verified_reason'],
                    #         gender=tag_base['vital_user']['gender'],
                    #         location=tag_base['vital_user']['location'],
                    #         description=tag_base['vital_user']['description'],
                    #         education=tag_base['vital_user']['education'],
                    #         work=tag_base['vital_user']['work'],
                    #         weibo_num=tag_base['vital_user']['weibo_num'],
                    #         following=tag_base['vital_user']['following'],
                    #         followers=tag_base['vital_user']['followers'],
                    #         max_page=tag_base['vital_user']['max_page']
                )
                tag_list.append(TagBase(
                    tag_task_id=tag['tag_task_id'],
                    tag=tag_base['tag'],
                    user_count=tag_base['user_count'],
                    weibo_count=tag_base['weibo_count'],
                    vital_user=user)
                )
        else:
            tag['status'] = status
            tag.pop('_id')
            tag_list.append(ProgressTask(**tag))

    return tag_list


async def get_tag_task_list_wx(mongo_db: AsyncIOMotorDatabase) -> list:
    tag_list_find = mongo_db['wx_task'].find({})
    tag_list = list()
    for tag in await tag_list_find.to_list(length=100):
        status = await get_task_state_wx(tag_task_id=tag['tag_task_id'], mongo_db=mongo_db)
        if status == 'SUCCESS':
            tag_base = await mongo_db['wx_introduce'].find_one({'tag_task_id': tag['tag_task_id']})

            if tag_base:
                # 返回指定字段，并确保字段不为null
                tag_list.append({
                    'tag_task_id': tag['tag_task_id'],
                    'tag': tag_base['tag'],
                    'gzh_count': tag_base.get('gzh_count', 0),
                    'wx_count': tag_base.get('wx_count', 0),
                })
        else:
            tag['status'] = status
            tag.pop('_id')
            # 返回指定字段
            tag_list.append({
                'tag_task_id': tag['tag_task_id'],
                'tag': tag['tag'],
                'status': status,
                # 确保ProgressTask有你需要的字段
            })

    return tag_list


async def get_tag_task_list_rm(mongo_db: AsyncIOMotorDatabase) -> list:
    tag_list_find = mongo_db['rm_task'].find({})
    tag_list = list()
    for tag in await tag_list_find.to_list(length=100):
        status = await get_task_state_rm(tag_task_id=tag['tag_task_id'], mongo_db=mongo_db)
        if status == 'SUCCESS':
            tag_base = await mongo_db['rm_introduce'].find_one({'tag_task_id': tag['tag_task_id']})

            if tag_base:
                # 返回指定字段，并确保字段不为null
                tag_list.append({
                    'tag_task_id': tag['tag_task_id'],
                    'tag': tag_base['tag'],
                    'rm_origin': tag_base.get('rm_origin', 0),
                    'rm_count': tag_base.get('rm_count', 0),
                })
        else:
            tag['status'] = status
            tag.pop('_id')
            # 返回指定字段
            tag_list.append({
                'tag_task_id': tag['tag_task_id'],
                'tag': tag['tag'],
                'status': status,
                # 确保ProgressTask有你需要的字段
            })

    return tag_list

async def get_tag_task_list_tb(mongo_db: AsyncIOMotorDatabase) -> list:
    tag_list_find = mongo_db['tb_task'].find({})
    tag_list = list()
    for tag in await tag_list_find.to_list(length=100):
        status = await get_task_state_tb(tag_task_id=tag['tag_task_id'], mongo_db=mongo_db)
        if status == 'SUCCESS':
            tag_base = await mongo_db['tb_introduce'].find_one({'tag_task_id': tag['tag_task_id']})

            if tag_base:
                # 返回指定字段，并确保字段不为null
                tag_list.append({
                    'tag_task_id': tag['tag_task_id'],
                    'tag': tag_base['tag'],
                    'tb_user': tag_base.get('tb_user', 0),
                    'tb_count': tag_base.get('tb_count', 0),
                })
        else:
            tag['status'] = status
            tag.pop('_id')
            # 返回指定字段
            tag_list.append({
                'tag_task_id': tag['tag_task_id'],
                'tag': tag['tag'],
                'status': status,
                # 确保ProgressTask有你需要的字段
            })

    return tag_list

async def get_tag_hot_blog(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> list:
    mongo_collection = mongo_db['blog']
    blog_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if blog_result:
        blog_result.pop('_id')
        blog_result['data'] = blog_result['data'][0:10]
        return blog_result['data']
    else:
        raise NotExistException(tag_task_id + '\'s hot_blog')


async def get_word_cloud(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['tag_word_cloud']
    word_cloud_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if word_cloud_result:
        word_cloud_result.pop('_id')
    return word_cloud_result

async def get_word_cloud_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['wx_word_cloud']
    word_cloud_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if word_cloud_result:
        word_cloud_result.pop('_id')
    return word_cloud_result

async def get_post_time_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['wx_post']
    post_time_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if post_time_result:
        post_time_result.pop('_id')
    return post_time_result

async def get_mood_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['wx_mood']
    mood_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if mood_result:
        mood_result.pop('_id')
    return mood_result

async def get_user_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['wx_user']
    user_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if user_result:
        user_result.pop('_id')
    return user_result

# 人民网
async def get_word_cloud_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['rm_word_cloud']
    word_cloud_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if word_cloud_result:
        word_cloud_result.pop('_id')
    return word_cloud_result

async def get_mood_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['rm_mood']
    mood_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if mood_result:
        mood_result.pop('_id')
    return mood_result

async def get_post_time_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['rm_post']
    post_time_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if post_time_result:
        post_time_result.pop('_id')
    return post_time_result

async def get_origin_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['rm_origin']
    origin_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if origin_result:
        origin_result.pop('_id')
    return origin_result


# 贴吧
async def get_word_cloud_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['tb_word_cloud']
    word_cloud_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if word_cloud_result:
        word_cloud_result.pop('_id')
    return word_cloud_result

async def get_mood_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['tb_mood']
    mood_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if mood_result:
        mood_result.pop('_id')
    return mood_result

async def get_post_time_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['tb_post']
    post_time_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if post_time_result:
        post_time_result.pop('_id')
    return post_time_result

async def get_tiezi_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> list:
    mongo_collection = mongo_db['tb_blog']
    blog_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if blog_result:
        blog_result.pop('_id')
        blog_result['data'] = blog_result['data'][0:10]
        return blog_result['data']
    else:
        raise NotExistException(tag_task_id + '\'s hot_blog')


async def get_relation_graph(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['tag_relation_graph']
    relation_graph_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if relation_graph_result:
        relation_graph_result.pop('_id')
        for node in relation_graph_result['nodes_list']:
            if 'category' in node.keys():
                node.pop('category')
    return relation_graph_result

async def topic_get_relation_graph(topic: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['topic_relation']
    relation_graph_result = await mongo_collection.find_one({'topic': topic})
    if relation_graph_result:
        relation_graph_result.pop('_id')
        for node in relation_graph_result['nodes_list']:
            if 'category' in node.keys():
                node.pop('category')
    return relation_graph_result


async def get_user_mark(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['tag_user']
    user_mark_result = await mongo_collection.find_one({'tag_task_id': tag_task_id})
    if user_mark_result:
        user_mark_result.pop('_id')
    return user_mark_result['data']

async def topic_get_user_mark(topic: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_collection = mongo_db['topic_user']
    user_mark_result = await mongo_collection.find_one({'topic': topic})
    if user_mark_result:
        user_mark_result.pop('_id')
    return user_mark_result['data']


async def delete_task_by_id(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_tag_task_collection = mongo_db['tag_task']
    mongo_character_category_collection = mongo_db['character_category']
    mongo_tag_hot = mongo_db['tag_hot']
    mongo_tag_evolve_collection = mongo_db['tag_evolve']
    mongo_tag_introduce_collection = mongo_db['tag_introduce']
    mongo_tag_relation_collection = mongo_db['tag_relation']
    mongo_tag_weibo_task_collection = mongo_db['tag_weibo_task']
    mongo_tag_word_cloud_collection = mongo_db['tag_word_cloud']
    mongo_tag_user_collection = mongo_db['tag_user']
    mongo_blog_collection = mongo_db['blog']
    task = await mongo_tag_task_collection.find_one({'tag_task_id': tag_task_id})
    if task:
        task.pop('_id')
        try:
            #TODO 修改signal
            celeryapp.control.revoke(task['tag_celery_task_id'], terminate=True, signal=signal.CTRL_C_EVENT)    # 删除后台的一级任务:话题分析任务
            await deleteTask(tag_task_id=tag_task_id, mongo_db=mongo_db)            # 删除后台的二级任务:评论分析任务
            await mongo_character_category_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_user_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_hot.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_evolve_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_introduce_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_relation_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_weibo_task_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_word_cloud_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_blog_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_task_collection.delete_one({'tag_task_id': tag_task_id})
        except Exception as e:
            raise e
        return task
    else:
        raise NotExistException(tag_task_id)

async def delete_task_by_id_wx(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_tag_task_collection = mongo_db['wx_task']
    mongo_tag_word_cloud_collection = mongo_db['wx_word_cloud']
    mongo_tag_introduce_collection = mongo_db['wx_introduce']
    mongo_blog_collection = mongo_db['wx_blog']
    mongo_post_collection = mongo_db['wx_post']
    mongo_user_collection = mongo_db['wx_user']
    mongo_mood_collection = mongo_db['wx_mood']

    task = await mongo_tag_task_collection.find_one({'tag_task_id': tag_task_id})
    if task:
        task.pop('_id')
        try:
            #TODO 修改signal
            celeryapp.control.revoke(task['tag_celery_task_id'], terminate=True, signal=signal.CTRL_C_EVENT)    # 删除后台的一级任务:话题分析任务
            # await deleteTask(tag_task_id=tag_task_id, mongo_db=mongo_db)            # 删除后台的二级任务:评论分析任务
            await mongo_tag_word_cloud_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_task_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_introduce_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_blog_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_post_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_user_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_mood_collection.delete_one({'tag_task_id': tag_task_id})
        except Exception as e:
            raise e
        return task
    else:
        raise NotExistException(tag_task_id)


async def delete_task_by_id_rm(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_tag_task_collection = mongo_db['rm_task']
    mongo_tag_word_cloud_collection = mongo_db['rm_word_cloud']
    mongo_tag_introduce_collection = mongo_db['rm_introduce']
    mongo_blog_collection = mongo_db['rm_blog']
    mongo_post_collection = mongo_db['rm_post']
    mongo_mood_collection = mongo_db['rm_mood']
    mongo_origin_collection = mongo_db['rm_origin']

    task = await mongo_tag_task_collection.find_one({'tag_task_id': tag_task_id})
    if task:
        task.pop('_id')
        try:
            #TODO 修改signal
            celeryapp.control.revoke(task['tag_celery_task_id'], terminate=True, signal=signal.CTRL_C_EVENT)    # 删除后台的一级任务:话题分析任务
            # await deleteTask(tag_task_id=tag_task_id, mongo_db=mongo_db)            # 删除后台的二级任务:评论分析任务
            await mongo_tag_word_cloud_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_task_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_introduce_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_blog_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_post_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_mood_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_origin_collection.delete_one({'tag_task_id': tag_task_id})
        except Exception as e:
            raise e
        return task
    else:
        raise NotExistException(tag_task_id)


async def delete_task_by_id_tb(tag_task_id: str, mongo_db: AsyncIOMotorDatabase) -> dict:
    mongo_tag_task_collection = mongo_db['tb_task']
    mongo_tag_word_cloud_collection = mongo_db['tb_word_cloud']
    mongo_tag_introduce_collection = mongo_db['tb_introduce']
    mongo_blog_collection = mongo_db['tb_blog']
    mongo_post_collection = mongo_db['tb_post']
    mongo_mood_collection = mongo_db['tb_mood']

    task = await mongo_tag_task_collection.find_one({'tag_task_id': tag_task_id})
    if task:
        task.pop('_id')
        try:
            #TODO 修改signal
            celeryapp.control.revoke(task['tag_celery_task_id'], terminate=True, signal=signal.CTRL_C_EVENT)    # 删除后台的一级任务:话题分析任务
            await deleteTask_tb(tag_task_id=tag_task_id, mongo_db=mongo_db)            # 删除后台的二级任务:评论分析任务
            await mongo_tag_word_cloud_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_task_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_tag_introduce_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_blog_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_post_collection.delete_one({'tag_task_id': tag_task_id})
            await mongo_mood_collection.delete_one({'tag_task_id': tag_task_id})


        except Exception as e:
            raise e
        return task
    else:
        raise NotExistException(tag_task_id)