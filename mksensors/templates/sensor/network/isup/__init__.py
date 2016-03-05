#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hostnames:
  - 8.8.8.8
  - 8.8.4.4

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
        return 'network.isup'

    def getDescription(self):
        return 'Return if the hosts are online'

    def checkRequirements(self):
        ping.checkRequirements()

    def __init__(self):
        """Init Sensor class"""
        super(Sensor, self).__init__(_LOGGER)
        self.hostnames = []

        sensorname = self.sensorname
        self.logger.info('Init %(sensorname)s sensor object' % locals())

    def initSensor(self):
        """Init the Sensor object parameters"""
        super(Sensor, self).initSensor()

        # Get hostnames list
        self.hostnames = self.config.get('hostnames', [])

        # Set datasource list
        datasources = []
        for hostname in self.hostnames:
            dsnames = (hostname, 'isup')
            datasources.append(dsnames)
            self.logger.info('Add %(hostname)s to check' % locals())

        self.senders = mks.getEnabledSenderObjects(self.sensorname, datasources)


    def startSensor(self):
        # Get hostnames list
        self.logger.info('Start the sensor')
        while True:
            # Ping for all hostnames
            for hostname in self.hostnames:

                self.logger.info('Check if the %(hostname)s is up' % locals())

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

                isup = 'Yes' if value == 255 else 'No'
                self.logger.info('The %(hostname)s is up => %(isup)s' % locals())

                self.sendValues(values)

            # Sleep
            self.flushMessages()
            time.sleep(self.mksconfig.get('stepinterval', 15))


if __name__ == '__main__':
    sensor = Sensor()
    sensor.initSensor()
    sensor.startSensor()
