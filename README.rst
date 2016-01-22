About
-----

mksensors

Installation
============

**On Raspbery PI or Debian/Ubuntu**

All command must run in **root**

.. code-block:: console

   apt-get install git python-pip
   pip install -U git+git://github.com/badele/mksensors.git
   mksensors init


Configure
=========

**On Raspbery PI or Debian/Ubuntu**

All command must run in **root**

.. code-block:: console

   # Add sender
   apt-get install rrdtool python-dev librrd-dev
   mksensors sender new sender.log --param="'location': '/usr/local/mksensors/log'"
   mksensors sender new sender.rrd --param="'location': '/usr/local/mksensors/rrd'"

   # Add sensors
   mksensors sensor new testping sensor.network --force --param="'hostnames': ['8.8.8.8', '8.8.4.4']"
