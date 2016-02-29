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

All command must run with **root** account.

Flow process example

.. code-block:: console

   # List available senders
   sudo mksensors list senders

   # | Sender name   | Description                          | Enabled   |
   # |---------------+--------------------------------------+-----------|
   # | log           | Write sensors values in one log file | Yes       |
   # | mqtt          | Send sensors values to Mqtt broker   |           |
   # | rrd           | Write sensors values in the RRD file |           |
   # | file          | Write sensors values in the file     |           |

   # Add senders
   sudo mksensors enable sender rrd
   sudo mksensors enable sender log

   # List available sensors from mksensors template
   sudo mksensors list sensors

   # | Sensor name   | Description                    | Used by                                |
   # |---------------+--------------------------------+----------------------------------------|
   # | network.isup  | Return if the hosts are online | mks_officeisup.conf, mks_homeisup.conf |
   # | network.ping  | Return ping result             | mks_netquality.conf                    |

   # Add sensors
   sudo mksensors enable sensor testping network.ping
   sudo mksensors enable sensor isup network.isup

   # Check if configuration is correctly configured before starting the mksensors service
   sudo mksensors check

   # Restart mksensors services
   sudo systemctl restart mksensors

   # Show running sensors
   sudo mksensorsctl status