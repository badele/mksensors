#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mksensors plugins
"""

import re
import sys
import traceback

from mksensors.lib import mks

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'


class SenderPlugin(object):
    def __init__(self):
        self.sendertype = None

    def getDescription(self):
        sendertype = self.sendertype
        raise Exception('Please define getDescription in %(sendertype)s class' % locals())

    def initSender(self, sensorname, datasources):
        self.sensorname = sensorname
        self.datasources = datasources

        # Check sender configuration
        sendertype = self.sendertype
        errors = self.checkConfiguration()
        if errors:
            errormess = "Cannot init %(sendertype)s sender:\n" % locals()
            for error in errors:
                errormess += " - %(error)s\n" % locals()

            raise Exception(errormess)

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
        errors = []
        for paramname in self.config:
            value = self.config[paramname]
            if isinstance(value, str):
                m = re.match(r'<SAMPLE>.*</SAMPLE>', value)
                if m:
                    errors.append("please define '%(paramname)s' in %(configfilename)s" % locals())

        return errors


class SensorPlugin(object):
    def __init__(self):
        self.sensorname = mks.getSensorName()
        self.config = mks.loadSensorConfig(self.sensorname)
        self.senders = []

    def initSensor(self):
        pass

    def flushMessages(self):
        sys.stdout.flush()
        sys.stderr.flush()

    def getSensortype(self):
        raise Exception('Please define in your class')

    def getDescription(self):
        raise Exception('Please define in your class')

    def getConfigFilename(self):
        """Get Sender YAML configuration"""
        confdir = mks.CONFDIR
        sensortype = self.getSensortype()
        return '%(confdir)s/sensor_%(sensortype)s.yml' % locals()

    def checkRequirements(self):
        if not self.getSensortype():
            raise Exception('sensortype is not defined')

    def checkConfiguration(self):
        """Check sensor configuration"""
        if not self.getSensortype():
            raise Exception('sensortype is not defined')

        # Check if required parameters is set"
        configfilename = self.getConfigFilename()
        for paramname in self.config:
            value = self.config[paramname]
            if isinstance(value, str):
                m = re.match(r'<SAMPLE>.*</SAMPLE>', value)
                if m:
                    print "Please define '%(paramname)s' in %(configfilename)s" % locals()

    def sendValues(self, values):

        for sender in self.senders:
            try:
                sender.sendValues(self.sensorname, values)
            except Exception as e:
                # Todo: log in mksensors.log
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print repr(traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout))
