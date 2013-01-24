---
title: natural-0.1.3
category: python
---
Just pushed version 0.1.3 of the
[natural](https://pypi.python.org/pypi/natural) project to PyPi and GitHub.
With this version we ironed out bugs in the duration calculation thanks to the
great help of [David Beitey](https://github.com/davidjb).

The natural project provides convenience functions to convert data to their
human readable form. Natural is fully gettext aware, so with your help it can
also be available in [your
language](http://natural.readthedocs.org/en/latest/locales.html)!

Examples
--------

Basic usage:

    :::python
    >>> from natural.file import accessed
    >>> print accessed(__file__)
    just now

We speak your language ([with your support](http://natural.readthedocs.org/en/latest/locales.html)):

    :::python
    >>> import locale
    >>> locale.setlocale(locale.LC_MESSAGES, 'nl_NL')
    >>> print accessed(__file__)
    zojuist


Links
-----

*  [Download natural-0.1.3](http://pypi.python.org/packages/source/n/natural/natural-0.1.3.tar.gz)
*  [Documentation](http://natural.readthedocs.org/)
*  [Bug tracker](https://github.com/tehmaze/natural/issues)
