#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hostnames:
  - 8.8.8.8
  - 8.8.4.4
datasources:
  - max_rtt
  - min_rtt
  - avg_rtt
  - packet_lost
  - packet_size
  - timeout
  - result
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__commitnumber__ = "$id$"

import time
from copy import deepcopy

from mksensors.lib import mks
from mksensors.lib.mks.plugins import SensorPlugin
from mksensors.lib.sensor.network import ping


class Sensor(SensorPlugin):
    def getSensortype(self):
        return 'network.netping'

    def getDescription(self):
        return 'Return ping result'

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
        self.filtered_ds = self.config.get(
            'datasources', [
                'max_rtt', 'min_rtt', 'avg_rtt', 'packet_lost',
                'packet_size', 'timeout', 'result',
            ]
        )


        # Set datasource list
        datasources = []
        for hostname in hostnames:
            for filtered in self.filtered_ds:
                dsnames = (hostname, filtered)
                datasources.append(dsnames)

        self.senders = mks.getEnabledSenderObjects(self.sensorname, datasources)


    def startSensor(self):

        # Set default parameters
        hostnames = self.config.get('hostnames', [])

        # Set datasource list
        datasources = []
        for hostname in hostnames:
            for filtered in self.filtered_ds:
                dsnames = (hostname, filtered)
                datasources.append(dsnames)

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
                for filtered in self.filtered_ds:
                    datasource = (hostname, filtered)
                    value = result[filtered]
                    values.append((datasource, value, mks.getTimestamp()))

                self.sendValues(values)

            # Sleep
            self.flushMessages()
            time.sleep(self.mksconfig.get('stepinterval', '15'))

if __name__ == '__main__':
    sensor = Sensor()
    sensor.initSensor()
    sensor.startSensor()
