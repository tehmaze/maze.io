---
title: getent-0.2
category: python
---
With the help of [Olivier Cortès](http://oliviercortes.com/) the
[getent](https://pypi.python.org/pypi/getent) library now also works in Python
3! The library offers a Python interface to the POSIX getent family of commands
(getpwent, getgrent, getnetent, etc.)

Examples
--------

Example usage:

    :::python
    >>> import getent
    >>> print dict(getent.passwd('root'))
    {'dir': '/root',
     'gecos': 'root',
     'gid': 0,
     'name': 'root',
     'password': 'x',
     'shell': '/bin/bash',
     'uid': 0}
    >>> print dict(getent.group('root'))
    {'gid': 0, 'members': [], 'name': 'root', 'password': 'x'}

Links
-----

*  [Download getent-0.2](https://pypi.python.org/packages/source/g/getent/getent-0.2.tar.gz)
*  [Bug tracker](https://github.com/tehmaze/getent/issues)
