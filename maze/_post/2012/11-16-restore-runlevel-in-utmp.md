---
title: Restore runlevel in utmp
category: hacking
---
Just a quick writeup as I did not find useful replies related to this issue. In
Red Hat 5 (and CentOS) there have been [various reports](http://m9.href.be/)
about tools having issues with utmp. We ran into this issue on multiple
occasions on our production systems.

Why is is a problem? Puppet.

The redhat.rb service provide in Puppet uses
[chkconfig](http://linux.die.net/man/8/chkconfig) to determine if a service
should run for a given runlevel. If you corrupt utmp, chkconfig will get
properly confused:

    # chkconfig puppet ; echo $?
    0
    # > /var/run/utmp # Don't do this!
    # chkconfig puppet ; echo $?
    cannot determine current run level
    1

This causes Puppet to start every service resource defined, on every Puppet
run. To "restore" the current runlevel information in utmp, we can switch to
init level 4 and back (assuming that your headless server defaults to runlevel
3):

    # runlevel || (telinit 4 && telinit 3 ; runlevel)
    unknown
    4 3

In Red Hat (and CentOS) you can check what services are possibly affected by
switching runlevels, using the very same chkconfig tool:

    # chkconfig --list | grep '[34]:on'
    acpid           0:off   1:off   2:on    3:on    4:on    5:on    6:off
    atd             0:off   1:off   2:off   3:on    4:on    5:on    6:off
    auditd          0:off   1:off   2:on    3:on    4:on    5:on    6:off
    crond           0:off   1:off   2:on    3:on    4:on    5:on    6:off
    diamond         0:off   1:off   2:on    3:on    4:on    5:on    6:off
    funcd           0:off   1:off   2:on    3:on    4:on    5:on    6:off
    ...

Now the runlevel information in utmp is restored, and chkconfig knows what to
do again:

    # chkconfig puppet ; echo $?
    0
