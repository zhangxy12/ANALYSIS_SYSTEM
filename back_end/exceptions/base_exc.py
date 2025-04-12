"""
:
"""


class CustomBaseException(Exception):
    """自定义异常基类"""
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__()
