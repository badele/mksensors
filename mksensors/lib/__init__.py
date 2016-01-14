#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Bruno Adelé <bruno@adele.im>'
__copyright__ = 'Copyright (C) 2016 Bruno Adelé'
__description__ = """Tool for easily create sensors daemons"""
__license__ = 'GPL'
__version__ = '0.0.1'

import os

SUPERVISOCONF = '/etc/supervisord.d'

def loadModule(modulename):
    # Try to load the sensor module
    try:
        mod = __import__(modulename, fromlist=[modulename])
    except ImportError:
        raise Exception("Can't Load module %s" % modulename)

    return mod


def getRootMKS():
    """Get root mksensors python project"""

    return os.path.abspath(os.path.join(__file__, '../..'))


def getSensorLibraryPath(sensorlibraryname):
    """Get main sensor python project file"""

    rootmks = os.path.abspath(os.path.join(__file__, '../..'))
    sensorlibrarypath = sensorlibraryname.replace('.', '/')

    sensorfilename = "%(rootmks)s/%(sensorlibrarypath)s/__init__.py" % locals()

    return sensorfilename


def createSupervisorConf(sensorname, sensorlibraryname, **kwargs):
    """Create supervisor conf for sensor"""

    # Add parameters
    kwargs['sensorname'] = sensorname
    kwargs['sensorcmd'] = getSensorLibraryPath(sensorlibraryname)

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


def saveto(filename, content):
    out = open(filename, 'wb')
    out.write(content)
    out.close()