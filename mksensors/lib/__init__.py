#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import os

SUPERVISOCONF = '/etc/supervisord.d'

def createSupervisorConf(confname, content):

    filename = os.path.join(SUPERVISOCONF, '%s.conf' % confname)
    saveto(filename, content)

def saveto(filename, content):
    out = open(filename, 'wb')
    out.write(content)
    out.close()