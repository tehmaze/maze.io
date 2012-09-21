---
title: zsh: for lazy system administrators
---
Another cool [zsh](http://zsh.org/) trick. As I am hopping to all kinds of
machines all day long in my role as UNIX system administrator, for convenience,
I can now just type the hostname into my shell.

Previously:

    :::bash
    ~% localhost
    zsh: command not found: localhost

After installing this into my ~/.zshrc:

    :::bash
    #
    #                         _______
    #   ____________ _______ _\__   /_________       ___  _____
    #  |    _   _   \   _   |   ____\   _    /      |   |/  _  \
    #  |    /   /   /   /   |  |     |  /___/   _   |   |   /  /
    #  |___/___/   /___/____|________|___   |  |_|  |___|_____/
    #          \__/                     |___|
    #
    #
    # Put this in your ~/.zshrc or ~/.bashrc:
    #   source ~/.zsh/ssh
    #
    # (c) 2011 Wijnand Modderman-Lenstra <maze@pyth0n.org>
    # MIT License
    #

    is_ip() {
        IP="$1"
        python - "${IP}" <<EOF
    import socket
    import sys 
    # Check IPv6
    if socket.has_ipv6:
        try:
            socket.inet_pton(socket.AF_INET6, sys.argv[1])
            sys.exit(0)
        except socket.error:
            pass
    # Check IPv4
    try:
        socket.inet_pton(socket.AF_INET, sys.argv[1])
        sys.exit(0)
    except socket.error:
        sys.exit(1)
    EOF
        return $?
    }

    try_connect_ssh() {
        # If only one argument is supplied and $1 resolves into a hostname,
        # connect there using ssh 
        if [[ $# -gt 0 ]]; then
            RESOLVES=$(host -W 2 $1 2>/dev/null | grep -v NXDOMAIN)
            if [ -z "${RESOLVES}" ]; then
                if is_ip "$1"; then
                    RESOLVES="$1"
                fi  
            fi  
            if [ $? -eq 0 -a -n "${RESOLVES}" ]; then
                ssh "$@"
                # Tell zsh we did handle the command
                return 0
            fi  
        fi  
    .
        # Tell zsh we didn't handle the command
        return 1
    }

    case "${SHELL}" in
        */zsh)
            command_not_found_handler() {
                try_connect_ssh "$@"
                return $?
            }   
            ;;  
        */bash)
            command_not_found_handle() {
                try_connect_ssh "$@"
                return $?
            }   
            ;;  
    esac

Now we get:

    :::bash
    ~% localhost
    Last login: Tue Jul 12 09:40:29 2011
    ~%
