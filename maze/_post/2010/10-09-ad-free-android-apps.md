---
title: Ad-free Android apps
---
Sick of all the (Google) ads in your Android apps? So am I, long live squid as
a transparent proxy.

Add this to your squid.conf:

    :::squid
    http_port 127.0.0.1:3129 transparent
    acl google_crap_path    urlpath_regex   ^pagead/
    acl google_crap_path    urlpath_regex   ^pageads/
    acl google_crap         dstdomain       adwords.google.com
    acl google_crap         dstdomain       pagead.googlesyndication.com
    acl google_crap         dstdomain       pagead2.googlesyndication.com
    acl google_crap         dstdomain       adservices.google.com
    acl google_crap         dstdomain       imageads.googleadservices.com
    acl google_crap         dstdomain       imageads1.googleadservices.com
    acl google_crap         dstdomain       imageads2.googleadservices.com
    acl google_crap         dstdomain       imageads3.googleadservices.com
    acl google_crap         dstdomain       imageads4.googleadservices.com
    acl google_crap         dstdomain       imageads5.googleadservices.com
    acl google_crap         dstdomain       imageads6.googleadservices.com
    acl google_crap         dstdomain       imageads7.googleadservices.com
    acl google_crap         dstdomain       imageads8.googleadservices.com
    acl google_crap         dstdomain       imageads9.googleadservices.com
    acl google_crap         dstdomain       www.googleadservices.com
    http_access deny google_crap
    http_access deny google_crap_path

Now, work the magic with your firewall, mine is pf on OpenBSD 4.7:

    :::pf
    # Proxy
    pass in  quick on $if_local proto tcp \
             from any to !$net_local port 80 \
             rdr-to 127.0.0.1 port 3129
