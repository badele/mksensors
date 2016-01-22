#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mksensors sender new sender.rrd --param="'location': '/usr/local/mksensors/rrd'"
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
    # Check rrdtool executable
    executable = find_executable('rrdtool')
    if executable is None:
        print "Cannot find the rrdtool executable, please install the rrdtool with your distribution package manager\n"
        sys.exit()

    # Check
    packages = ['rrdtool==0.1.2']
    mks.checkOrInstallPackages(packages)



class Sender(object):
    """Check if host reply a ICMP request"""

    def __init__(self, sensorname, datasources, conf):
        self.myrrdtool = __import__('rrdtool')

        self.sensorname = sensorname
        self.datasources = datasources
        self.conf = conf.get('sender.rrd', {})
        self.conf['step'] = int(self.conf.get('step', '15'))
        self.conf['pdpday'] = int(self.conf.get('dayres', '60')) / self.conf['step']
        self.conf['pdpweek'] = int(self.conf.get('weekres', '300')) / self.conf['step']
        self.conf['pdpmonth'] = int(self.conf.get('monthres', '900')) / self.conf['step']
        self.conf['pdpyear'] = int(self.conf.get('monthres', '3600')) / self.conf['step']
        self.conf['pdptenyear'] = int(self.conf.get('monthres', '14400')) / self.conf['step']
        self.conf['unknowtime'] = self.conf['step'] * 4
        self.conf['sample4day'] = DAY / self.conf['step'] / self.conf['pdpday']
        self.conf['sample4week'] = WEEK / self.conf['step'] / self.conf['pdpweek']
        self.conf['sample4month'] = MONTH / self.conf['step'] / self.conf['pdpmonth']
        self.conf['sample4year'] = YEAR / self.conf['step'] / self.conf['pdpyear']
        self.conf['sample4tenyear'] = 10 * YEAR / self.conf['step'] / self.conf['pdptenyear']


    def initSender(self):


        if 'location' not in self.conf:
            raise Exception("Location is not define")

        # Check folder
        location = self.conf['location']
        if not os.path.isdir(location):
            os.makedirs(location)


    def createRRD(self, filename, datasource):
        if not os.path.exists(filename):
            step = self.conf['step']
            pdpday = self.conf['pdpday']
            pdpweek = self.conf['pdpweek']
            pdpmonth = self.conf['pdpmonth']
            pdpyear = self.conf['pdpyear']
            pdptenyear = self.conf['pdptenyear']
            datas4day = self.conf['sample4day']
            datas4week = self.conf['sample4week']
            datas4month = self.conf['sample4month']
            datas4year = self.conf['sample4year']
            datas4tenyear = self.conf['sample4tenyear']
            unknowtime = self.conf['unknowtime']
            self.myrrdtool.create(
                filename,
                '--start',
                'now',
                '--step', '%(step)s' % locals(),
                'DS:value:GAUGE:%(unknowtime)s:U:U' % locals(),
                'RRA:AVERAGE:0.5:%(pdpday)s:%(datas4day)s' % locals(),
                'RRA:AVERAGE:0.5:%(pdpweek)s:%(datas4week)s' % locals(),
                'RRA:AVERAGE:0.5:%(pdpmonth)s:%(datas4month)s' % locals(),
                'RRA:AVERAGE:0.5:%(pdpyear)s:%(datas4year)s' % locals(),
                'RRA:AVERAGE:0.5:%(pdptenyear)s:%(datas4tenyear)s' % locals(),
                'RRA:MIN:0.5:%(pdpday)s:%(datas4day)s' % locals(),
                'RRA:MIN:0.5:%(pdpweek)s:%(datas4week)s' % locals(),
                'RRA:MIN:0.5:%(pdpmonth)s:%(datas4month)s' % locals(),
                'RRA:MIN:0.5:%(pdpyear)s:%(datas4year)s' % locals(),
                'RRA:MIN:0.5:%(pdptenyear)s:%(datas4tenyear)s' % locals(),
                'RRA:MAX:0.5:%(pdpday)s:%(datas4day)s' % locals(),
                'RRA:MAX:0.5:%(pdpweek)s:%(datas4week)s' % locals(),
                'RRA:MAX:0.5:%(pdpmonth)s:%(datas4month)s' % locals(),
                'RRA:MAX:0.5:%(pdpyear)s:%(datas4year)s' % locals(),
                'RRA:MAX:0.5:%(pdptenyear)s:%(datas4tenyear)s' % locals()
            )

    def sendValues(self, sensorname, items):
        for item in items:
            (datasource, value, ts) = item

            # Check if rrd exist
            sensorname = self.sensorname
            location = self.conf['location']
            filename = '%(location)s/%(sensorname)s.%(datasource)s.rrd' % locals()
            if not os.path.exists(filename):
                self.createRRD(filename, datasource)

            # Write data
            if value is not None:
                self.myrrdtool.update(filename, 'N:%(value)s' % locals())
