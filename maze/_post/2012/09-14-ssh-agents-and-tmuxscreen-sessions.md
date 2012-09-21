---
title: SSH agents and tmux/screen sessions
category: hacking
---
Don't you wish SSH agent forwarding also kept working in between tmux/screen
sessions? It's easy!

In your ~/.bash_profile:

    :::bash
    # Link this session's agent
    umask 77
    mkdir -p ~/.ssh/auth
    if [ -n "$SSH_AUTH_SOCK" -a -e "$SSH_AUTH_SOCK" ]; then
            ln -sf $SSH_AUTH_SOCK ~/.ssh/auth/sock
            export SSH_AUTH_SOCK_OLD=$SSH_AUTH_SOCK
            export SSH_AUTH_SOCK=$HOME/.ssh/auth/sock
    fi

In your ~/.bash_logout:

    :::bash
    # Find the newest SSH agent that's not the one from this session
    find /tmp -name agent.* -user $USER -exec stat -f '%c %N' {} \; 2>/dev/null \
            | sort -n \
            | while read CTIME NAME; do
            if [ "$NAME" != "$SSH_AUTH_SOCK_OLD" ]; then
                    # Check if this socket is alive and working
                    SSH_AUTH_SOCK=$NAME ssh-add -l >/dev/null 2>&1
                    if [ $? -eq 0 ]; then
                            ln -sf $NAME ~/.ssh/auth/sock
                            unset SSH_AUTH_SOCK_OLD
                    fi
                    break
            fi
    done

    # If $SSH_AUTH_SOCK_OLD is still set, it did not work out. Remove the symlink
    if [ -n "$SSH_AUTH_SOCK_OLD" ]; then
        rm ~/.ssh/auth/sock
    fi

*[SSH]: Secure SHell
