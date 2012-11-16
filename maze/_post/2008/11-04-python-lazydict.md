---
title: Python LazyDict
category: python
---
I'm a great fan of the dot notation, instead of `foo['bar']` hash notation. Also
because the Django and Jinja templating engines use dot notation for all their
object attribute/key lookups.

You can also use assignments and lookups on a dictionary, using the `__setattr__`
and `__getattr__` methods:

    :::python
    class LazyDict(dict):
        def __getattr__(self, attr):
            if attr in self:
                return self[attr]
            else:
                raise AttributeError, "'%s' object has no attribute '%s'" \
                    % (self.__class__.__name__, attr)

        def __setattr__(self, attr, value):
            if hasattr(super(LazyDict, self), attr):
                raise AttributeError, "'%s' object already has attribute '%s'" \
                    % (self.__class__.__name__, attr)
            self[attr] = value

This allows you to do:

    :::python
    >>> from lazydict import LazyDict
    >>> foo = LazyDict()
    >>> foo.bar = 42
    >>> foo.bar
    42
    >>> foo.biz = LazyDict()
    >>> foo.biz.qux
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "lazydict.py", line 6, in __getattr__
    AttributeError: LazyDict instance has no attribute 'qux'
    >>> foo.biz.qux = object()
    >>> foo.biz.qux
    <object object at 0xb7d26468>
