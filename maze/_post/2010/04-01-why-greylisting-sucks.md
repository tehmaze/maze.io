---
title: Why greylisting sucks
category: hacking
---
Greylisting is a SPAM fighting technique that deliberately delays the mail flow
in the hope to block spammers. When a remote mailserver is seen for the first
time, a temporary error will be generated for a fixed amount of time (usually
somewhere between five and fifteen minutes). All of this in the hope to reject
mail from spammers, assuming they won’t retry delivering the e-mail.

In my opinion this is bad practice, and mail server operators should know
better! Why deliberately slow down the mail flow? Some reasons NOT to implement
greylisting…

## I want my mail and I want it now

If I’m using a web service that requires validation by e-mail for example, I
don’t want to have to wait another few minutes before I can continue the signup
process.

    :::syslog
    Apr  1 13:28:06 tazz postfix/smtp[20811]: 08BAE401BB: to=<xyz@xyz.com>,
    relay=xyz.com[216.66.a.b]:25, delay=206, delays=204/1.6/0.65/0.16,
    dsn=4.2.0, status=deferred (host xyz.com[216.66.a.b] said: 450 4.2.0
    <xyz@xyz.com>: Recipient address rejected: Greylisted, see
    http://postgrey.schweikert.ch/help/xyz.com.html (in reply to RCPT TO
    command))

Great, now I have to wait until the remote server is being recognized as a
trusted relay, which can take up to fifteen minutes!

## The validation process will break

My mail servers validate back if the envelope sender address is an actual
address. This is perfectly fine practice, as there is no reason to accept mail
originating from non-existing addresses. The mail server does this by
contacting a server that is handling the mail from the sender in parallel to
the receiving process (in-line). If that server greylists me, this validation
process will fail! Bad practice!

    :::syslog
    Apr  1 13:30:37 tazz postfix/smtpd[20990]: NOQUEUE: reject: RCPT from
    xyz.com[216.66.a.b]: 450 4.1.7 <xyz@xyz.com>: Sender address rejected:
    unverified address: host xyz.com[216.66.a.b] said: 450 4.2.0 <xyz@xyz.com>:
    Recipient address rejected: Greylisted, see
    http://postgrey.schweikert.ch/help/xyz.com.html (in reply to RCPT TO
    command); from=<xyz@xyz.com> to=<blackhole@maze.io> proto=ESMTP
    helo=<xyz.com>

The server has been greylisted, now I have to wait up to fifteen minutes before
I can properly validate the originating address. Narf.

## Security by obscurity

Although this technique might be effective in some cases, it won’t help
blocking spam sent through actual mail servers that implement proper back-off
and re-delivery attempts. This only helps against fire-and-forget type of spam
robots.

## Final thoughts

So mail admins, please disable greylisting, or I have to slap you with my rusty
cluebat! I know spam-figthing is a big issue and requires a big investment in
terms of time and dedication, but with greylisting techniques you’re mostly
annoying mail server administrators like myself and their users (complaining
about mail being slow, etc.).

## Blacklist

<s>I implemented a DNS-based Blackhole List for recipient domains that use
greylisting, as I no longer wish to relay for mail servers that have
greylisting enabled. You can find out more about the DNSBL at
http://mail.maze.io/greylist/</s> offline
