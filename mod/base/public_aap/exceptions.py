# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------

# 异常类

# 提示类异常 会正常响应
class HintException(Exception):
    pass


# 无授权异常
class NoAuthorizationException(HintException):
    pass


# 面板错误异常
class PanelError(Exception):
    '''
        @name 面板通用异常对像
        @author MissChina<2021-06-25>
    '''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return ("An error occurred while the panel was running: {}".format(str(self.value)))
