#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
apt-get install rrdtool python-dev librrd-dev
mksensors sender new sender.rrd --param="'location': '/opt/mksensors/datas/rrd'"
save dump for convert to another computer: for f in *.rrd; do rrdtool dump ${f} > ${f}.xml; done
restore from xml file: for f in *.xml; do rrdtool restore ${f} `echo ${f} | sed s/\.xml//`; done
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import os

from distutils.spawn import find_executable
from mksensors.lib import mks
from mksensors.lib.mks.plugins import SenderPlugin

DAY = 86400
WEEK = DAY * 7
MONTH = DAY * 31
YEAR = DAY * 365


class Sender(SenderPlugin):
    def __init__(self):
        """Init sender class"""
        super(Sender, self).__init__()
        self.sendertype = 'rrd'
        self.config = mks.loadSenderConfig(self.sendertype)

        # Load rrd module
        self.myrrdtool = __import__('rrdtool')

        # Init default parameters
        self.config['step'] = int(self.config.get('step', '15'))
        self.config['pdpday'] = int(self.config.get('dayres', '60')) / self.config['step']
        self.config['pdpweek'] = int(self.config.get('weekres', '300')) / self.config['step']
        self.config['pdpmonth'] = int(self.config.get('monthres', '900')) / self.config['step']
        self.config['pdpyear'] = int(self.config.get('monthres', '3600')) / self.config['step']
        self.config['pdptenyear'] = int(self.config.get('monthres', '14400')) / self.config['step']
        self.config['unknowtime'] = self.config['step'] * 4
        self.config['sample4day'] = DAY / self.config['step'] / self.config['pdpday']
        self.config['sample4week'] = WEEK / self.config['step'] / self.config['pdpweek']
        self.config['sample4month'] = MONTH / self.config['step'] / self.config['pdpmonth']
        self.config['sample4year'] = YEAR / self.config['step'] / self.config['pdpyear']
        self.config['sample4tenyear'] = 10 * YEAR / self.config['step'] / self.config['pdptenyear']


    def getDescription(self):
        return "Write sensors values in the RRD file"

    def initSender(self, sensorname, datasources):
        """Init the sender object parameters"""
        if 'location' not in self.config:
            raise Exception("Location is not define")

        # Check folder
        location = self.config['location']
        if not os.path.isdir(location):
            os.makedirs(location)

    def createRRD(self, filename, datasource):
        if not os.path.exists(filename):
            step = self.config['step']
            pdpday = self.config['pdpday']
            pdpweek = self.config['pdpweek']
            pdpmonth = self.config['pdpmonth']
            pdpyear = self.config['pdpyear']
            pdptenyear = self.config['pdptenyear']
            datas4day = self.config['sample4day']
            datas4week = self.config['sample4week']
            datas4month = self.config['sample4month']
            datas4year = self.config['sample4year']
            datas4tenyear = self.config['sample4tenyear']
            unknowtime = self.config['unknowtime']
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
            location = self.config['location']
            dsname = mks.datasource2String(datasource, '.')
            filename = '%(location)s/%(sensorname)s.%(dsname)s.rrd' % locals()
            if not os.path.exists(filename):
                self.createRRD(filename, datasource)

            # Write data
            if value is not None:
                self.myrrdtool.update(filename, 'N:%(value)s' % locals())

    def checkRequirements(self):
        super(Sender, self).checkRequirements()

        # Check rrdtool executable
        executable = find_executable('rrdtool')
        if executable is None:
            raise Exception(
                "Cannot find the rrdtool executable, please install the rrdtool with your distribution package manager")

        # Check
        packages = ['python-rrdtool==1.4.7']
        mks.checkOrInstallPackages(packages)
