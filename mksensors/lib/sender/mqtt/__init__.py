#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mksensors sender new sender.mqtt --param="'broker': 'mqtt.hostname.com','topic': 'mksensors'"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__commitnumber__ = "$id$"

import logging

from mksensors.lib import mks
from mksensors.lib.mks.plugins import SenderPlugin

DAY = 86400
WEEK = DAY * 7
MONTH = DAY * 31
YEAR = DAY * 365

_LOGGER = logging.getLogger(__name__)
mks.init_logging(logger=_LOGGER, loglevel=mks.LOGSEVERITY['DEBUG'])


class Sender(SenderPlugin):
    def __init__(self):
        try:
            super(Sender, self).__init__('mqtt', _LOGGER)
            self.mymqtt = __import__('paho.mqtt.client')
            self.mqttc = None
        except:
            _LOGGER.exception('SenderPlugin Init error')
            raise

    def getDescription(self):
        return "Send sensors values to Mqtt broker"


    def initSender(self, sensorname, datasources):
        super(Sender, self).initSender(sensorname, datasources)

        self.mqttc = self.mymqtt.mqtt.client.Client()
        self.mqttc.connect(self.config['broker'])
        self.mqttc.loop_start()

        self.logger.debug('Sender is initialized')

    def sendValues(self, sensorname, items):

        topic = self.config['topic']
        for item in items:
            (datasource, value, ts) = item

            if value is not None:
                dsname = mks.datasource2String(datasource, '/')
                fulltopicname = "%(topic)s/%(sensorname)s.%(dsname)s" % locals()
                self.mqttc.publish(fulltopicname, value)

    def checkRequirements(self):
        # Check
        packages = ['paho-mqtt==1.1']
        mks.checkOrInstallPackages(packages)
