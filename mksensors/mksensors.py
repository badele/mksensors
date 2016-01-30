#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  mksensors enable sender SENDERTYPE [-d | --debug]
  mksensors disable sender SENDERTYPE [-d | --debug]
  mksensors sensor new SENSORNAME SENSORLIBRARYNAME [--force]  [--param=<param>]
  mksensors sensor list
  mksensors sensor remove SENSORNAME
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


def newSensor(sensorname, sensorlibraryname, params, **kwargs):
    """
    Create new sensor configuration
     - Create supervisor configuration
     - Create sensor user script from template
     - Create YAML configuration file from --param
     """

    # Check packages installation
    modulename = 'mksensors.templates.%s' % sensorlibraryname
    mod = mks.loadModule(modulename)
    mod.checkRequirements()

    # Create Supervisor configuration
    mks.createSupervisorConf(
        sensorname=sensorname,
        sensorlibraryname=sensorlibraryname,
        params=params,
        **kwargs
    )

    # Copy module sensor into USERSCRIPTS folder
    mks.copySensorLibraryToUser(
        sensorname=sensorname,
        sensorlibraryname=sensorlibraryname,
        params=params,
        **kwargs
    )

    # Create sensor user configuration
    mks.createSensorConfig(
        sensorname=sensorname,
        params=params,
        **kwargs
    )


def removeSensor(sensorname):
    """
    Remove sensor
     - Remove supervisor sensor configuration
     - Remove Sensor user script
     - Remove Sensor configuration
    """
    mks.removeSupervisorConf(sensorname=sensorname)
    mks.removeSensorUser(sensorname)


def ListSensors():
    supervisorfiles = glob.glob(os.path.join(mks.SUPERVISORDIR, "mks_*"))

    for filename in supervisorfiles:
        content = open(filename).read()
        m = re.match(r".* (.*/__init__\.py)", content, re.DOTALL)
        # if m:
        #     sensorfilename = m.group(1)
        #     sensormod = mks.loadModule(sensorfilename)


def enableSender(sendertype, **kwargs):
    # Check packages installation
    modulename = 'mksensors.lib.%s' % sendertype

    # Check sender requirements
    mod = mks.loadModule(modulename)
    mod.checkRequirements()

    # Create sensor user configuration
    mks.enableSenderConfig(
        sendertype=sendertype,
        #params=params,
        **kwargs
    )

def disableSender(sendertype, **kwargs):
    # Create sensor user configuration
    mks.disableSenderConfig(
        sendertype=sendertype,
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
    # Sensor
    ###############################
    if argopts['sensor'] and argopts['new']:

        newSensor(
            sensorname=argopts['SENSORNAME'],
            sensorlibraryname=argopts['SENSORLIBRARYNAME'],
            params=mks.convertStrintToDict(argopts['--param']),
            **argopts
        )

    if argopts['sensor'] and argopts['remove']:
        removeSensor(sensorname=argopts['SENSORNAME'])

    if argopts['sensor'] and argopts['list']:
        ListSensors()

    ###############################
    # Enable / Disable
    ###############################
    if argopts['enable']:
        if argopts['sender']:
            enableSender(
                sendertype=argopts['SENDERTYPE'],
                #params=mks.convertStrintToDict(argopts['--param']),
                **argopts
            )

    if argopts['disable']:
        if argopts['sender']:
            disableSender(
                sendertype=argopts['SENDERTYPE'],
                #params=mks.convertStrintToDict(argopts['--param']),
                **argopts
            )


if __name__ == '__main__':
    main()
