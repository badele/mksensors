#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  mksensors enable sender SENDERTYPE [-d | --debug]
  mksensors disable sender SENDERTYPE [-d | --debug]
  mksensors enable sensor SENSORNAME SENSORLIBRARYNAME [-d | --debug] [--force]
  mksensors disable sensor SENSORNAME [-d | --debug]
  mksensors remove sensor SENSORNAME [-d | --debug]
  mksensors list sensors [-d | --debug]
  mksensors list senders [-d | --debug]
  mksensors check
  mksensors -d | --debug
  mksensors -h | --help

Arguments:
  <sensorname> 	    Sensor name
  SENSORLIBRARYNAME Sensor libraryname (ex: sensor.network )
  SENDERTYPE 	    Sender type (ex: sender.file, sender.mqtt)

Options:
  -d --debug    Active debug
  -h --help     Show this screen.

Examples:
    sudo mksensors sender new sender.file --param="'location': '/opt/mksensors/datas/log'"
    sudo mksensors new testping sensor.network --param="'hostnames': ['8.8.8.8', '8.8.4.4'], 'filters': ['avg_rtt']"
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__commitnumber__ = "$id$"

import os
import re
import sys
import glob
import logging

import stat
from distutils.spawn import find_executable

from docopt import docopt
from tabulate import tabulate

from lib import mks

_LOGGER = logging.getLogger(__name__)
mks.init_logging(logger=_LOGGER, loglevel=mks.LOGSEVERITY['DEBUG'])

def rootRequire():
    """Check if run root session"""
    if not os.geteuid() == 0:
        sys.exit('This command must be run as root')


def enableSensor(sensorname, sensorlibraryname, **kwargs):
    """
    Enable new sensor configuration
     - Create supervisor configuration
     - Create sensor user script from template
     - Create YAML configuration from sensor template
     """

    _LOGGER.info('enableSensor %(sensorname)s(%(sensorlibraryname)s)' % locals())

    # Check packages installation
    modulename = 'mksensors.templates.sensor.%s' % sensorlibraryname
    mod = mks.loadModule(modulename)
    sensorobj = mod.Sensor()
    sensorobj.checkRequirements()

    # Create Supervisor configuration
    mks.enableSupervisorConf(sensorname=sensorname, sensorlibraryname=sensorlibraryname)

    # Copy module sensor code to bin folder
    mks.copySensorTemplateToUserBin(sensorname=sensorname, sensorlibraryname=sensorlibraryname)

    # Create sensor user configuration
    mks.enableSensorConfig(sensorname=sensorname, sensortype=sensorlibraryname)


def disableSensor(sensorname, **kwargs):
    """
    Enable new sensor configuration
     - Disable supervisor configuration
     - Disable sensor user script from template
     - Disable YAML configuration from sensor template
     """

    _LOGGER.info('disableSensor %(sensorname)s' % locals())

    # Create Supervisor configuration
    mks.disableSupervisorConf(sensorname)

    # Copy module sensor code to bin folder
    mks.disableSensorTemplateToUserBin(sensorname)

    # Create sensor user configuration
    mks.disableSensorConfig(sensorname)


def removeSensor(sensorname):
    """
    Remove sensor
     - Remove supervisor sensor configuration
     - Remove Sensor user script
     - Remove Sensor configuration
    """
    _LOGGER.info('removeSensor %(sensorname)s' % locals())

    mks.removeSupervisorConf(sensorname=sensorname)
    mks.removeSensorUser(sensorname)
    mks.disableSensorConfig(sensorname)

def checkMkSensors():
    _LOGGER.info('checkMkSensors' % locals())

    allerrors = mks.checkMkSensors()

    if not allerrors:
        print "You mksensors is correctly configured"
        return

    print "** FOUND ERRORS **"
    for sendername in allerrors.keys():
        print "* %(sendername)s:" % locals()
        for error in allerrors[sendername]:
            print "  - %(error)s" % locals()


def showSensorsList():
    _LOGGER.info('showSensorsList')

    # Get sensors informations
    allsensors = mks.getSensorPluginsList()
    enabledsensors = mks.getEnabledSensorNames()

    # Search if use the sensor from mksensors template
    for supervisorconf in enabledsensors.keys():
        if 'sensorname' in enabledsensors[supervisorconf]:
            sensorname = enabledsensors[supervisorconf]['sensorname']
            allsensors[sensorname]['usedby'].append(supervisorconf)

    # Show result
    sensors = []
    for sensorkey in allsensors.keys():
        description = allsensors[sensorkey]['description']
        usedby = ', '.join(allsensors[sensorkey]['usedby'])
        sensors.append((sensorkey, description, usedby))

    header = ['Sensor name', 'Description', 'Used by']
    print tabulate(sensors, headers=header, tablefmt="orgtbl")


def showSendersList():
    _LOGGER.info('showSendersList')

    allsenders = mks.getSenderPluginsList()
    enabledsenders = mks.getEnabledSenderNames()

    senders = []
    for sendername in allsenders:
        # Get senders information
        try:
            modulename = 'mksensors.lib.sender.%s' % sendername
            mod = mks.loadModule(modulename)
            senderobj = mod.Sender()
            description = senderobj.getDescription()
            enabled = 'Yes' if sendername in enabledsenders else ''
        except Exception as e:
            enabled = ''
            description = 'Cannot load the sender'

        senders.append((sendername, description, enabled))

    header = ['Sender name', 'Description', 'Enabled']
    print tabulate(senders, headers=header, tablefmt="orgtbl")


def enableSender(sendername, **kwargs):
    _LOGGER.info('enableSender %(sendername)s' % locals())

    # Check packages installation
    modulename = 'mksensors.lib.sender.%s' % sendername

    # Check sender requirements
    mod = mks.loadModule(modulename)
    senderobj = mod.Sender()
    senderobj.checkRequirements()

    # Create sensor user configuration
    mks.enableSenderConfig(
        sendername=sendername,
        #params=params,
        **kwargs
    )

    # Check mksensors configuration
    mks.checkMkSensors()

def disableSender(sendertype, **kwargs):
    _LOGGER.info('disableSender %(sendertype)s' % locals())

    # Create sensor user configuration
    mks.disableSenderConfig(
        sendername=sendertype,
        #params=params,
        **kwargs
    )


def main():
    mks.init_logging(_LOGGER, loglevel=logging.INFO)

    argopts = docopt(__doc__)

    # Force use root account
    rootRequire()

    # Debug mode
    if not argopts['--debug']:
        sys.tracebacklimit = 0

    ###############################
    # Enable / Disable
    ###############################
    if argopts['enable']:
        if argopts['sender']:
            enableSender(
                sendername=argopts['SENDERTYPE'],
                **argopts
            )

        if argopts['sensor']:
            enableSensor(
                sensorname=argopts['SENSORNAME'],
                sensorlibraryname=argopts['SENSORLIBRARYNAME'],
                **argopts
            )

    if argopts['disable']:
        if argopts['sender']:
            disableSender(
                sendertype=argopts['SENDERTYPE'],
                **argopts
            )

        if argopts['sensor']:
            disableSensor(
                sensorname=argopts['SENSORNAME'],
                **argopts
            )

    if argopts['remove']:
        if argopts['sensor']:
            removeSensor(sensorname=argopts['SENSORNAME'])

    if argopts['check']:
        checkMkSensors()

    if argopts['list']:
        if argopts['senders']:
            showSendersList()

        if argopts['sensors']:
            showSensorsList()

if __name__ == '__main__':
    main()
