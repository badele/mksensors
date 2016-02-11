#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mksensors sender new sender.log --param="'location': '/opt/mksensors/datas/log'"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__commitnumber__ = "$id$"

import os

from mksensors.lib import mks
from mksensors.lib.mks.plugins import SenderPlugin


class Sender(SenderPlugin):
    def __init__(self):
        """Init sender class"""
        super(Sender, self).__init__()
        self.sendertype = 'log'
        self.config = mks.loadSenderConfig(self.sendertype)

        # Init variable
        self._file = None

    def getDescription(self):
        return "Write sensors values in one log file"


    def initSender(self, sensorname, datasources):
        """Init the sender object parameters"""
        super(Sender, self).initSender(sensorname, datasources)

        if 'location' not in self.config:
            raise Exception("Location is not define")

        # Check folder
        location = self.config['location']
        if not os.path.isdir(location):
            os.makedirs(location)

        # Init log file
        logfilename = '%(location)s/sender.log' % locals()
        self._file = open(logfilename, "a")

    def sendValues(self, sensorname, items):
        """Send value to the sender storage"""
        for item in items:
            (datasource, value, ts) = item
            dsname = mks.datasource2String(datasource, '.')
            content = "%(ts)s %(sensorname)s.%(dsname)s %(value)s\n" % locals()
            self._file.write(content)
        self._file.flush()