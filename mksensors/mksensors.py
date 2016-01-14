#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  mksensors init
  mksensors new SENSORNAME SENSORLIBRARYNAME [--param=<param>]...
  mksensors list
  mksensors del SENSORNAME
  mksensors senderconfig EXPORTERNAME [--param=<param>]...
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
import re
import sys

import lib
import glob

from docopt import docopt
from distutils.spawn import find_executable


def convertParamToDict(params):
    result = {}
    for param in params:
        (key, value) = param.split('=')
        result[key] = value

    return result

def rootRequire():
    if not os.geteuid() == 0:
        sys.exit('This command must be run as root')




def setExporterOptions():
    pass


def newSensor(sensorname, sensorlibraryname, **kwargs):

    # Set default variable if is not set
    if 'python' not in kwargs:
        kwargs['python'] = sys.executable

    lib.createSupervisorConf(
        sensorname=sensorname,
        sensorlibraryname=sensorlibraryname,
        **kwargs
    )


def ListSensors():
    supervisorfiles = glob.glob(os.path.join(lib.SUPERVISOCONF, "mks_*"))

    for filename in supervisorfiles:
        content = open(filename).read()
        m = re.match(r".* (.*/__init__\.py)", content, re.DOTALL)
        if m:
            sensorfilename = m.group(1)
            sensormod = lib.loadModule(sensorfilename)


def initMkSensors():
    errormsg = ""

    # Check Supervisorctl executable
    executable = find_executable('supervisorctl')
    if executable is None:
        errormsg += "* Cannot find the supervisorctl executable\n"

    # Check /etc/supervisord.d folder
    folderexists = os.path.isdir(lib.SUPERVISOCONF)
    if not folderexists:
        errormsg += "* Cannot find the %s folder\n" % lib.SUPERVISOCONF

    # Create supervisor launcher
    dirname = os.path.dirname(sys.executable)

    executable = find_executable('systemctl')
    if executable:
        systemdconf = """[Unit]
Description=Supervisor process control system for UNIX
Documentation=http://supervisord.org
After=network.target

[Service]
ExecStart=%(dirname)s/supervisord -n -c /etc/supervisord.conf
ExecStop=%(dirname)s/supervisorctl shutdown
ExecReload=%(dirname)s/supervisorctl reload
KillMode=process
Restart=on-failure
RestartSec=50s

[Install]
WantedBy=multi-user.target""" % locals()

        lib.saveto('/etc/systemd/system/supervisord.service', systemdconf)

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


if __name__ == '__main__':

    argopts = docopt(__doc__)

    # Force use root account
    rootRequire()

    if argopts['init']:
        initMkSensors()

    if argopts['new']:
        newSensor(
            sensorname=argopts['SENSORNAME'],
            sensorlibraryname=argopts['SENSORLIBRARYNAME'],
            **convertParamToDict(argopts['--param'])
        )

    if argopts['list']:
        ListSensors()

    if argopts['senderconfig']:
        setExporterOptions()

