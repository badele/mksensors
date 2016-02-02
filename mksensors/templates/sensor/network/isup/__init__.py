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
    def __init__(self):
        """Init Sensor class"""
        super(Sensor, self).__init__()
        self.sensortype = 'network.isup'

        self.sensorname = mks.getSensorName()
        self.config = mks.loadSensorConfig(self.sensorname)


    def initSensor(self):
        """Init the Sensor object parameters"""
        super(Sensor, self).initSensor()


    def sendValues(self, sensorname, items):
        """Send value to the sender storage"""
        for item in items:
            (datasource, value, ts) = item
            dsname = mks.datasource2String(datasource, '.')
            content = "%(ts)s %(sensorname)s%(dsname)s %(value)s\n" % locals()
            self._file.write(content)
        self._file.flush()

    def checkRequirements(self):
        ping.checkRequirements()


if __name__ == '__main__':
    params = mks.loadSensorConfig()
    sensorname = mks.getSensorName()

    # Set default parameters
    hostnames = params.get('hostnames', [])

    # Set datasource list
    datasources = []
    for hostname in hostnames:
        dsnames = (hostname, 'isup')
        datasources.append(dsnames)

    senders = mks.getEnabledSenderObjects(sensorname, datasources)

    while True:
        # Ping for all hostnames
        for hostname in hostnames:
            # Test connexion
            rping = ping.ping(destination=hostname, **params)
            rping.run()
            result = deepcopy(rping.results)
            result['sensorname'] = sensorname
            result['hostname'] = hostname.replace('.', '_')

            # return value
            values = []
            datasource = (hostname, 'isup')
            value = result['result']
            values.append((datasource, value, mks.getTimestamp()))

            mks.sendValues(senders, sensorname, values)

        # Sleep
        time.sleep(params['pause'])
