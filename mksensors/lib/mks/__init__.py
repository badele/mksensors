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
import time
import pip
import datetime
import pkg_resources
from shutil import copytree, rmtree
from copy import deepcopy

try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse


import yaml

# Default Constant
SUPERVISOCONF = '/etc/supervisord.d'
LIBDIR = os.path.abspath(os.path.join(__file__, '../../..'))
CONFDIR = '/usr/local/mksensors/conf'
BINDIR = '/usr/local/mksensors/bin'
LOGDIR = '/usr/local/mksensors/log'


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


def getSensorLibraryPath(sensorlibraryname):
    """Get main sensor python project file"""

    libdir = LIBDIR
    subpath = sensorlibraryname.replace('.', '/')
    sensorlibrarypath = "%(libdir)s/%(subpath)s" % locals()

    return sensorlibrarypath


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


def createSupervisorConf(sensorname, sensorlibraryname, params, **kwargs):
    """Create supervisor conf for sensor"""

    # Add parameters
    localparams = deepcopy(params)
    localparams['python'] = sys.executable
    localparams['sensorname'] = sensorname
    localparams['sensorcmd'] = getSensorBinPath(sensorname) + '/__init__.py'


    # Prepare supervisor.conf
    sconf = """[program:%(sensorname)s]
command=%(python)s %(sensorcmd)s
autostart=true
autorestart=true
redirect_stderr=true
startsecs=5""" % localparams

    # Write configuration
    supervisordir = SUPERVISOCONF
    filename = "%(supervisordir)s/mks_%(sensorname)s.conf" % locals()
    saveto(filename, sconf)


def removeSupervisorConf(sensorname):
    """Remove the supervisor Configuration"""

    supervisordir = SUPERVISOCONF
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


def copySensorLibraryToUser(sensorname, sensorlibraryname, params,  **kwargs):
    """Copy sensor template to user script folder"""

    sensorlibrarypath = getSensorLibraryPath(sensorlibraryname)
    sensoruserpath = getSensorBinPath(sensorname)

    if os.path.isdir(sensoruserpath) and kwargs['--force'] is False:
        print '%(sensorname)s allready exist in %(sensoruserpath)s' % locals()
    else:
        if os.path.isdir(sensoruserpath):
            rmtree(sensoruserpath)
        copytree(sensorlibrarypath, sensoruserpath)


def createSensorConfig(sensorname, params, **kwargs):
    """Create sensor YAML configuration file"""

    # Sensor configuration filename
    sensoruserpath = getSensorBinPath(sensorname)
    conffilename = '%(sensoruserpath)s/conf.yml' % locals()

    # Merge configuration
    conf = {}
    if os.path.isfile(conffilename):
        with open(conffilename, 'r') as stream:
            conf = yaml.load(stream)

    for key in params.keys():
        conf[key] = params[key]

    # Save to YAML format
    saveto(conffilename, yaml.dump(conf, default_flow_style=False))


def createSenderConfig(sendertype, params, **kwargs):
    """Create sensor YAML configuration file"""

    # Sender configuration filename
    etc = CONFDIR
    conffilename = '%(etc)s/sender.yml' % locals()

    # Merge configuration
    conf = {}
    if os.path.isfile(conffilename):
        with open(conffilename, 'r') as stream:
            conf = yaml.load(stream)

    conf[sendertype] = {}
    for key in params.keys():
        conf[sendertype][key] = params[key]

    # Save to YAML format
    saveto(conffilename, yaml.dump(conf, default_flow_style=False))


def loadSenderObject(sensorname):
    conf = CONFDIR
    conffilename = '%(conf)s/sender.yml' % locals()

    conf = {}
    if os.path.isfile(conffilename):
        with open(conffilename, 'r') as stream:
            conf = yaml.load(stream)

    senders = []
    for key in conf:
        modulename = 'mksensors.%s' % key
        mod = loadModule(modulename)
        obj = mod.Sender(sensorname, conf)
        obj.initSender()
        senders.append(obj)

    return senders

def sendMessages(senders, id, value, ts=None):

    if ts is None:
        now = datetime.datetime.now()
        ts = time.mktime(now.timetuple())

    for sender in senders:
        sender.sendMessage(id, value, ts)

def loadSensorConfig():
    """Load sensor YAML file"""

    mainpython = sys.argv[0]
    sensorfolder = os.path.dirname(mainpython)
    conffilename = "%(sensorfolder)s/conf.yml" % locals()

    conf = {}
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