.. Clickpecker Device Manager documentation master file, created by
   sphinx-quickstart on Sat Feb 10 21:07:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

   
Welcome to Clickpecker Device Manager's documentation!
======================================================

Launching
=========

Use ``docker`` and ``docker-compose`` to launch the device manager::

  docker-compose up -d --build

Device manager will be available from ``127.0.0.1/5000``.

Image building proccess may take a long time because of ``minicap`` and ``minitouch`` building.

API Reference
=============

.. autoflask:: device_manager.app:app
   :undoc-static:

.. _filters-specification:

Filtering
=========

Clickpecker Device Manager allows to find specific device by filters.

``POST`` request to ``/``, ``/acquire``, ``/release`` endpoints should contain
JSON object with ``"filters"`` object inside.

**Example**:

.. sourcecode:: json

    {
        "filters": {
            "android_version__gt": "4.2.0",
            "android_version__le": "7.1.1"
        }
    }

This filter will find devices with Android version > 4.2.0 and <= 7.1.1.

Filters support all fields returned by ``GET /``, and standard Python comparsion
operators ``eq``, ``lt``, ``gt``, ``le``, ``ge``. Operators should be divided from
fields by double underline as in example above. If operator is omitted, ``eq`` will
be used.

Configuration
=============

Some Device Manager's parameters can be configured via ``configs/device_manager.conf``.

start_port, max_devices
  Specifies the range ``[sart_port; start_port + 2 * max_devices]`` of available ports. 

minicap_root, minitouch_root
  Specifies path to minicap and minitouch binaries.

whitelist_devices, blacklist_devices
    * If ``whitelist`` is not empty, only devices with specified ADB ID will be available. ``blacklist`` will be ignored.
    * If ``whitelist`` is empty, devices with ADB ID, specified in ``blacklist`` will be unavailable.
    * If both lists are empty, all connected devices will be available.

