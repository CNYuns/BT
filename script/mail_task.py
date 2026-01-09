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
sys.path.insert(0,"/www/server/panel/class/")
try:
    import send_to_user
    msg=send_to_user.send_to_user()
    msg.main()
except:
    pass