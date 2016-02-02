#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mksensors plugins
"""

import re

from mksensors.lib import mks

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

class SenderPlugin(object):
    def __init__(self):
        self.sendertype = None

    def initSender(self, sensorname, datasources):
        self.sensorname = sensorname
        self.datasources = datasources


    def getConfigFilename(self):
        """Get Sender YAML configuration"""
        confdir = mks.CONFDIR
        sendertype = self.sendertype
        return '%(confdir)s/sender_%(sendertype)s.yml' % locals()


    def checkRequirements(self):
        if not self.sendertype:
            raise Exception('sendertype is not defined')


    def checkConfiguration(self):
        """Check sender configuration"""
        if not self.sendertype:
            raise Exception('sendertype is not defined')

        # Check if required parameters is set"
        configfilename = self.getConfigFilename()
        for paramname in self.config:
            value = self.config[paramname]
            if isinstance(value, str):
                m = re.match(r'<SAMPLE>.*</SAMPLE>', value)
                if m:
                    print "'%(paramname)s' not defined in %(configfilename)s" % locals()


class SensorPlugin(object):
    def __init__(self):
        self.sendertype = None

    def initSender(self, sensorname, datasources):
        self.sensorname = sensorname
        self.datasources = datasources


    def getConfigFilename(self):
        """Get Sender YAML configuration"""
        confdir = mks.CONFDIR
        sendertype = self.sendertype
        return '%(confdir)s/sender_%(sendertype)s.yml' % locals()


    def checkRequirements(self):
        if not self.sendertype:
            raise Exception('sendertype is not defined')


    def checkConfiguration(self):
        """Check sender configuration"""
        if not self.sendertype:
            raise Exception('sendertype is not defined')

        # Check if required parameters is set"
        configfilename = self.getConfigFilename()
        for paramname in self.config:
            value = self.config[paramname]
            if isinstance(value, str):
                m = re.match(r'<SAMPLE>.*</SAMPLE>', value)
                if m:
                    print "'%(paramname)s' not defined in %(configfilename)s" % locals()
