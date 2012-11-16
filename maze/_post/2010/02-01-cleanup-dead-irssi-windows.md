---
title: Clean up dead irssi windows
category: hacking
---
Quick oneliner to cleanup dead [irssi](http://irssi.org/) windows (split over
multiple lines to aid readability):

    :::perl
    /script exec foreach $w (sort {$b->{refnum} <=> $a->{refnum}} Irssi::windows()) {
      if ((!$w->items()) && !($w->{refnum} == 1)) {
        Irssi::print("window closing " . $w->{refnum});
        Irssi::command("window goto $w->{refnum}");
        Irssi::command("window close");
      }
    }

Please keep in mind that:

 *  application windows will be closed (like [twirssi](http://twirssi.org/)'s
    status, etc)

    > hint: `/window immortal ON`

 *  dead queries will be closed

 *  you should also take a look at `/set query_auto_close <SECONDS>`

    > hint: `/set query_auto_close 86400` to close a query after a day of inactivity


Some quick tips:

 *  use `/layout save` if you are happy, it makes irssi store your current layout

 *  use `/foreach query /unquery` to close all queries

    > tip: Habbie reported that this might crash irssi if you have lots of open
    > queries use `/set reuse_unused_windows ON` to "recycle" windows after they are
    > dead

 *  check out [quick tips for irssi+screen users](/2008/11/23/quick-tip-for-irssi+screen-users/)

 *  check out [irssi keyboard mapping](http://wordpress.maze.io/2009/10/15/irssi-keyboard-mapping)


Thanks #irssi for helping out. Happy chatting!
