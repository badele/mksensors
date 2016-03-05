#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mksensors sender new sender.file --param="'location': '/opt/mksensors/datas/file'"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__commitnumber__ = "$id$"

import os
import logging

from mksensors.lib import mks
from mksensors.lib.mks.plugins import SenderPlugin

_LOGGER = logging.getLogger(__name__)
mks.init_logging(logger=_LOGGER, loglevel=mks.LOGSEVERITY['DEBUG'])


class Sender(SenderPlugin):
    def __init__(self):
        """Init sender class"""
        try:
            super(Sender, self).__init__('file', _LOGGER)
        except:
            _LOGGER.exception('SenderPlugin Init error')
            raise

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
        foldername = '%(location)s/%(sensorname)s/' % locals()
        if not os.path.isdir(foldername):
            os.makedirs(foldername)

        # Open files
        sensorname = self.sensorname
        for datasource in datasources:
            dsname = mks.datasource2String(datasource, '.')
            print dsname
            logfilename = '%(location)s/%(sensorname)s/%(dsname)s.txt' % locals()
            self._files[dsname] = open(logfilename, "a")

        self.logger.debug('Sender is initialized')

    def sendValues(self, sensorname, items):

        for item in items:
            (datasource, value, ts) = item
            dsname = mks.datasource2String(datasource, '.')
            content = "%(ts)s %(dsname)s %(value)s\n" % locals()
            self._files[dsname].write(content)
            self._files[dsname].flush()
