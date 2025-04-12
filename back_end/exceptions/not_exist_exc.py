"""
:不存在异常

"""
from .base_exc import CustomBaseException


class NotExistException(CustomBaseException):
    def __init__(self, msg: str = ''):
        super().__init__('ERROR: '+msg+' NOT EXISTED!')
