---
title: SSH visual fingerprints
category: hacking
---
OpenSSH version 5.1 comes with a great new feature, namely visual fingerprint
identification. This helps you in recognizing and identifying changes in
fingerprints.

To enable visual fingerprinting for all your SSH sessions, add this to your
~/.ssh/config file:

    :::ssh
    Host *
        VisualHostKey yes

This gives you a pretty piece of ASCII art when connecting to a remote host:

    $ ssh labs.tehmaze.com
    Host key fingerprint is fb:24:0a:db:f3:10:d2:33:20:14:fb:43:52:1e:05:50
    +--[ RSA 2048]----+
    |  ++Eo.          |
    | . + .           |
    |  + +            |
    |   = o           |
    |    + = S        |
    |     o + .       |
    |    . . o .      |
    |     +.o +       |
    |    . oo. .      |
    +-----------------+

    Last login: Thu Oct  2 12:38:55 2008 from *.nl
    wijnand@drone:~$

Trying another host…

    $ ssh example
    Host key fingerprint is 99:a3:6f:96:78:9c:ef:d7:83:26:33:1f:bd:b0:c7:be
    +--[ RSA 2048]----+
    |                 |
    |                 |
    |                 |
    |         o       |
    |        S        |
    |       . .   .   |
    |      .o o  o+.  |
    |      ..B + ++=. |
    |       +.ooBooEo |
    +-----------------+

    Last login: Thu Oct  2 10:47:23 2008 from *.nl
    wijnand@example:~$

Isn’t it pretty?
