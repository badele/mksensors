#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
--param="'hostnames': ['8.8.8.8', '8.8.4.4']"
--param="'hostnames': ['8.8.8.8', '8.8.4.4'], 'pause': 10"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import time
from copy import deepcopy

from mksensors.lib import mks
from mksensors.lib.mks.plugins import SensorPlugin
from mksensors.lib.sensor.network import ping


class Sensor(SensorPlugin):

    def getSensortype(self):
        return 'network.isup'

    def getDescription(self):
        return 'Return if the hosts are online'

    def checkRequirements(self):
        ping.checkRequirements()

    def __init__(self):
        """Init Sensor class"""
        super(Sensor, self).__init__()
        self.hostnames = []

    def initSensor(self):
        """Init the Sensor object parameters"""
        super(Sensor, self).initSensor()

        # Get hostnames list
        hostnames = self.config.get('hostnames', [])

        # Set datasource list
        datasources = []
        for hostname in hostnames:
            dsnames = (hostname, 'isup')
            datasources.append(dsnames)

        self.senders = mks.getEnabledSenderObjects(self.sensorname, datasources)


    def startSensor(self):
        # Get hostnames list
        hostnames = self.config.get('hostnames', [])

        while True:
            # Ping for all hostnames
            for hostname in hostnames:

                # Test connexion
                rping = ping.ping(destination=hostname)
                rping.run()
                result = deepcopy(rping.results)
                result['sensorname'] = self.sensorname
                result['hostname'] = hostname.replace('.', '_')

                # return value
                values = []
                datasource = (hostname, 'isup')
                value = result['result']
                values.append((datasource, value, mks.getTimestamp()))

                self.sendValues(values)

            # Sleep
            self.flushMessages()
            time.sleep(self.config.get('pause', 15))


if __name__ == '__main__':
    sensor = Sensor()
    sensor.initSensor()
    sensor.startSensor()
