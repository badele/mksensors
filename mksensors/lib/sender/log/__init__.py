#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mksensors sender new sender.log --param="'location': '/opt/mksensors/datas/log'"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import os

from mksensors.lib import mks


def checkRequirements():
   pass

class Sender(object):
    def __init__(self, sensorname, datasources, conf):
        self.sensorname = sensorname
        self.datasources = datasources
        self.conf = conf.get('sender.log', {})
        self._file = None


    def initSender(self):

        if 'location' not in self.conf:
            raise Exception("Location is not define")

        # Check folder
        location = self.conf['location']
        if not os.path.isdir(location):
            os.makedirs(location)

        # Init log file
        logfilename = '%(location)s/sender.log' % locals()
        self._file = open(logfilename, "a")


    def sendValues(self, sensorname, items):
        for item in items:
            (datasource, value, ts) = item
            dsname = mks.datasource2String(datasource, '.')
            content = "%(ts)s %(sensorname)s%(dsname)s %(value)s\n" % locals()
            self._file.write(content)
        self._file.flush()
