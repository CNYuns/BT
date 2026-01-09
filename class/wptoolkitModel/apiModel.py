# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------

import json
import os
from types import MethodType

from wptoolkitModel.base import wpbase
import requests
import panelSite
import public_wp as public
from wptoolkitModel.toolkitModel import toolkitModel
from flask import request

class main(wpbase):
    def __init__(self, get=None):
        super(main, self).__init__(get)

    def test(self, get):
        query = request.args
        if not query.get("model") or not query.get("action"):
            return public.returnMsg(False, "参数错误")
        model = "{}Model".format(query['model'])
        action = query['action']
        cls = globals()[model]
        get = public.to_dict_obj(vars(get))
        method = getattr(cls(), action)
        return method(get)

