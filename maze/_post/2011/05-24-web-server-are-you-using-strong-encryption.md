---
title: Are you using strong encryption?
---
Most of the analysed websites by [Qualys](http://www.qualys.com/) that are
using SSL are still using SSLv2 or even SSLv1 for their encryption. SSLv2
standards were formed in 1995 and can be called outdated without a doubt.
Therefor it is recommended to use at least TLSv1 (which is dated back in 1999,
but hey) but rather TLSv1.2.  Unfortunately TLSv1.2 still has limited (server)
support, so let's take a look on how to secure [nginx](http://nginx.org/) by
using TLSv1 and strong ciphers.

nginx supports strong encryption by default, to enable it put this in your
server section:

    :::nginx
    server {
        listen                  0.0.0.0:443 default ssl;

        ssl_certificate         /etc/ssl/nginx.crt;
        ssl_certificate_key     /etc/ssl/private/nginx.key;

        # Enable SSL session cache
        ssl_session_cache       shared:SSL:10m;
        ssl_session_timeout     5m;

        # Only new protocols and strong ciphers
        ssl_protocols           TLSv1;

        # Only accept strong ciphers, but disable the weaker ADH and MD5 ciphers
        ssl_ciphers             HIGH:!ADH:!MD5;
        ssl_prefer_server_ciphers on;

        # Enable STS, http://8n.href.be/
        add_header              Strict-Transport-Security max-age=500;

        # ... add the rest of your configuration here
    }

You can test your setup by using the free 
[SSL Server Test](https://www.ssllabs.com/ssldb/index.html)
by Qualys, [my setup](https://www.ssllabs.com/ssldb/analyze.html?d=maze.io)
currently gets a class A rating with a score of 87.
