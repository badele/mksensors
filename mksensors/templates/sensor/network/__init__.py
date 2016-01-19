#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
--param="'hostnames': ['8.8.8.8', '8.8.4.4']"
--param="'hostnames': ['8.8.8.8', '8.8.4.4'], 'pause': 10"
--param="'hostnames': ['8.8.8.8', '8.8.4.4'], 'filters': ['avg_rtt']"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import time
from copy import deepcopy

from mksensors.lib import mks
from mksensors.lib.sensor.network import ping


def checkRequirements():
    ping.checkRequirements()


if __name__ == '__main__':
    params = mks.loadSensorConfig()
    sensorname = mks.getSensorName()

    # Set default parameters
    hostnames = params.get('hostnames', [])
    filters = params.get(
        'datasources', [
            'max_rtt', 'min_rtt', 'avg_rtt', 'packet_lost',
            'packet_size', 'timeout', 'destination',
            'destination_ip', 'result',
        ]
    )

    # Set datasource list
    datasources = []
    for hostname in hostnames:
        for filter in filters:
            dsname = "%(hostname)s_%(filter)s" % locals()
            datasources.append(dsname)

    senders = mks.loadSenderObject(sensorname, datasources)

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
            for filter in filters:
                datasource = "%(hostname)s_%(filter)s" % locals()
                value = result[filter]
                values.append((datasource, value, mks.getTimestamp()))

            mks.sendValues(senders, sensorname, values)
        # Sleep
        time.sleep(params['pause'])
