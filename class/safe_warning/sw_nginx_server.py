# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------

import re, public, os
_title = 'Nginx 版本泄露'
_version = 1.0  # 版本
_ps = "Nginx 版本泄露"  # 描述
_level = 2  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2022-8-10'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_nginx_server.pl")
_tips = [
    "在【/www/server/nginx/conf/nginx.conf】文件中设置server_tokens off;",
    "提示：server_tokens off;"
]
_help = ''
_remind = '此方案加强了服务器防护，降低网站被入侵的风险。'

def check_run():
    '''
        @name 检测nginx版本泄露
        @author MissChina
        @return tuple (status<bool>,msg<string>)
    '''

    if os.path.exists('/www/server/nginx/conf/nginx.conf'):
        try:
            info_data = public.ReadFile('/www/server/nginx/conf/nginx.conf')
            if info_data:
                if re.search('server_tokens off;', info_data):
                    return True, '无风险'
                else:
                    return False, '当前Nginx存在版本泄露请在Nginx配置文件中添加或者修改参数server_tokens 为off;，例：server_tokens off;'
        except:
            return True, '无风险'
    return True, '无风险'
