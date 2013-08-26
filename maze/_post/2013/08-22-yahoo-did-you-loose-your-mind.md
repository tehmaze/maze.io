---
title: Yahoo! Did you loose your mind?
category: stuff
---
Today the IETF draft
[draft-ietf-appsawg-rrvs-header-field](https://datatracker.ietf.org/doc/draft-ietf-appsawg-rrvs-header-field/)
came to my attention. From the *about* section:

> This document defines an email header field, ``Require-Recipient-Valid-Since``,
> to provide a method for senders to indicate to receivers the time when the
> sender last confirmed the ownership of the target mailbox.  This can be used
> to detect changes of mailbox ownership, and thus prevent mail from being
> delivered to the wrong party.
>
> The intended use of this header field is on automatically generated messages
> that might contain sensitive information.

Well, that sounds reasonable right? Spoiler alert: it's a very bad idea.

## Social engineering

The draft will allow an e-mail sender to only have the mail accepted if the
account was created before a given date. In the _Privacy considerations_
section does not mention any means to effectively prevent attackers from
probing for account creation dates by simply iterating over a range of possible
dates. This means that you'll get a whole new attack vector in social
engineering.

> "Yes hello, this is Steve from Yahoo! calling about the account you created
> on December 3rd 2011. We need to verify your password ..."

## Data mining

So when companies that interact with users via e-mail want to implement this
header in their password reset e-mails, what date would you typically use to
put in the header? The date the user signed up, obviously. This is a nice data
source to start mining to extend the ever growing market dealing in personal
information. I'm not sure what an effective counter measure would be, maybe use
the last time the user signed in. Any ideas?

## Spoofing

As most know, e-mail is not exactly reliable and can be [easily
spoofed](http://en.wikipedia.org/wiki/Email_spoofing). The draft mentions this
in the _Abuse Countermeasures_ section, but offers no real solution. So if you
chose to use this header, please make sure it's properly signed with
[DomainKeys Identified Mail](http://www.dkim.org/) (or DKIM).

## Just admit your mistake, Yahoo!

So Yahoo! [announced on
Tumblr](http://yahoo.tumblr.com/post/52805929240/yourname-yahoo-com-can-be-yours)
that they'll be deleting unused accounts from their system that have been idle
for an arbitrary period of 12 months. That's not bad per see, why keep
collecting e-mails filling up your systems for active accounts right? But here
comes the ugly part: the account ID becomes available for registration again!

To band aid the problem Yahoo! released the first version of
[draft-wmills-rrvs-header-field](https://datatracker.ietf.org/doc/draft-wmills-rrvs-header-field/)
in the beginning of August 2013. In stead of admitting they made a huge mistake
by allowing people to "steal" other peoples identities (most web applications
use your e-mail address as a unique identifier), they figured there would be a
techincal solution to their problem.

## Maybe it's not too late

So Yahoo! please retract your draft from the IETF board and admit you've made a
huge mistake. It's not too late, you know. But to be honest most big
corporations will feel the need to protect their poor users
and implement this header anyway.
