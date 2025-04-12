"""
:

"""
from .base_exc import CustomBaseException


class TokenException(CustomBaseException):
    """Token异常处理类"""
    def __init__(self, msg: str = ''):
        super().__init__('Token is invalid' + msg)
