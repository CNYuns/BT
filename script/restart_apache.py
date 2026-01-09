# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------
import os
import subprocess

def check_mysql_status():
    result = subprocess.run(['/etc/init.d/httpd', 'status'], stdout=subprocess.PIPE)
    return 'running' in result.stdout.decode('utf-8')

def start_mysql():
    os.system('/etc/init.d/httpd start')


if not check_mysql_status():
    start_mysql()
