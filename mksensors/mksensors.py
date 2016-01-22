#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
  mksensors init
  mksensors sensor new SENSORNAME SENSORLIBRARYNAME [--force]  [--param=<param>]
  mksensors sensor list
  mksensors sensor remove SENSORNAME
  mksensors sender new SENDERTYPE [--param=<param>]
  mksensors -h | --help

Arguments:
  <sensorname> 	    Sensor name
  SENSORLIBRARYNAME Sensor libraryname (ex: sensor.network )
  SENDERTYPE 	    Sender type (ex: sender.file, sender.mqtt)

Options:
  -h --help     Show this screen.

Examples:
    sudo mksensors init
    sudo mksensors sender new sender.file --param="'location': '/usr/local/mksensors/log'"
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


def newSender(sendertype, params, **kwargs):
    # Check packages installation
    modulename = 'mksensors.lib.%s' % sendertype
    mod = mks.loadModule(modulename)
    mod.checkRequirements()

    # Create sensor user configuration
    mks.createSenderConfig(
        sendertype=sendertype,
        params=params,
        **kwargs
    )


def initMkSensors():
    """
    Init the mksensors configuration, it check
     - Check if supervisorctl executable is present
     - Check if /etc/supervisord.d folder exists
     - Create supervisor systemd launcher
     - Create /usr/local/mksensors folder
    """

    errormsg = ""

    ################################
    # Supervisor checker
    ################################

    # Check Supervisorctl executable
    supervisord = find_executable('supervisord')
    supervisorctl = find_executable('supervisorctl')
    if supervisorctl is None:
        errormsg += "* Cannot find the supervisorctl executable\n"

    # Check /etc/supervisord.d folder
    supervisordir = mks.SUPERVISORDIR
    folderexists = os.path.isdir(supervisordir)
    if not folderexists:
        os.mkdir(supervisordir)

    # Check supervisord.conf file
    supervisordconf = '%s/supervisord.conf' % mks.CONFDIR
    fileexists = os.path.isfile(supervisordconf)
    if not fileexists:
        content = """[unix_http_server]
file=/tmp/supervisor_mksensors.sock
[supervisord]
logfile=/tmp/supervisord_mksensors.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/tmp/supervisord_mksensors.pid
nodaemon=false
minfds=1024
minprocs=200
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
[supervisorctl]
serverurl=unix:///tmp/supervisor_mksensors.sock
[include]
files = %(supervisordir)s/*.conf""" % locals()
        mks.saveto(supervisordconf, content)

    ################################
    # Systemd startup script
    ################################

    dirname = os.path.dirname(sys.executable)
    systemctl = find_executable('systemctl')
    if systemctl:
        content = """[Unit]
Description=Supervisor process control system for UNIX
Documentation=http://supervisord.org
After=network.target

[Service]
ExecStart=%(supervisord)s -n -c %(supervisordconf)s
ExecStop=%(supervisorctl)s shutdown
ExecReload=%(supervisorctl)s reload
KillMode=process
Restart=on-failure
RestartSec=50s

[Install]
WantedBy=multi-user.target""" % locals()

        mks.saveto('/etc/systemd/system/mksensors.service', content)

    # Create supervisorctl alias
    content = """#!/bin/bash
%(supervisorctl)s -c %(supervisordconf)s $*""" % locals()

    mks.saveto(mks.MKSENSORSCTL, content)
    fd = os.open(mks.MKSENSORSCTL, os.O_RDONLY)
    os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR | stat.S_IEXEC)

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
    #
    # # Check and create mksensors user scripts folder
    # folderexists = os.path.isdir(mks.USERDIR)
    # if not folderexists:
    #     os.makedirs(mks.USERDIR)
    #
    # if folderexists:
    #     fd = os.open(mks.USERDIR, os.O_RDONLY)
    #     os.fchown(fd, uid, 0)
    #     os.fchmod(fd, stat.S_ISUID | stat.S_IRUSR | stat.S_IWUSR | stat.S_IEXEC)

    # Check and create mksensors folders
    checkdirs = [mks.CONFDIR, mks.BINDIR, mks.LOGDIR]
    for checkdir in checkdirs:
        folderexists = os.path.isdir(checkdir)
        if not folderexists:
            os.makedirs(checkdir)

    if errormsg != "":
        print errormsg

def main():
    argopts = docopt(__doc__)

    # Force use root account
    rootRequire()

    if argopts['init']:
        initMkSensors()

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
    # Sensor
    ###############################
    if argopts['sender'] and argopts['new']:
        newSender(
            sendertype=argopts['SENDERTYPE'],
            params=mks.convertStrintToDict(argopts['--param']),
            **argopts
        )


if __name__ == '__main__':
    main()