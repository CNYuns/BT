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
import os
import traceback

os.chdir('/www/server/panel/')
sys.path.insert(0, "/www/server/panel/class/")
sys.path.insert(0, "/www/server/panel/")

try:
    from mod.project.node.filetransfer import run_file_transfer_task
    run_file_transfer_task(int(sys.argv[1]))
except:
    traceback.print_exc()
    with open('/tmp/node_file_transfer.pl', 'w') as f:
        f.write(traceback.format_exc())
