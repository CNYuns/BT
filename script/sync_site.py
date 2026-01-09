# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------
import sys

sys.path.insert(0, "/www/server/panel/class/")
import PluginLoader
print("开始执行同步站点任务...")
syncsite = PluginLoader.module_run("syncsite", "run_task",{})
print(syncsite)
print("同步站点任务执行完毕!")