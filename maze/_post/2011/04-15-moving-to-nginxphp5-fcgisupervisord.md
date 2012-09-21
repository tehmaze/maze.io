---
title: Moving to nginx/php5-fcgi/supervisord
---
Some collegues have been pushing me to try out [nginx](http://nginx.org/). I
hesitated for quite a while, but I figured to see and try it out. Coming from
apache one could just lazily install mod_php and mod_wsgi for all PHP and
Python needs, in nginx you need a bit more complicated setup.

Running PHP, welcome supervisord
--------------------------------

I have been a fan of D. J. Bernstein's
[daemontools](http://cr.yp.to/daemontools.html) for process control. That is,
until I learned about [supervisord](http://supervisord.org/). Supervisord
allows one not only to start daemons, but it also allows you to set up and
control FastCGI processes. My FastCGI php configuration looks something like:

    :::ini
    [fcgi-program:php5-fcgi]
    socket=tcp://127.0.0.1:9000
    command=/usr/bin/php5-fcgi
    numprocs=8
    priority=999
    process_name=%(program_name)s_%(process_num)02d
    user=www-data
    autorestart=true
    autostart=true
    startsecs=1
    startretries=3
    stopsignal=QUIT
    stopwaitsecs=10
    redirect_stderr=true
    stdout_logfile=/var/log/supervisor/php5-fcgi.log
    stdout_logfile_maxbytes=100MB

The /usr/bin/php5-fcgi binary is a small wrapper around Debian's php5-cgi
binary, to pass some FastCGI settings to the process:

    :::bash
    #! /bin/sh
    export PHP_FCGI_MAX_REQUESTS=128
    export PHP_FCGI_CHILDREN=2
    exec /usr/bin/php5-cgi "$@"


Tell your nginx vhost to pass PHP to the daemon
-----------------------------------------------

Now you can tell nginx to pass all requests to .php files to the FastCGI daemon
process:

    :::nginx
    location ~ \.php {
        include                 fastcgi_params;
        keepalive_timeout       0;
        fastcgi_param           SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        fastcgi_pass            127.0.0.1:9000;
    }


Running Python, using mod_wsgi
------------------------------

Luckily, nginx also has a [mod_wsgi](http://wiki.nginx.org/NginxNgxWSGIModule)
module available, after installing, instruct nginx to use wsgi:

    :::nginx
    server {
        listen       8000;
        server_name  localhost;

        wsgi_var  REQUEST_METHOD      $request_method;
        wsgi_var  QUERY_STRING        $query_string;
        wsgi_var  CONTENT_TYPE        $content_type;
        wsgi_var  CONTENT_LENGTH      $content_length;
        wsgi_var  SERVER_NAME         $server_name;
        wsgi_var  SERVER_PORT         $server_port;
        wsgi_var  SERVER_PROTOCOL     $server_protocol;

        #
        # additional variables
        # (they will be present in the WSGI environment only if not empty)
        #
        wsgi_var  REQUEST_URI         $request_uri;
        wsgi_var  DOCUMENT_URI        $document_uri;
        wsgi_var  DOCUMENT_ROOT       $document_root;
        wsgi_var  SERVER_SOFTWARE     $nginx_version;
        wsgi_var  REMOTE_ADDR         $remote_addr;
        wsgi_var  REMOTE_PORT         $remote_port;
        wsgi_var  SERVER_ADDR         $server_addr;

        wsgi_var  REMOTE_USER         $remote_user;

        location  / {
            wsgi_pass /path/to/wsgi.py;

            wsgi_pass_authorization off;
            wsgi_script_reloading on;
            wsgi_use_main_interpreter on;
            }
        }
    }
