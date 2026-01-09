# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------
import sys, os

os.chdir('/www/server/panel/')
sys.path.insert(0, "class/")
import PluginLoader
import public
import time


def clear_hosts():
    """
    @name 清理hosts文件中的bt.cn记录（已禁用）
    @return:
    """
    # 禁用hosts清理功能
    pass


def flush_cache():
    '''
        @name 更新缓存（已禁用远程获取）
        @author MissChina
        @return void
    '''
    try:
        # 禁用从远程服务器获取数据
        # 仅调用本地 PluginLoader
        res = PluginLoader.get_plugin_list(1)
        # 禁用远程下载 pay_type.json
        # 禁用远程部署列表获取
    except:
        pass


def flush_php_order_cache():
    """
    更新软件商店php顺序缓存（已禁用）
    @return:
    """
    # 禁用远程下载
    pass


def flush_msg_json():
    """
    @name 更新消息json（已禁用）
    """
    # 禁用远程下载
    pass


if __name__ == '__main__':
    tip_date_tie = '/tmp/.fluah_time'
    if os.path.exists(tip_date_tie):
        last_time = int(public.readFile(tip_date_tie))
        timeout = time.time() - last_time
        if timeout < 600:
            print("执行间隔过短，退出 - {}!".format(timeout))
            sys.exit()
    # 禁用远程检查
    # clear_hosts()
    flush_cache()
    # flush_php_order_cache()
    # flush_msg_json()

    public.writeFile(tip_date_tie, str(int(time.time())))
