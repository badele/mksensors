About
-----

mksensors

Installation
============

All command must run with **root** account

.. code-block:: console

   wget -q --no-check-certificate https://raw.githubusercontent.com/badele/mksensors/master/scripts/setup.sh -O - | sudo bash -


Configure
=========

All command must run with **root** account

.. code-block:: console

   # Add sender
   # [Debian] apt-get install rrdtool python-dev librrd-dev
   sudo mksensors enable sender rrd
   sudo mksensors enable sender log

   # Add sensors
   sudo mksensors sensor new testping sensor.network.ping --param="'hostnames': ['8.8.8.8', '8.8.4.4']"
   sudo mksensors sensor new isup sensor.network.isup --param="'hostnames': ['host1.int.dns', '192.168.1.2']"

   # Restart mksensors services
   sudo systemctl restart mksensors

   # Show running sensors
   sudo mksensorsctl status