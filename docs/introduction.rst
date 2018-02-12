############
Introduction
############

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
