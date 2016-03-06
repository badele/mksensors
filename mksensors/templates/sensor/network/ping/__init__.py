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
import logging
from copy import deepcopy

from mksensors.lib import mks
from mksensors.lib.mks.plugins import SensorPlugin
from mksensors.lib.sensor.network import ping

_LOGGER = logging.getLogger('network.isup')


class Sensor(SensorPlugin):
    def getSensortype(self):
        return 'network.netping'

    def getDescription(self):
        return 'Return ping result'

    def checkRequirements(self):
        ping.checkRequirements()

    def __init__(self):
        """Init Sensor class"""
        super(Sensor, self).__init__(_LOGGER)
        self.hostnames = []

        sensorname = self.sensorname
        self.logger.debug('Init %(sensorname)s sensor object' % locals())


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

                fullname = '.'.join(dsnames)
                self.logger.debug('Add %(fullname)s datasource' % locals())

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

        self.logger.debug('Start the sensor')
        while True:
            # Ping for all hostnames
            for hostname in hostnames:
                self.logger.debug('Ping %(hostname)s' % locals())

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

                avg_rtt = result['avg_rtt']
                self.logger.debug('ping result for %(hostname)s => %(avg_rtt)s ms' % locals())

                self.sendValues(values)

            # Sleep
            stepinterval = int(self.mksconfig.get('stepinterval', 15))
            self.flushMessages()
            self.logger.debug('Sleep for %(stepinterval)s seconds' % locals())
            time.sleep(stepinterval)

if __name__ == '__main__':
    sensor = Sensor()
    sensor.initSensor()
    sensor.startSensor()
