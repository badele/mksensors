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
   sudo mksensors enable sensor testping network.ping
   sudo mksensors enable sensor isup network.isup

   # Restart mksensors services
   sudo mksensors check
   sudo systemctl restart mksensors

   # Show running sensors
   sudo mksensorsctl status