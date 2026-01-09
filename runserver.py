#coding: utf-8
# +-------------------------------------------------------------------
# | BT Panel
# +-------------------------------------------------------------------
# | Copyright (c) 2015-present MissChina. All rights reserved.
# +-------------------------------------------------------------------
# | Author: MissChina
# | License: Proprietary
# +-------------------------------------------------------------------
from os import environ
from BTPanel import app,sys

if __name__ == '__main__':
    f = open('data/port.pl')
    PORT = int(f.read())
    HOST = '0.0.0.0'
    f.close()
    app.run(host=HOST,port=PORT)
