# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------
import sys,os
os.chdir('/www/server/panel/')
sys.path.insert(0,"class/")
import PluginLoader
cid = sys.argv[-1]
PluginLoader.get_soft_list(cid)