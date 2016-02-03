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
__version__ = '0.0.1'

import os
import re
import sys
import glob
import stat
from distutils.spawn import find_executable

from docopt import docopt


from lib import mks

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
    mks.removeSupervisorConf(sensorname=sensorname)
    mks.removeSensorUser(sensorname)
    mks.disableSensorConfig(sensorname)

def checkMkSensors():
    allerrors = mks.checkMkSensors()

    if not allerrors:
        print "You mksensors is correctly configured"
        return

    print "** FOUND ERRORS **"
    for sendername in allerrors.keys():
        print "%(sendername)s:" % locals()
        for error in allerrors[sendername]:
            print "  - %(error)s" % locals()

def ListSensors():
    supervisorfiles = glob.glob(os.path.join(mks.SUPERVISORDIR, "mks_*"))

    for filename in supervisorfiles:
        content = open(filename).read()
        m = re.match(r".* (.*/__init__\.py)", content, re.DOTALL)
        # if m:
        #     sensorfilename = m.group(1)
        #     sensormod = mks.loadModule(sensorfilename)


def enableSender(sendername, **kwargs):
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
    # Create sensor user configuration
    mks.disableSenderConfig(
        sendername=sendertype,
        #params=params,
        **kwargs
    )



def main():
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

    if argopts['list']:
        if argopts['sensors']:
            ListSensors()

    if argopts['check']:
        checkMkSensors()


if __name__ == '__main__':
    main()
