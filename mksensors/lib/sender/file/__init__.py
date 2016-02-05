#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mksensors sender new sender.file --param="'location': '/opt/mksensors/datas/file'"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import os
from mksensors.lib import mks
from mksensors.lib.mks.plugins import SenderPlugin


class Sender(SenderPlugin):
    def __init__(self):
        """Init sender class"""
        super(Sender, self).__init__()
        self.sendertype = 'file'
        self.config = mks.loadSenderConfig(self.sendertype)

        # Init variable
        self._files = {}

    def getDescription(self):
        return "Write sensors values in the file"

    def initSender(self, sensorname, datasources):
        """Init the sender object parameters"""
        super(Sender, self).initSender(sensorname, datasources)

        if 'location' not in self.config:
            raise Exception("Location is not define")

        # Check folder
        location = self.config['location']
        if not os.path.isdir(location):
            os.makedirs(location)

        sensorname = self.sensorname
        for datasource in self.datasources:
            dsname = mks.datasource2String(datasource, '.')
            logfilename = '%(location)s/%(sensorname)s%(dsname)s.log' % locals()
            self._files[datasource] = open(logfilename, "a")

    def sendValues(self, sensorname, items):

        for item in items:
            (datasource, value, ts) = item
            content = "%(ts)s %(value)s\n" % locals()
            self._files[datasource].write(content)
        self._files[datasource].flush()
