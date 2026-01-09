# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------
import os, sys, time, json

panelPath = '/www/server/panel'
os.chdir(panelPath)
if not panelPath + "/class/" in sys.path:
    sys.path.insert(0, panelPath + "/class/")
import public, re


class virtualBase:

    def __init__(self):
        pass