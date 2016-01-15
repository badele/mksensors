#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import time


if __name__ == '__main__':
    while True:

        # Check internet connexion
        pping = ping(destination="8.8.8.8", count=1)
        # Use sender

        #Sleep
        time.sleep(0.5)
