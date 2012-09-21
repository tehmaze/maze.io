---
title: Speed up RoundCube webmail
---
We have been using [RoundCube](http://roundcube.net/) webmail on various
occasions, it's a good looking, intuitive webmail interface with all the
fancyness you can expect from a modern webmail client. RoundCube can, at time,
be a bit sluggish with all the features enabled. You can speed up RoundCube
quite a bit.


Proxy IMAP connections
----------------------

With the [IMAP Proxy](http://imapproxy.org/) you can save a lot of connections
to your IMAP server. IMAP Proxy simply sits between your webmail server and
your IMAP server. It accepts connections from your webmail server for each
client login, then proxies that connection to your real IMAP server. When your
webmail client disconnects, IMAP Proxy will leave the connection open to the
IMAP server such that when your webmail client reconnects, the existing
connection may be re-used.

To start the IMAP Proxy on port 1143 on localhost, forwarding connections to
localhost:143:

    :::nginx
    listen_address          127.0.0.1
    listen_port             1143
    server_hostname         localhost
    server_port             143
    cache_size              3072
    cache_expiration_time   300
    proc_username           nobody
    proc_groupname          nogroup
    stat_filename           /var/run/pimpstats
    protocol_log_filename   /var/log/imapproxy_protocol.log
    syslog_facility         LOG_MAIL
    send_tcp_keepalives     no
    enable_select_cache     no
    foreground_mode         no
    force_tls               no
    chroot_directory        /var/lib/imapproxy/chroot
    enable_admin_commands   no


Enable caching
--------------

If your IMAP server is residing on a different machine, enable local caching in
the RoundCube main configuration:

    :::perl
    $rcmail_config['enable_caching'] = true;
    $rcmail_config['skip_deleted'] = false;


Cache static content
--------------------

You can make the webmail client cache all the scripts and images from RoundCube
by enabling mod_expires in your apache installation, now drop this .htaccess
file in your skins/ folder:

    :::apache
    ExpiresActive On
    ExpiresByType image/gif A86400
    ExpiresByType image/png A86400
    ExpiresByType text/css A86400
    ExpiresByType text/javascript A86400


Use an opcode cacher
--------------------

Opcode cachers such as [APC](http://pecl.php.net/APC/) (for Apache) and
[xCache](http://xcache.lighttpd.net/) (for lighttpd) can improve the speed of
PHP by quite a bit by caching the compiled bytecode of PHP scripts to avoid the
overhead of parsing and compiling source code on each request. To further
improve performance, the cached code is stored in shared memory and directly
executed from there, minimizing the amount of slow disk reads and memory
copying at runtime.


Do some basic database tuning
-----------------------------

RoundCube uses InnoDB by default, but the MySQL defaults for InnoDB are not
optimized for speed. You can get some performance gain by doing some basic
tuning:

    :::ini
    [mysqld]
    # If you’re not concerned about ACID and can loose transactions for last second
    # or two in case of full OS crash than set this value. It can dramatic effect
    # especially on a lot of short write transactions.
    innodb_flush_log_at_trx_commit  = 2

    # Avoid double buffering and reduce swap pressure, in most cases this setting
    # improves performance. Though be careful if you do not have battery backed up
    # RAID cache as when write IO may suffer.
    innodb_flush_method             = O_DIRECT

    # Even with current Innodb Scalability Fixes having limited concurrency helps.
    # The actual number may be higher or lower depending on your application and
    # default which is 8 is decent start
    innodb_thread_concurrency       = 8
