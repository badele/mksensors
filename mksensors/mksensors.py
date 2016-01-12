#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  mksensors init
  mksensors new SENSORNAME SENSORLIBRARYNAME [--param=<param>]...
  mksensors exporter EXPORTERNAME PARAMS...
  mksensors -h | --help

Arguments:
  <sensorname> 	    Sensor name
  SENSORLIBRARYNAME Sensor libraryname (ex: sensors.network )
  EXPORTERNAME 	Exporter name

Options:
  -h --help     Show this screen.
"""

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'


import os
import sys

import lib

from docopt import docopt
from distutils.spawn import find_executable


def convertParamToDict(params):
    result = {}
    for param in params:
        (key, value) = param.split('=')
        result[key] = value

    return result

def initMkSensors():
    errormsg = ""

    # Check if script run as root
    if not os.geteuid() == 0:
        sys.exit('Script must be run as root')

    # Check Supervisorctl executable
    executable = find_executable('supervisorctl')
    if executable is None:
        errormsg += "* Cannot find the supervisorctl executable\n"

    # Check Supervisorctl executable
    executable = find_executable('supervisorctl')
    if executable is None:
        errormsg += "* Cannot find the supervisorctl executable\n"

    # Check /etc/supervisord.d folder
    folderexists = os.path.isdir(lib.SUPERVISOCONF)
    if not folderexists:
        errormsg += "* Cannot find the %s folder\n" % lib.SUPERVISOCONF

    # Check and create /etc/mksensors folder
    folderexists = os.path.isdir('/etc/mksensors')
    if not folderexists:
        os.makedirs('/etc/mksensors')

    # Check and create .mksensors user folder
    folderexists = os.path.isdir(os.path.expanduser('~/.mksensors'))
    if not folderexists:
        print "create dir"
        os.makedirs(os.path.expanduser('~/.mksensors'))

    if errormsg != "":
        print errormsg


def setExporterOptions():
    pass


def newSensors(**kwargs):

    # Try to load the sensor module
    try:
        modsensor = __import__(argopts['SENSORLIBRARYNAME'], fromlist=[argopts['SENSORLIBRARYNAME']])
    except ImportError:
        raise Exception("Can't Load module argopts['SENSORLIBRARYNAME']")


    # Set default variable if is not set
    if 'python' not in kwargs:
        kwargs['python'] = sys.executable

    # Execute init sensor module
    modsensor.init(**kwargs)


if __name__ == '__main__':
    argopts = docopt(__doc__)

    if argopts['init']:
        initMkSensors()

    if argopts['exporter']:
        setExporterOptions()

    if argopts['new']:
        newSensors(
            sensorname=argopts['SENSORNAME'],
            **convertParamToDict(argopts['--param'])
        )

