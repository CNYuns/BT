# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------
import os,sys,re,json,shutil,psutil,time
from panelModel.base import panelBase
import public,psutil

class main(panelBase):

    def __init__(self):
        super().__init__()

    def get_disk_usage(self,get):
        """
            @name 获取目录可用空间
        """
        path = get.path
        if not os.path.exists(path):
            return public.returnMsg(False,'指定目录不存在.')

        res = psutil.disk_usage(path)
        return res

    def get_dir_used(self,get):

        """
            @name 获取目录已用空间
        """
        path = get.path
        if not os.path.exists(path):
            return public.returnMsg(False,'指定目录不存在.')

        res = public.get_size_total([path])
        if path in res:
            return res[path]
        return False







