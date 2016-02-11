#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__commitnumber__ = "$id$"

import os
import sys
import ast
import glob
import time
import pip
import datetime
import pkg_resources
import traceback

from shutil import copyfile, copytree, rmtree, move
from copy import deepcopy

try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse


import yaml

# Default Constant
MKSPROGRAM = os.path.abspath(os.path.join(__file__, '../../..'))
MKSDATA = '/var/lib/mksensors'
CONFDIR = '%(MKSDATA)s/etc' % locals()
BINDIR = '%(MKSDATA)s/bin' % locals()
LOGDIR = '%(MKSDATA)s/log' % locals()
SUPERVISORDIR = '%(CONFDIR)s/supervisord.d' % locals()

def getTimestamp():
    now = datetime.datetime.now()
    ts = time.mktime(now.timetuple())

    return ts

def checkPackageInstalled(package):
    """Check python package is installed"""

    try:
        req = pkg_resources.Requirement.parse(package)
    except ValueError:
        # check zip file
        req = pkg_resources.Requirement.parse(urlparse(package).fragment)

    return any(dist in req for dist in pkg_resources.working_set)


def checkOrInstallPackages(packages):
    """Check and install package if is not installed"""

    if isinstance(packages, str):
        packages = [packages]

    for package in packages:
        if not checkPackageInstalled(package):
            pip.main(['install', package])

def checkMkSensors():
    sendernames = getEnabledSenderNames()
    allerrors = {}
    for sendername in sendernames:
        modulename = 'mksensors.lib.sender.%s' % sendername
        mod = loadModule(modulename)
        senderobj = mod.Sender()
        sendererrors = senderobj.checkConfiguration()
        if sendererrors:
            allerrors[sendername] = sendererrors

    return allerrors


def loadModule(modulename):
    """Load Dynamicaly python module"""

    # Try to load the sensor module
    try:
        mod = __import__(modulename, fromlist=[modulename])
    except ImportError as e:
        raise Exception("Can't Load module %s" % modulename)

    return mod


def convertStrintToDict(content):
    """Convert string to Dictionary"""
    if content is None:
        return {}

    return ast.literal_eval("{%s}" % content)


def datasource2String(datasources, separator):
    return separator.join(datasources)

def getSensorTemplatePath(sensorlibraryname):
    """Get main sensor python project file"""

    mksprogram = MKSPROGRAM
    templatedir = '%(mksprogram)s/templates/sensor' % locals()
    subpath = sensorlibraryname.replace('.', '/')
    sensortemplatepath = "%(templatedir)s/%(subpath)s" % locals()

    return sensortemplatepath


def getSensorBinPath(sensorname):
    """Get user sensor path"""

    bindir = BINDIR
    sensorbinpath = "%(bindir)s/%(sensorname)s" % locals()

    return sensorbinpath


def getSensorLogPath(sensorname):
    """Get user sensor path"""

    logdir = LOGDIR
    sensorlogpath = "%(logdir)s/%(sensorname)s" % locals()

    return sensorlogpath


def enableSupervisorConf(sensorname, sensorlibraryname, **kwargs):
    """Create supervisor sensor conf"""

    # Add parameters
    logdir = LOGDIR
    supervisordir = SUPERVISORDIR
    pythonexec = sys.executable
    sensorcmd = getSensorBinPath(sensorname) + '/__init__.py'
    conffilename = "%(supervisordir)s/mks_%(sensorname)s.conf" % locals()
    disabledconf = '%(conffilename)s.disabled' % locals()

    if os.path.isfile(conffilename):
        return

    if os.path.isfile(disabledconf):
        move(disabledconf, conffilename)
    else:
        # Prepare supervisor.conf
        content = """[program:%(sensorname)s]
command=%(pythonexec)s %(sensorcmd)s
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=%(logdir)s/sensor_%(sensorname)s.log
startsecs=5""" % locals()

        # Write configuration
        saveto(conffilename, content)


