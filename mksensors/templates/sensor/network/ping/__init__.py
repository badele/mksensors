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
    sensorname = mks.getSensorName()
    config = mks.loadSensorConfig(sensorname)

    # Set default parameters
    hostnames = config.get('hostnames', [])
    filtered_ds = config.get(
        'datasources', [
            'max_rtt', 'min_rtt', 'avg_rtt', 'packet_lost',
            'packet_size', 'timeout', 'result',
        ]
    )

    # Set datasource list
    datasources = []
    for hostname in hostnames:
        for filtered in filtered_ds:
            dsnames = (hostname, filtered)
            datasources.append(dsnames)

    senders = mks.getEnabledSenderObjects(sensorname, datasources)

    while True:
        # Ping for all hostnames
        for hostname in hostnames:
            # Test connexion
            rping = ping.ping(destination=hostname, **config)
            rping.run()
            result = deepcopy(rping.results)
            result['sensorname'] = sensorname
            result['hostname'] = hostname.replace('.', '_')

            # return value
            values = []
            for filtered in filtered_ds:
                datasource = (hostname, filtered)
                value = result[filtered]
                values.append((datasource, value, mks.getTimestamp()))

            mks.sendValues(senders, sensorname, values)
        # Sleep
        time.sleep(config['pause'])
