---
title: ipcalc-1.0.0
category: python
---
The [ipcalc](https://pypi.python.org/pypi/ipcalc) has reached version 1.0! The
API is stable enough for a 1.x release now. There are no API changes between
the 0.x and 1.x versions, if such changes may occur we will switch to a new
major version.

Examples
--------

Example usage:

    ::: python
    >>> import ipcalc
    >>> for x in ipcalc.Network('172.16.42.0/30'):
    ...     print str(x)
    ...
    172.16.42.1
    172.16.42.2
    >>> subnet = ipcalc.Network('2001:beef:babe::/48')
    >>> print str(subnet.network())
    2001:beef:babe:0000:0000:0000:0000:0000
    >>> print str(subnet.netmask())
    ffff:ffff:ffff:0000:0000:0000:0000:0000
    >>> '192.168.42.23' in Network('192.168.42.0/24')
    True
    >>> long(IP('fe80::213:ceff:fee8:c937'))
    338288524927261089654168587652869703991L

Links
-----

*  [Download ipcalc-1.0.0](http://pypi.python.org/packages/source/i/ipcalc/ipcalc-1.0.0.tar.gz)
*  [Documentation](http://ipcalc.readthedocs.org/)
*  [Bug tracker](https://github.com/tehmaze/ipcalc/issues)
