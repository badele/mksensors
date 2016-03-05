#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mksensors plugins
"""

import re
import sys
import logging

from mksensors.lib import mks

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__commitnumber__ = "$id$"

_LOGGER = logging.getLogger(__name__)
mks.init_logging(logger=_LOGGER, loglevel=mks.LOGSEVERITY['DEBUG'])

class SenderPlugin(object):
    def __init__(self, sendertype, logger):
        try:
            self.sendertype = sendertype
            self.logger = logger
            self.config = mks.loadSenderConfig(self.sendertype)
            self.mksconfig = mks.loadMkSensorsConfig()

            # Init log
            loglevel = mks.LOGSEVERITY[self.mksconfig.get('loglevel', 'WARNING')]
            mks.init_logging(self.logger, loglevel=loglevel)

        except:
            _LOGGER.exception('SenderPlugin Init error')
            raise

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
            self.logger.error('Sender configuration error for %(sensorname)s' % locals())
            errormess = "Cannot init %(sendertype)s sender:\n" % locals()
            for error in errors:
                errormess += " - %(error)s\n" % locals()
                self.logger.error(' - %(error)s' % locals())

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
    def __init__(self, logger):
        try:
            self.logger = logger
            self.sensorname = mks.getSensorName()
            self.config = mks.loadSensorConfig(self.sensorname)
            self.mksconfig = mks.loadMkSensorsConfig()
            self.senders = []
        except:
            self.logger.exception('SenderPlugin Init error')
            raise

    def initSensor(self):
        sensorname = self.sensorname
        logname = 'sensor_%(sensorname)s' % locals()
        loglevel = mks.LOGSEVERITY[self.mksconfig.get('loglevel', 'WARNING')]
        mks.init_logging(self.logger, loglevel=loglevel)

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
            sender.sendValues(self.sensorname, values)
