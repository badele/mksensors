#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import pyping


class ping(object):
    """Check if host reply a ICMP request"""
    def __init__(self, **kwargs):
        self.params = kwargs
        self.results = {}

    def run(self):
        if 'timeout' not in self.params:
            self.params['timeout'] = 500
        if 'count' not in self.params:
            self.params['count'] = 2

        try:
            r = pyping.ping(
                hostname=self.params['destination'],
                timeout=self.params['timeout'],
                count=self.params['count'],
            )

            self.results = {
                'max_rtt': r.max_rtt,
                'min_rtt': r.min_rtt,
                'avg_rtt': r.avg_rtt,
                'packet_lost': r.packet_lost,
                'output': r.output,
                'packet_size': r.packet_size,
                'timeout': r.timeout,
                'destination': r.destination,
                'destination_ip': r.destination_ip,
                'result': 255 - (r.ret_code * 255),
            }

        except:
            self.results = {}