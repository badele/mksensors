#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import os
from shutil import copytree

SUPERVISOCONF = '/etc/supervisord.d'
LIBDIR = os.path.abspath(os.path.join(__file__, '../..'))
USERDIR = '/usr/local/mksensors/bin'
CONFDIR = '/usr/local/mksensors/bin'


def loadModule(modulename):
    # Try to load the sensor module
    try:
        mod = __import__(modulename, fromlist=[modulename])
    except ImportError:
        raise Exception("Can't Load module %s" % modulename)

    return mod


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


def createSupervisorConf(sensorname, sensorlibraryname, **kwargs):
    """Create supervisor conf for sensor"""

    # Add parameters
    kwargs['sensorname'] = sensorname
    kwargs['sensorcmd'] = getSensorUserPath(sensorname) + '/__init__.py'

    # Prepare supervisor.conf
    sconf = """[program:%(sensorname)s]
command=%(python)s %(sensorcmd)s
autostart=true
autorestart=true
redirect_stderr=true
startsecs=5""" % kwargs

    # Write configuration
    filename = "/etc/supervisord.d/mks_%(sensorname)s.conf" % locals()
    saveto(filename, sconf)

def copySensorLibraryToUser(sensorname, sensorlibraryname, **kwargs):

    sensorlibrarypath = getSensorLibraryPath(sensorlibraryname)
    sensoruserpath = getSensorUserPath(sensorname)
    if os.path.isdir(sensoruserpath):
        raise Exception(
            '%(sensorname)s allready exist in %(sensoruserpath)s' % locals()
        )

    copytree(sensorlibrarypath, sensoruserpath)

def saveto(filename, content):
    out = open(filename, 'wb')
    out.write(content)
    out.close()