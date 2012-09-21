---
title: One less GNU tool: tmux replacing screen
---
So, you are busy working on a project, switch between browser and your vim
session running in a screen back and forward. You continously resize the
terminal and switch tabs, then you switched back to your vim session running in
a screen and ... boom! Screen is dead once again.

Obviously GNU screen has not been able to fix these kinds of issues for years,
but luckily [tmux](http://tmux.sourceforge.net/) is a very good alternative.
You can even make tmux act like screen by replacing some of the key bindings!

Here is my tmux.conf:

    :::config
    # c-b .. really?
    set-option -g prefix C-a

    # c-a c-a for the last active window
    bind-key C-a last-window

    # command sequence for nested tmux sessions
    bind-key a send-prefix

    # start window numbering at 1
    set -g base-index 1

    # faster command sequences
    set -s escape-time 0

    # aggressive resize
    setw -g aggressive-resize on

    # longer show time for messages
    set -g display-time 2000

    # different message colors
    set -g message-bg red
    set -g message-fg white

    # default statusbar colors
    set -g status-fg white
    set -g status-bg default
    set -g status-attr default

    # status extras
    set -g status-left ' #[fg=yellow,bold]%Y-%m-%d %H:%M#[fg=black,bold] |#[default]#[fg=cyan] %A #[fg=black,bold]|#[default]#[fg=green,bold] #(cut -d " " -f1-3 </proc/loadavg)#[default]'
    set -g status-left-length 50
    set -g status-right ''
    set -g status-right-length 0
    set -g status-justify right
