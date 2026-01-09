# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------

import collections

# Common structures
aap_t_simple_result = collections.namedtuple('aap_t_simple_result', ['success', 'msg'])
aap_t_mysql_dump_info = collections.namedtuple('aap_t_mysql_dump_info', ['db_name', 'file', 'dump_time'])
aap_t_http_multipart = collections.namedtuple('aap_t_http_multipart', ['headers', 'body'])
