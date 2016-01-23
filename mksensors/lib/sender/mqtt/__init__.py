#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mksensors sender new sender.mqtt --param="'broker': 'mqtt.hostname.com','topic': 'mksensors'"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import os
import sys

from distutils.spawn import find_executable

from mksensors.lib import mks

DAY = 86400
WEEK = DAY * 7
MONTH = DAY * 31
YEAR = DAY * 365

def checkRequirements():
    # Check
    packages = ['paho-mqtt==1.1']
    mks.checkOrInstallPackages(packages)



class Sender(object):
    def __init__(self, sensorname, datasources, conf):
        self.mymqtt = __import__('paho.mqtt.client')

        self.sensorname = sensorname
        self.datasources = datasources
        self.conf = conf.get('sender.mqtt', {})
        self.mqtt = None

    def initSender(self):

        if 'broker' not in self.conf:
            raise Exception("Broker is not define")

        if 'topic' not in self.conf:
            raise Exception("Topic is not define")

        self.mqttc = self.mymqtt.mqtt.client.Client()
        self.mqttc.connect(self.conf['broker'])
        self.mqttc.loop_start()


    def sendValues(self, sensorname, items):

        topic = self.conf['topic']
        for item in items:
            (datasource, value, ts) = item

            if value is not None:
                dsname = mks.datasource2String(datasource, '/')
                fulltopicname = "%(topic)s/%(sensorname)s%(dsname)s" % locals()
                print fulltopicname
                self.mqttc.publish(fulltopicname, value)