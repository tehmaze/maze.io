---
title: SSL IRC, is your connection really secure?
category: hacking
---
This article is about a wrong assumption I encounter quite often:

> "I am using SSL IRC, now I have a secure connection, right?"


The answer is: No, not really, or rather, really not. This only means you have
an ”encrypted” connection, you still have to take a few additional steps to
make sure your connection also is ”secure”.

The only thing your client does, is set up an encrypted connection to the IRC
server. Irssi does no verification by default, meaning, the ”secure” server
could be ”any secure server”. If one was to create a spoofed host that talks
SSL to your client, and proxing all traffic to one of the real IRC servers, you
wouldn’t notice.

## Setting up SSL IRC verification

This is an example for irc.mononoke.nl, we assume you are on a secure
connection. Best would be to ask the IRC administrators for their CA
certificates over a secure medium (email with verified PGP keys for example).
You can also retrieve the server (CA) certificates to verify your connection,
of course, this only is sane if you know you can trust the certificates
currently presented to you by the server(s). You can do by issuing:

    :::shell
    [user@ircbox ~]$ mkdir .irssi/ssl
    [user@ircbox ~]$ cd .irssi/ssl
    [user@ircbox ~/.irssi/ssl]$ wget -O mononoke-ca.crt \
        http://www.cacert.org/certs/root.crt
    [user@ircbox ~/.irssi/ssl]$ for SERVER in $(dig +short a irc.mononoke.nl); do
    >    echo "QUIT" \
    >        | openssl s_client -host $SERVER -port 6697 \
    >        >> mononoke-ca.crt 2>/dev/null
    > done
    [user@ircbox ~/.irssi/ssl]$

## Creating a client certificate

Create a client certificate and key, keep them safe!:

    :::shell
    [user@ircbox ~/.irssi/ssl]$ openssl req -nodes -newkey rsa:2048 \
        -keyout mononoke.key -x509 -days 365 -out mononoke.crt
    ... answer the questions ...
    [user@ircbox ~/.irssi/ssl]$ chmod 400 mononoke.key

## Tell irssi to use the files you just created

    :::irssi
    irssi> /network add mono-ix
    irssi> /server add -auto -ssl -ssl_cert ~/.irssi/ssl/mononoke.pem
           -ssl_verify -ssl_cafile ~/.irssi/ssl/mononoke-ca.crt
           -network mono-ix irc.mononoke.nl 6697

Now, if you would connect to a server with an invalid certificated (spoofed,
expired, etc.), irssi won’t accept the connection to the server:

    15:22:01 [mono-ix] Irssi: Reconnecting to irc.mononoke.nl [79.170.94.111]
              port 6697 - use /RMRECONNS to abort
    15:22:01 Irssi: warning Could not verify SSL servers certificate:
    15:22:01 Irssi: warning   Subject : /CN=*.mononoke.nl
    15:22:01 Irssi: warning   Issuer  : /O=CAcert
              Inc./OU=http://www.CAcert.org/CN=CAcert Class 3 Root
    15:22:01 Irssi: warning   MD5 Fingerprint :
              BA:88:E7:9E:77:F2:68:CE:9B:0E:0F:78:8E:4F:14:71
    15:22:01 [mono-ix] Irssi: Connection lost to irc.mononoke.nl
