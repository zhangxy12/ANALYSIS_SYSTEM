"""
:配置类

"""
from pydantic import BaseSettings


class CeleryConfig(BaseSettings):
    """
    celery 启动的相关配置
    """
    BROKER = 'redis://localhost:6379/0'
    BACKEND = 'redis://localhost:6379/1'


class MongoConfig(BaseSettings):
    """
    Mongo的相关配置
    """
    HOST: str = '127.0.0.1'
    PORT: int = 27017
    DB_NAME: str = 'test'
    #总的
    SEARCH_RES: str = 'search_res'
    SEARCH_HISTORY: str = 'search_history'
    TOPIC_CONTENT: str = 'topic_content'
    TOPIC_USER: str = 'topic_user'
    TOPIC_CHARACTER: str = 'topic_character'
    TOPIC_RELATION: str = 'topic_relation'
    # 大屏
    ALL_CONTENT: str = 'all_content'
    ALL_COMMENT: str = 'all_comment'
    ALL_COMMENT_IP: str = 'all_comment_ip'

    # 话题任务数据库名称
    # 微博
    TASK: str = 'tag_task'
    BLOG: str = 'blog'
    CHARACTER: str = 'character_category'
    EVOLVE: str = 'tag_evolve'
    HOT: str = 'tag_hot'
    INTRODUCE: str = 'tag_introduce'
    RELATION: str = 'tag_relation_graph'
    RETWEET: str = 'tag_weibo_task'
    CLOUD: str = 'tag_word_cloud'
    USER: str = 'tag_user'

    # 微信
    WX_TASK: str = 'wx_task'
    WX_BLOG: str = 'wx_blog'
    WX_INTRODUCE: str = 'wx_introduce'
    WX_CLOUD: str = 'wx_word_cloud'
    WX_POST: str = 'wx_post'
    WX_MOOD: str = 'wx_mood'
    WX_USER: str = 'wx_user'

    # 人民网
    RM_TASK: str = 'rm_task'
    RM_BLOG: str = 'rm_blog'
    RM_INTRODUCE: str = 'rm_introduce'
    RM_CLOUD: str = 'rm_word_cloud'
    RM_POST: str = 'rm_post'
    RM_MOOD: str = 'rm_mood'
    RM_ORIGIN: str = 'rm_origin'

    # 贴吧
    TB_TASK: str = 'tb_task'
    TB_BLOG: str = 'tb_blog'
    TB_INTRODUCE: str = 'tb_introduce'
    TB_CLOUD: str = 'tb_word_cloud'
    TB_POST: str = 'tb_post'
    TB_MOOD: str = 'tb_mood'


    # 微博评论任务数据库名称
    COMMENT_TASK = 'comment_task'
    COMMENT_REPOSTS = 'comment_reposts'
    COMMENT_CLOUD = 'comment_cloud'
    COMMENT_CLUSTER = 'comment_cluster'
    COMMENT_NODE = 'comment_node'
    COMMENT_TENDENCY = 'comment_tendency'
    COMMENT_TOPIC = 'comment_topic'
    COMMENT_TREE = 'comment_tree'

    # 贴吧评论任务数据库名称
    TB_COMMENT_TASK = 'tb_comment_task'
    TB_COMMENT_REPOSTS = 'tb_comment_reposts'
    TB_COMMENT_CLOUD = 'tb_comment_cloud'
    TB_COMMENT_IP = 'tb_comment_ip'
    TB_COMMENT_MOOD = 'tb_comment_mood'
    TB_COMMENT_TENDENCY = 'tb_comment_tendency'
    TB_COMMENT_TOPIC = 'tb_comment_topic'
    TB_COMMENT_TREE = 'tb_comment_tree'

    #用户注册登录数据库
    USER = 'user'
    # 谣言
    RUMOR_ANA: str = 'rumor_ana'
    #人民网数据库
    NEWS = 'news'


class ElasticSearchConfig(BaseSettings):
    """
    ES配置
    """
    ES_HOST = '127.0.0.1:9200'
    ES_SEARCH_INDEX = 'weibo'
    ES_TIMEOUT = 60
    LANG_TYPE = ['zh', 'en']