def disableSupervisorConf(sensorname):
    """Disable supervisor sensor conf"""

    # Vars
    supervisordir = SUPERVISORDIR
    srcconf = "%(supervisordir)s/mks_%(sensorname)s.conf" % locals()
    disabledconf = "%(supervisordir)s/mks_%(sensorname)s.conf.disabled" % locals()

    # Check if supervisor configuration exists
    if not os.path.isfile(srcconf):
        return

    # If file allready disable, can disable again
    if os.path.isfile(disabledconf):
        raise Exception("'%(disabledconf)s' allready exist, cannot disable the '%(sensorname)s' sensor\n"
                        "Please remove '%(disabledconf)s' or '%(srcconf)s'" % locals())

    # Disable the supervisor configuration
    move(srcconf, disabledconf)


def removeSupervisorConf(sensorname):
    """Remove the supervisor Configuration"""

    supervisordir = SUPERVISORDIR
    filename = "%(supervisordir)s/mks_%(sensorname)s.conf" % locals()

    if not os.path.exists(filename):
        return

    os.remove(filename)
    disableSupervisorConf(sensorname)

def removeSensorUser(sensorname):
    """Remove the sensor user script"""

    sensoruserpath = getSensorBinPath(sensorname)
    checkfilename = '%(sensoruserpath)s/__init__.py' % locals()

    # Check if main sensor user file exists
    if not os.path.exists(checkfilename):
        return

    # Delete sensor user folder
    rmtree(sensoruserpath)


def copySensorTemplateToUserBin(sensorname, sensorlibraryname):
    """Copy sensor template to user script folder"""

    sensorlibrarypath = getSensorTemplatePath(sensorlibraryname)
    sensoruserpath = getSensorBinPath(sensorname)
    disableduserpath ='%(sensoruserpath)s.disabled' % locals()

    # Check if sensor user path allready exists
    if os.path.isdir(sensoruserpath):
        return

    if os.path.isdir(disableduserpath):
        move(disableduserpath, sensoruserpath)
    else:
        copytree(sensorlibrarypath, sensoruserpath)


def disableSensorTemplateToUserBin(sensorname, **kwargs):
    """Copy sensor template to user script folder"""

    # Sensor configuration filename
    srcuserpath = getSensorBinPath(sensorname)
    disablesensoruserpath = '%(srcuserpath)s.disabled' % locals()

    # Check if sensor user folder exists
    if not os.path.isdir(srcuserpath):
        return

    # If file allready disable, can disable again
    if os.path.isdir(disablesensoruserpath):
        raise Exception("'%(disablesensoruserpath)s' allready exist, cannot disable the '%(sensorname)s' sensor\n"
                        "Please remove '%(srcuserpath)s' or '%(disablesensoruserpath)s'" % locals())

    # Disable the user folder
    move(srcuserpath, disablesensoruserpath)


def enableSensorConfig(sensorname, sensortype, **kwargs):
    """Create sensor YAML configuration file"""

    # Sensor configuration filename
    etc = CONFDIR
    mksprogram = MKSPROGRAM
    templatedir = '%(mksprogram)s/templates/sensor' % locals()
    subpath = sensortype.replace('.', '/')

    srcconf = '%(templatedir)s/%(subpath)s/configuration.sample.yml' % locals()
    dstconf = '%(etc)s/sensor_%(sensorname)s.yml' % locals()
    disabledconf = '%(etc)s/sensor_%(sensorname)s.yml.disabled' % locals()

    # If configuration is disabled, just enable it
    if os.path.isfile(disabledconf):
        if os.path.isfile(dstconf):
            raise Exception("'%(dstconf)s' allready exist, cannot activate the '%(sensorname)s' sensor\n"
                            "Please remove '%(disabledconf)s' or '%(dstconf)s'" % locals())

        move(disabledconf, dstconf)
    else:
        if not os.path.isfile(dstconf):
            copyfile(srcconf, dstconf)

    print "%(sensorname)s sensor configuration in '%(dstconf)s'" % locals()


def disableSensorConfig(sensorname):
    """Disable sensor YAML configuration file"""

    # Sensor configuration filename
    etc = CONFDIR
    srcconf = '%(etc)s/sensor_%(sensorname)s.yml' % locals()
    disabledconf = '%(etc)s/sensor_%(sensorname)s.yml.disabled' % locals()

    # Check if sensor configuration exists
    if not os.path.isfile(srcconf):
        return

    # If file allready disabled, can disable again
    if os.path.isfile(disabledconf):
        raise Exception("'%(disabledconf)s' allready exist, cannot disable the '%(sensorname)s' sensor\n"
                        "Please remove '%(disabledconf)s' or '%(srcconf)s'" % locals())

    # Disabled configuration
    move(srcconf, disabledconf)


