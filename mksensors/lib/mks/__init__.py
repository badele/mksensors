#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

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

def loadModule(modulename):
    """Load Dynamicaly python module"""

    # Try to load the sensor module
    try:
        mod = __import__(modulename, fromlist=[modulename])
    except ImportError:
        raise Exception("Can't Load module %s" % modulename)

    return mod


def convertStrintToDict(content):
    """Convert string to Dictionary"""
    if content is None:
        return {}

    return ast.literal_eval("{%s}" % content)


def datasource2String(datasources, separator):
    result = ""
    for datasource in datasources:
        result += "%(separator)s%(datasource)s" % locals()

    return result

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


def addSupervisorConf(sensorname, sensorlibraryname, **kwargs):
    """Create supervisor conf for sensor"""

    # Add parameters
    pythonexec = sys.executable
    sensorcmd = getSensorBinPath(sensorname) + '/__init__.py'
    logdir = LOGDIR

    # Prepare supervisor.conf
    sconf = """[program:%(sensorname)s]
command=%(pythonexec)s %(sensorcmd)s
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=%(logdir)s/sensor_%(sensorname)s.log
startsecs=5""" % locals()

    # Write configuration
    supervisordir = SUPERVISORDIR
    filename = "%(supervisordir)s/mks_%(sensorname)s.conf" % locals()
    saveto(filename, sconf)


def removeSupervisorConf(sensorname):
    """Remove the supervisor Configuration"""

    supervisordir = SUPERVISORDIR
    filename = "%(supervisordir)s/mks_%(sensorname)s.conf" % locals()
    if os.path.exists(filename):
        print "Delete %s" % filename
        os.remove(filename)


def removeSensorUser(sensorname):
    """Remove the sensor user script"""

    sensoruserpath = getSensorBinPath(sensorname)
    checkfilename = '%(sensoruserpath)s/__init__.py' % locals()
    if os.path.exists(checkfilename):
        print "Delete %s" % sensoruserpath
        rmtree(sensoruserpath)


def copySensorTemplateToUserBin(sensorname, sensorlibraryname, **kwargs):
    """Copy sensor template to user script folder"""

    sensorlibrarypath = getSensorTemplatePath(sensorlibraryname)
    sensoruserpath = getSensorBinPath(sensorname)

    if os.path.isdir(sensoruserpath) and kwargs['--force'] is False:
        print '%(sensorname)s sensor allready exist in %(sensoruserpath)s' % locals()
    else:
        if os.path.isdir(sensoruserpath):
            rmtree(sensoruserpath)
        copytree(sensorlibrarypath, sensoruserpath)


def addSensorConfig(sensorname, sensortype, **kwargs):
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
            raise Exception("'%(dstconf)s' allready exist, cannot activate the '%(sensortype)s'\n"
                            "Please remove '%(disabledconf)s' or '%(dstconf)s'" % locals())

        move(disabledconf, dstconf)
    else:
        copyfile(srcconf, dstconf)

    print "%(sensorname)s sensor configuration in '%(dstconf)s'" % locals()


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
            raise Exception("'%(dstconf)s' allready exist, cannot activate the '%(sendertype)s'\n"
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

    srcconf = '%(libdir)s/sender/%(sendername)s/configuration.sample.yml' % locals()
    dstconf = '%(etc)s/sender_%(sendername)s.yml' % locals()
    disabledconf = '%(etc)s/sender_%(sendername)s.yml.disabled' % locals()

    # If configuration is enabled, just disable it
    if os.path.isfile(dstconf):
        if os.path.isfile(disabledconf):
            raise Exception("'%(disabledconf)s' allready exist, cannot activate the '%(sendertype)s'\n"
                            "Please remove '%(dstconf)s' or '%(disabledconf)s'" % locals())

        move(dstconf, disabledconf)

    print "%(sendername)s sender is now disabled" % locals()


def getEnabledSenderNames(sendername=None):
    sendernames = []

    enabledsenders = glob.glob(os.path.join(CONFDIR, "sender_*.yml"))
    for enabledsender in enabledsenders:
        #filename = os.path.splitext(os.pathsep(os.path.basename(enabledsender)))
        filename = os.path.basename(os.path.splitext(enabledsender)[0])
        sendername = filename.replace('sender_', '')
        sendernames.append(sendername)

    return sendernames

def getEnabledSenderObjects(sensorname, datasources):
    sendernames = getEnabledSenderNames()

    senders = []
    for key in sendernames:
        modulename = 'mksensors.lib.sender.%s' % key
        mod = loadModule(modulename)
        senderobj = mod.Sender()
        senderobj.initSender(sensorname, datasources)
        senders.append(senderobj)

    return senders


def loadSenderConfig(sendername):
    confdir = CONFDIR
    conffilename = '%(confdir)s/sender_%(sendername)s.yml' % locals()

    config = {}
    if os.path.isfile(conffilename):
        with open(conffilename, 'r') as stream:
            config = yaml.load(stream)

    return config


def sendValues(senders, sensorname, values):

    for sender in senders:
        try:
            sender.sendValues(sensorname, values)
        except Exception as e:
            # Todo: log in mksensors.log
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print repr(traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout))
pass


def loadSensorConfig(sensorname):
    """Load sensor YAML file"""

    etc = CONFDIR
    conffilename = '%(etc)s/sensor_%(sensorname)s.yml' % locals()


    conf = {}
    if os.path.isfile(conffilename):
        with open(conffilename, 'r') as stream:
            conf = yaml.load(stream)

    # Set default parameter
    conf['pause'] = conf.get('pause', 15)

    return conf

def getSensorName():
    """Return the sensor name from user folder"""
    mainpython = sys.argv[0]
    sensorfolder = os.path.basename(os.path.dirname(mainpython))

    return sensorfolder


def saveto(filename, content):
    """Save content to file"""

    out = open(filename, 'wb')
    out.write(content)
    out.close()