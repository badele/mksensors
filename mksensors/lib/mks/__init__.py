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
from shutil import copytree, rmtree
from copy import deepcopy

import yaml

# Default Constant
SUPERVISOCONF = '/etc/supervisord.d'
LIBDIR = os.path.abspath(os.path.join(__file__, '../../..'))
USERDIR = '/usr/local/mksensors/bin'
CONFDIR = '/usr/local/mksensors/bin'


def loadModule(modulename):
    # Try to load the sensor module
    try:
        mod = __import__(modulename, fromlist=[modulename])
    except ImportError:
        raise Exception("Can't Load module %s" % modulename)

    return mod


def convertStrintToDict(content):
    """Convert string to Dictionary"""
    return ast.literal_eval("{%s}" % content)


def getSensorLibraryPath(sensorlibraryname):
    """Get main sensor python project file"""

    libdir = LIBDIR
    subpath = sensorlibraryname.replace('.', '/')
    sensorlibrarypath = "%(libdir)s/%(subpath)s" % locals()

    return sensorlibrarypath


def getSensorUserPath(sensorname):
    """Get user sensor path"""

    userdir = USERDIR
    sensorlibrarypath = "%(userdir)s/%(sensorname)s" % locals()

    return sensorlibrarypath


def createSupervisorConf(sensorname, sensorlibraryname, params, **kwargs):
    """Create supervisor conf for sensor"""

    # Add parameters
    localparams = deepcopy(params)
    localparams['python'] = sys.executable
    localparams['sensorname'] = sensorname
    localparams['sensorcmd'] = getSensorUserPath(sensorname) + '/__init__.py'


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

    sensoruserpath = getSensorUserPath(sensorname)
    checkfilename = '%(sensoruserpath)s/__init__.py' % locals()
    if os.path.exists(checkfilename):
        print "Delete %s" % sensoruserpath
        rmtree(sensoruserpath)


def copySensorLibraryToUser(sensorname, sensorlibraryname, params,  **kwargs):
    """Copy sensor template to user script folder"""

    sensorlibrarypath = getSensorLibraryPath(sensorlibraryname)
    sensoruserpath = getSensorUserPath(sensorname)

    if os.path.isdir(sensoruserpath) and kwargs['--force'] is False:
        print '%(sensorname)s allready exist in %(sensoruserpath)s' % locals()
    else:
        rmtree(sensoruserpath)
        copytree(sensorlibrarypath, sensoruserpath)


def createSensorConfig(sensorname, params, **kwargs):
    """Create sensor YAML configuration file"""

    # Sensor configuration filename
    sensoruserpath = getSensorUserPath(sensorname)
    conffilename = '%(sensoruserpath)s/conf.yml' % locals()

    # Merge configuration
    conf = {}
    if os.path.isdir(conffilename):
        with open(conffilename, 'r') as stream:
            conf = yaml.load(stream)

    for key in params.keys():
        conf[key] = params[key]

    # Save to YAML format
    saveto(conffilename, yaml.dump(conf))


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