def enableSenderConfig(sendername, **kwargs):
    """Enable sender YAML configuration file"""

    # Sender configuration filename
    etc = CONFDIR
    mksprogram = MKSPROGRAM
    libdir = '%(mksprogram)s/lib' % locals()

    srcconf = '%(libdir)s/sender/%(sendername)s/configuration.sample.yml' % locals()
    dstconf = '%(etc)s/sender_%(sendername)s.yml' % locals()
    disabledconf = '%(etc)s/sender_%(sendername)s.yml.disabled' % locals()

    # If configuration is disabled, just enable it
    if os.path.isfile(disabledconf):
        if os.path.isfile(dstconf):
            raise Exception("'%(dstconf)s' allready exist, cannot activate the '%(sendername)s' sender\n"
                            "Please remove '%(disabledconf)s' or '%(dstconf)s'" % locals())

        move(disabledconf, dstconf)
    else:
        if not os.path.isfile(dstconf):
            copyfile(srcconf, dstconf)

    print "%(sendername)s sender configuration in '%(dstconf)s'" % locals()


def disableSenderConfig(sendername, **kwargs):
    """Disable sender YAML configuration file"""

    # Sender configuration filename
    etc = CONFDIR
    mksprogram = MKSPROGRAM
    libdir = '%(mksprogram)s/lib' % locals()

    dstconf = '%(etc)s/sender_%(sendername)s.yml' % locals()
    disabledconf = '%(etc)s/sender_%(sendername)s.yml.disabled' % locals()

    # Check if sender configuration exist
    if not os.path.isfile(dstconf):
        return


    # If file allready disabled, can disable again
    if os.path.isfile(disabledconf):
        raise Exception("'%(disabledconf)s' allready exist, cannot activate the '%(sendername)s' sender\n"
                        "Please remove '%(dstconf)s' or '%(disabledconf)s'" % locals())

    # Disable configuration
    move(dstconf, disabledconf)

    print "%(sendername)s sender is now disabled" % locals()


def getSenderPluginsList():
    senderfolder = '%(MKSPROGRAM)s/lib/sender' % globals()
    files = os.listdir(senderfolder)

    sendernames = []
    for filename in files:
        location = '%(senderfolder)s/%(filename)s' % locals()
        if os.path.isdir(location):
            sendernames.append(filename)

    return sendernames


def getEnabledSenderNames(sendername=None):
    enabledsenders = []

    senders = getSenderPluginsList()
    for sendername in senders:
        senderpath = os.path.join(CONFDIR, "sender_%(sendername)s.yml" % locals())
        if os.path.isfile(senderpath):
            enabledsenders.append(sendername)

    return enabledsenders

def getEnabledSenderObjects(sensorname, datasources):
    sendernames = getEnabledSenderNames()

    senders = []
    for sendername in sendernames:
        modulename = 'mksensors.lib.sender.%s' % sendername
        mod = loadModule(modulename)
        try:
            senderobj = mod.Sender()
            senderobj.initSender(sensorname, datasources)
            senders.append(senderobj)
        except Exception as e:
            print e.message

    return senders


def loadSenderConfig(sendername):
    confdir = CONFDIR
    conffilename = '%(confdir)s/sender_%(sendername)s.yml' % locals()

    config = {}
    if os.path.isfile(conffilename):
        with open(conffilename, 'r') as stream:
            config = yaml.load(stream)

    return config


def loadSensorConfig(sensorname):
    confdir = CONFDIR
    conffilename = '%(confdir)s/sensor_%(sensorname)s.yml' % locals()

    config = {}
    if os.path.isfile(conffilename):
        with open(conffilename, 'r') as stream:
            config = yaml.load(stream)

    return config



def getSensorName():
    """Return the sensor name from user folder"""
    mainpython = sys.argv[0]
    sensorfolder = os.path.basename(os.path.dirname(mainpython))

    return sensorfolder


def saveto(filename, content):
    """Save content to file"""

    # Create directory if not exists
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    # Write content
    out = open(filename, 'wb')
    out.write(content)
    out.close()