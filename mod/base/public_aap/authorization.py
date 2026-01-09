# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------

# 授权检测帮助模块
# 已修改为本地永久授权模式


from functools import wraps
from public.exceptions import NoAuthorizationException


# 专业版用户限定装饰器 - 已修改为始终通过
def only_pro_members(func: callable) -> callable:
    @wraps(func)
    def _wrap_func(*args, **kwargs):
        # 已修改: 始终允许访问，跳过授权检查
        return func(*args, **kwargs)

    return _wrap_func
