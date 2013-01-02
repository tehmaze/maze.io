---
title: lolcat
category: python
---
As a coding exercise, I decided to port lolcat to Python.
[lolcat](https://github.com/busyloop/lolcat) is originally written in Ruby and
heavily depends on the [Paint](https://github.com/janlelis/paint) module for
doing ANSI renditions. The Python port I did does not depend on anything else
but the default [Python stdlib](http://docs.python.org/2/library/).

It's a tool like cat, with added lulz, [get it while it's
hot](https://github.com/tehmaze/lolcat#readme)!

![](/images/post/lolcat.png)

Check out the ASCII cast at [ascii.io](http://ascii.io/a/1563).

Installing lolcat
-----------------

To install the stable version:

    :::bash
    $ pip install lolcat
