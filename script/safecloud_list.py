# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------
import os,sys
# 作为面板task，定时执行
os.chdir('/www/server/panel')
sys.path.insert(0,'class/')
import PluginLoader,public,json
args = public.dict_obj()
args.model_index = 'project'
# 调用云查杀接口
res = PluginLoader.module_run('safecloud', 'webshell_detection', args)
print(json.dumps(res))
