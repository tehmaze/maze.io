---
title: Restricting directory in Apache per logged in user
category: hacking
---
Sometimes you wonder why such seemingly simple problems have to end up in such
complex solutions. For example [Apache][]'s
[mod_rewrite](http://httpd.apache.org/docs/2.2/mod/mod_rewrite.html). The
engine allows for parameter substitution in the RewriteCond and RewriteRule
options, but its use is restricted to the left hand argument. [Apache][] states:
Remember: `CondPattern` is a perl compatible regular expression with some
additions.

There are
[plenty](http://mail-archives.apache.org/mod_mbox//httpd-users/200904.mbox/%3C49EF63E9.4060106@ice-sa.com%3E)
[examples](http://mail-archives.apache.org/mod_mbox//httpd-users/200906.mbox/4A4A77A1.1080202@ice-sa.com)
of people with similar issues, I’ve also seen a few upstream patches to the
[Apache][] source tree, but apparently they never made it to an [Apache][] release.

Well, four hours, a lot of frustration and some rage later, we came to a
solution thanks to [jink][]:

    :::apache
    # Restrict /home/* to /home/%{REMOTE_USER} access only
    RewriteEngine On
    RewriteCond %{REQUEST_URI} ^/home/(?:|README\.x?html?|index\..+)$
    RewriteRule ^.* - [L]
    RewriteCond %{LA-U:REMOTE_USER} ^(.+)
    RewriteCond %1:/home/$1 !^([^:]+):/home/\1$
    RewriteRule ^/home/([^/]+) - [F,L]

You want me to explain this? Right, here we go.

Firstly, we want `/home/` still to be accessible, so the user can enlist its own
directory, we do this simply by comparing to the `REQUEST_URI`:

    :::apache
    RewriteCond %{REQUEST_URI} ^/home/(?:|README\.x?html?|index\..+)$
    RewriteRule ^.* - [L]

Now for the interesting part, [Apache][] uses `%{LA-U:...}` construction to allow
the mod_rewrite parser to prefetch these variables before evaluating the
rewrite chain. We store the result of the `REMOTE_USER` value in `%1`. [Apache][] on
the `%{LA-U:...}` construction:

> `%{LA-U:variable}` can be used for look-aheads which perform an internal
> (URL-based) sub-request to determine the final value of variable. This can be
> used to access variable for rewriting which is not available at the current
> stage, but will be set in a later phase.

> For instance, to rewrite according to the `REMOTE_USER` variable from within
> the per-server context (httpd.conf file) you must use `%{LA-U:REMOTE_USER}` -
> this variable is set by the authorization phases, which come after the URL
> translation phase (during which mod_rewrite operates).

Secondly, we append `:/home/.*` to the `REMOTE_USER` part stored in `%1`, and
compare this to a regular expression. If there is no match, the `RewriteRule`
kicks in and throws a HTTP 403 Forbidden. Simple... right? &lt;/sarcasm&gt;:

    :::apache
    RewriteCond %{LA-U:REMOTE_USER} ^(.+)
    RewriteCond %1:/home/$1 !^([^:]+):/home/\1$
    RewriteRule ^/home/([^/]+) - [F,L]

Combined with [mod_dav](http://www.webdav.org/mod_dav/) this gives me the
possibility to give a per-user share to authenticated users, I wanted to
provide an access method to files which are accessible on any platform from any
network. As most providers and network operators allow HTTP(S), [WebDAV][] seems
like a logical choice. As icing on the cake, Mac OSX supports [WebDAV][] access
natively (by entering the URL in Finder’s network connect), also iCalendar and
other tools allow for [WebDAV][] access which provides a great way to publish your
calendars to a trusted source!

A full Virtual Host example reads:

    :::apache
    <VirtualHost *:80>
        ServerName docs.maze.io
        DocumentRoot /export/docs
        <Directory /export/docs>
            # No .htaccess allowed
            AllowOverride None

            # Authenticate through LDAP
            AuthType basic
            AuthName "docs area"
            AuthBasicProvider ldap
            AuthLDAPBindDN "userid=apache,dc=maze,dc=io"
            AuthLDAPBindPassword "secret"
            AuthLDAPURL "ldaps://ldap.net.maze.io/dc=maze,dc=io"
            AuthLDAPGroupAttribute memberUid
            AuthLDAPGroupAttributeIsDN off
            Require ldap-group cn=docs,ou=Groups,dc=maze,dc=io

            # Enable WebDAV
            DAV On
        </Directory>

        # Restrict /home/* to /home/%{REMOTE_USER} access only
        RewriteEngine On
        RewriteCond %{REQUEST_URI} ^/home/(?:|README\.x?html?|index\..+)$
        RewriteRule ^.* - [L]
        RewriteCond %{LA-U:REMOTE_USER} ^(.+)
        RewriteCond %1:/home/$1 !^([^:]+):/home/\1$
        RewriteRule ^/home/([^/]+) - [F,L]
    </VirtualHost>

[Apache]: http://httpd.apache.org/
[jink]:   http://twitter.com/mrjink
[WebDAV]: http://www.webdav.org/
