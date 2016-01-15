#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  mksensors init
  mksensors new SENSORNAME SENSORLIBRARYNAME [--param=<param>]...
  mksensors list
  mksensors remove SENSORNAME
  mksensors senderconfig EXPORTERNAME [--param=<param>]...
  mksensors -h | --help

Arguments:
  <sensorname> 	    Sensor name
  SENSORLIBRARYNAME Sensor libraryname (ex: sensors.network )
  EXPORTERNAME 	Exporter name

Options:
  -h --help     Show this screen.

Examples!
   sudo mksensors init
   sudo mksensors new testping sensors.network --param=destination=8.8.8.8 --param=timeout=500
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

from docopt import docopt
from distutils.spawn import find_executable

from lib import mks


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

    # Create Supervisor configuration
    mks.createSupervisorConf(
        sensorname=sensorname,
        sensorlibraryname=sensorlibraryname,
        **kwargs
    )

    # Copy module sensor into USERSCRIPTS folder
    mks.copySensorLibraryToUser(sensorname, sensorlibraryname, **kwargs)

def removeSensor(sensorname):

    # Set default variable if is not set
    if 'python' not in kwargs:
        kwargs['python'] = sys.executable

    # Create Supervisor configuration
    mks.createSupervisorConf(
        sensorname=sensorname,
        sensorlibraryname=sensorlibraryname,
        **kwargs
    )

    # Copy module sensor into USERSCRIPTS folder
    mks.copySensorLibraryToUser(sensorname, sensorlibraryname, **kwargs)


def ListSensors():
    supervisorfiles = glob.glob(os.path.join(mks.SUPERVISOCONF, "mks_*"))

    for filename in supervisorfiles:
        content = open(filename).read()
        m = re.match(r".* (.*/__init__\.py)", content, re.DOTALL)
        if m:
            sensorfilename = m.group(1)
            sensormod = mks.loadModule(sensorfilename)


def initMkSensors():
    errormsg = ""

    ################################
    # Supervisor checker
    ################################

    # Check Supervisorctl executable
    executable = find_executable('supervisorctl')
    if executable is None:
        errormsg += "* Cannot find the supervisorctl executable\n"

    # Check /etc/supervisord.d folder
    folderexists = os.path.isdir(mks.SUPERVISOCONF)
    if not folderexists:
        errormsg += "* Cannot find the %s folder\n" % mks.SUPERVISOCONF

    # Create supervisor launcher
    dirname = os.path.dirname(sys.executable)

    ################################
    # Systemd startup script
    ################################

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

        mks.saveto('/etc/systemd/system/supervisord.service', systemdconf)

    ################################
    # Mksensors user & folders
    ################################

    # uid = -1
    # try:
    #     uid = pwd.getpwnam('mksensors').pw_uid
    # except KeyError:
    #     executable = find_executable('systemctl')
    #     if executable:
    #         randomvalue = "%032x" % random.getrandbits(128)
    #         md5 = hashlib.md5(randomvalue).hexdigest()
    #         userdir = mks.USERDIR
    #         os.system("useradd -p '%(md5)s' -d '%(userdir)s' mksensors" % locals())

    # Check and create mksensors user scripts folder
    folderexists = os.path.isdir(mks.USERDIR)
    if not folderexists:
        os.makedirs(mks.USERDIR)

    # if folderexists:
    #     fd = os.open(mks.USERDIR, os.O_RDONLY)
    #     os.fchown(fd, uid, 0)
    #     os.fchmod(fd, stat.S_ISUID | stat.S_IRUSR | stat.S_IWUSR | stat.S_IEXEC)

    # # Check and create /etc/mksensors folder
    # folderexists = os.path.isdir(mks.CONFDIR)
    # if not folderexists:
    #     os.makedirs(mks.CONFDIR)

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

    if argopts['remove']:
        removeSensor(sensorname=argopts['SENSORNAME'])

    if argopts['list']:
        ListSensors()

    if argopts['senderconfig']:
        setExporterOptions()

