"""
:配置实体

"""
from .task_config_class import (
    MongoConfig,
    CeleryConfig,
    ElasticSearchConfig
)

mongo_conf = MongoConfig()
celery_conf = CeleryConfig()
es_conf = ElasticSearchConfig()
