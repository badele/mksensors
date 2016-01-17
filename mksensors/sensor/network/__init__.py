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
from mksensors.lib.mod.network.ping import ping

if __name__ == '__main__':
    params = mks.loadSensorConfig()
    sensorname = mks.getSensorName()
    senders = mks.loadSenderObject(sensorname)

    # Set default parameters
    hostnames = params.get('hostnames', [])
    filters = params.get(
        'filters', [
            'max_rtt', 'min_rtt', 'avg_rtt', 'packet_lost',
            'output', 'packet_size', 'timeout', 'destination',
            'destination_ip', 'result',
        ]
    )

    while True:
        # Ping for all hostnames
        for hostname in hostnames:
            # Test connexion
            rping = ping(destination=hostname, **params)
            rping.run()
            result = deepcopy(rping.results)
            result['sensorname'] = sensorname
            result['hostname'] = hostname.replace('.', '_')

            # return value
            for varname in filters:
                result['varname'] = varname
                id = "%(sensorname)s.%(hostname)s.%(varname)s" % result
                value = "%(avg_rtt)s" % result
                mks.sendMessages(senders, id, value)
        # Sleep
        time.sleep(params['pause'])
