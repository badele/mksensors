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
__commitnumber__ = "$id$"

import os
import logging

from distutils.spawn import find_executable
from mksensors.lib import mks
from mksensors.lib.mks.plugins import SenderPlugin

DAY = 86400
WEEK = DAY * 7
MONTH = DAY * 31
YEAR = DAY * 365

_LOGGER = logging.getLogger(__name__)
mks.init_logging(logger=_LOGGER, loglevel=mks.LOGSEVERITY['DEBUG'])

class Sender(SenderPlugin):
    def __init__(self):
        """Init sender class"""
        try:
            super(Sender, self).__init__('rrd', _LOGGER)
        except:
            _LOGGER.exception('SenderPlugin Init error')
            raise

        # Load rrd module
        self.myrrdtool = __import__('rrdtool')

        # RRD
        if 'rrd' not in self.config:
            self.config['rrd'] = {
                'unknowtime': 60,
                'daily': {
                    'lastaverage': {'nbsample': 1440, 'pdp': 4},
                    'minmax': {'nbsample': 1440, 'pdp': 240}
                },
                'monthly': {
                    'lastaverage': {'nbsample': 8928, 'pdp': 20},
                    'minmax': {'nbsample': 124, 'pdp': 1440}
                },
                'yearly': {
                    'lastaverage': {'nbsample': 35040, 'pdp': 60},
                    'minmax': {'nbsample': 730, 'pdp': 2880}
                },
                'yearlyten': {
                    'lastaverage': { 'nbsample': 87600, 'pdp': 240},
                    'minmax': {'nbsample': 3650, 'pdp': 5760}
                }
            }


    def getDescription(self):
        return "Write sensors values in the RRD file"

    def initSender(self, sensorname, datasources):
        """Init the sender object parameters"""

        super(Sender, self).initSender(sensorname, datasources)

        if 'location' not in self.config:
            raise Exception("Location is not define")

        # Check folder
        location = self.config['location']
        if not os.path.isdir(location):
            os.makedirs(location)

        self.logger.debug('Sender is initialized')


    def createRRD(self, filename, datasource):
        try:
            if not os.path.exists(filename):
                step = self.mksconfig.get('stepinterval', 15)
                unknowtime = self.config['rrd'].get('unknowtime', 60)
                # Daily
                d_lastaverage_pdp = self.config['rrd']['daily']['lastaverage'].get('pdp', 4)
                d_lastaverage_sample = self.config['rrd']['daily']['lastaverage'].get('nbsample', 1440)
                d_minmax_pdp = self.config['rrd']['daily']['minmax'].get('pdp', 240)
                d_minmax_sample = self.config['rrd']['daily']['minmax'].get('nbsample', 1440)
                # Monthly
                m_lastaverage_pdp = self.config['rrd']['monthly']['lastaverage'].get('pdp', 20)
                m_lastaverage_sample = self.config['rrd']['monthly']['lastaverage'].get('nbsample', 8928)
                m_minmax_pdp = self.config['rrd']['monthly']['minmax'].get('pdp', 1440)
                m_minmax_sample = self.config['rrd']['monthly']['minmax'].get('nbsample', 124)
                # Yearly
                y_lastaverage_pdp = self.config['rrd']['yearly']['lastaverage'].get('pdp', 60)
                y_lastaverage_sample = self.config['rrd']['yearly']['lastaverage'].get('nbsample', 35040)
                y_minmax_pdp = self.config['rrd']['yearly']['minmax'].get('pdp', 2880)
                y_minmax_sample = self.config['rrd']['yearly']['minmax'].get('nbsample', 730)
                # 10 Yearly
                t_lastaverage_pdp = self.config['rrd']['yearlyten']['lastaverage'].get('pdp', 240)
                t_lastaverage_sample = self.config['rrd']['yearlyten']['lastaverage'].get('nbsample', 87600)
                t_minmax_pdp = self.config['rrd']['yearlyten']['minmax'].get('pdp', 5760)
                t_minmax_sample = self.config['rrd']['yearlyten']['minmax'].get('nbsample', 3650)

                self.myrrdtool.create(
                        filename,
                        '--start',
                        'now',
                        '--step', '%(step)s' % locals(),
                            'DS:value:GAUGE:%(unknowtime)s:U:U' % locals(),
                            # Daily
                            'RRA:LAST:0.5:%(d_lastaverage_pdp)s:%(d_lastaverage_sample)s' % locals(),
                            'RRA:AVERAGE:0.5:%(d_lastaverage_pdp)s:%(d_lastaverage_sample)s' % locals(),
                            'RRA:MIN:0.5:%(d_minmax_pdp)s:%(d_minmax_sample)s' % locals(),
                            'RRA:MAX:0.5:%(d_minmax_pdp)s:%(d_minmax_sample)s' % locals(),
                            # Montly
                            'RRA:AVERAGE:0.5:%(m_lastaverage_pdp)s:%(m_lastaverage_sample)s' % locals(),
                            'RRA:MIN:0.5:%(m_minmax_pdp)s:%(m_minmax_sample)s' % locals(),
                            'RRA:MAX:0.5:%(m_minmax_pdp)s:%(m_minmax_sample)s' % locals(),
                            # Yearly
                            'RRA:AVERAGE:0.5:%(y_lastaverage_pdp)s:%(y_lastaverage_sample)s' % locals(),
                            'RRA:MIN:0.5:%(y_minmax_pdp)s:%(y_minmax_sample)s' % locals(),
                            'RRA:MAX:0.5:%(y_minmax_pdp)s:%(y_minmax_sample)s' % locals(),
                            # 10 Yearly
                            'RRA:AVERAGE:0.5:%(t_lastaverage_pdp)s:%(t_lastaverage_sample)s' % locals(),
                            'RRA:MIN:0.5:%(t_minmax_pdp)s:%(t_minmax_sample)s' % locals(),
                            'RRA:MAX:0.5:%(t_minmax_pdp)s:%(t_minmax_sample)s' % locals(),
                )
        except:
            self.logger.exception('createRRD')
            raise


    def sendValues(self, sensorname, items):
        try:
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
        except:
            self.logger.exception('sendValues')

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
