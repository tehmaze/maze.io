---
title: Generating CRC32 in Python
category: python
---
Unfortunately, Python does not know about signedness and assumes all integers
are signed. I wanted to get a CRC32 hexadecimal checksum for some files.

Oddly, the mechanisms for the CRC32 checksumming are in the zlib package. There
is also a version in binascii, but this algorithm looks slower (might depend on
Python version and CPU architecture). Why doesn't this algorithm reside in the
hashlib module?

This is how you generate a CRC32 checksum (to check .sfv files for example):

    :::python
    >>> import zlib
    >>> hash = zlib.crc32('hi there!')
    >>> hash = zlib.crc32('more data', hash)
    >>> print '%08X' % (hash & 0xFFFFFFFF,)
    31A783A9

## Speed comparison

    :::python
    >>> import timeit
    >>> f = '''
    hash = crc32('')
    for x in xrange(0, 10):
        hash = crc32('%04d' % (x,), hash)
    '''
    >>> t = timeit.Timer(stmt=f, setup='from binascii import crc32')
    >>> print "%.2f usec/pass" % (1000000 * t.timeit(number=100000)/100000)
    19.12 usec/pass
    >>> t = timeit.Timer(stmt=f, setup='from zlib import crc32')
    >>> print "%.2f usec/pass" % (1000000 * t.timeit(number=100000)/100000)
    17.23 usec/pass
