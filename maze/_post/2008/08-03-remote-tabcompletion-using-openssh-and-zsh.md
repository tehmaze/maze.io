---
title: Remote tabcompletion using OpenSSH and zsh
category: development
---
The [zsh](http://zsh.org/) shell comes with (more than one) great feature(s),
such as remote tabcompletion. If you for example want to copy a file over scp,
simply hit tab at any part of the filename on the remote host. zsh is able to
establish an ssh session on the background, and fetch the related information
for you, so you can tabcomplete trough the remote files.

This works best if you have set up a few things, including: Use ssh shared keys
(in combination with ssh-agent) Enable remote tabcompletion in zsh Enable
control connections in your OpenSSH client (optional) I’m not going to cover
how to use shared keys here, just [Google for "ssh shared
keys"](http://lmgtfy.com/?q=ssh+shared+keys) and you will find plenty examples.

To enable the remote tabcompletion in your zsh shell, add the following to your
~/.zshenv file:

    :::zsh
    # ssh, scp, ping, host
    zstyle ':completion:*:scp:*' tag-order \
          'hosts:-host hosts:-domain:domain hosts:-ipaddr:IP\ address *'
    zstyle ':completion:*:scp:*' group-order \
          users files all-files hosts-domain hosts-host hosts-ipaddr
    zstyle ':completion:*:ssh:*' tag-order \
          users 'hosts:-host hosts:-domain:domain hosts:-ipaddr:IP\ address *'
    zstyle ':completion:*:ssh:*' group-order \
          hosts-domain hosts-host users hosts-ipaddr

    zstyle ':completion:*:(ssh|scp):*:hosts-host' ignored-patterns \
          '*.*' loopback localhost
    zstyle ':completion:*:(ssh|scp):*:hosts-domain' ignored-patterns \
          '<->.<->.<->.<->' '^*.*' '*@*'
    zstyle ':completion:*:(ssh|scp):*:hosts-ipaddr' ignored-patterns \
          '^<->.<->.<->.<->' '127.0.0.<->'
    zstyle ':completion:*:(ssh|scp):*:users' ignored-patterns \
          adm bin daemon halt lp named shutdown sync
    If you also want tab completion of the hosts listed in your ~/.ssh/known_hosts and /etc/hosts files, you can add:

    zstyle -e ':completion:*:(ssh|scp):*' hosts 'reply=(
          ${=${${(f)"$(cat {/etc/ssh_,~/.ssh/known_}hosts(|2)(N) \
                          /dev/null)"}%%[# ]*}//,/ }
          ${=${(f)"$(cat /etc/hosts(|)(N) <<(ypcat hosts 2>/dev/null))"}%%\#*}
          ${=${${${${(@M)${(f)"$(<~/.ssh/config)"}:#Host *}#Host }:#*\**}:#*\?*}}
          )'

## The following part is optional

Using control connections in your OpenSSH client can speed things up. This
feature will tunnel all succeeding connections to a remote host over one single
connection, once an ssh session has been established. This saves you the delay
that comes with establishing and negotiating an ssh session every time you hit
tab.

To enable the control connection in your OpenSSH client configuration
(`~/.ssh/config`), please not that you need OpenSSH version 4 or newer for this
functionality:

    :::ssh
    Host *
        ControlPath ~/.ssh/master-%r@%h:%p
        ControlMaster auto

And you're all set! Have fun.
