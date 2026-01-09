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

if '/www/server/panel/class' not in sys.path:
    sys.path.append("/www/server/panel/class")
import PluginLoader
import public

if __name__ == '__main__':
    args = public.dict_obj()
    args.model_index = 'monitor'
    res = PluginLoader.module_run("sitelogpush", "run", args)
