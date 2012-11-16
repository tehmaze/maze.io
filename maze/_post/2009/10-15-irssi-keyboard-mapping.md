---
title: irssi keyboard mapping
category: hacking
---
I like typing as little as possible, so I added this to my `~/.irssi/config` to
allow for quick window switching, some examples:

    <ESC>0: Switch to window 10
    <ESC>k: Switch to window 28
    <ESC>O: Switch to window 59

Now I can use my full QWERTY keyboard for window switching in
[irssi](http://irssi.org/)!

## Mappings

    :::perl
    keyboard = (
      { key = "meta-a"; id = "change_window"; data = "21"; },
      { key = "meta-s"; id = "change_window"; data = "22"; },
      { key = "meta-d"; id = "change_window"; data = "23"; },
      { key = "meta-f"; id = "change_window"; data = "24"; },
      { key = "meta-g"; id = "change_window"; data = "25"; },
      { key = "meta-h"; id = "change_window"; data = "26"; },
      { key = "meta-j"; id = "change_window"; data = "27"; },
      { key = "meta-k"; id = "change_window"; data = "28"; },
      { key = "meta-l"; id = "change_window"; data = "29"; },
      { key = "meta-;"; id = "change_window"; data = "30"; },
      { key = "meta-z"; id = "change_window"; data = "31"; },
      { key = "meta-x"; id = "change_window"; data = "32"; },
      { key = "meta-c"; id = "change_window"; data = "33"; },
      { key = "meta-v"; id = "change_window"; data = "34"; },
      { key = "meta-b"; id = "change_window"; data = "35"; },
      { key = "meta-n"; id = "change_window"; data = "36"; },
      { key = "meta-m"; id = "change_window"; data = "37"; },
      { key = "meta-,"; id = "change_window"; data = "38"; },
      { key = "meta-."; id = "change_window"; data = "39"; },
      { key = "meta-/"; id = "change_window"; data = "40"; },
      { key = "meta-!"; id = "change_window"; data = "41"; },
      { key = "meta-@"; id = "change_window"; data = "42"; },
      { key = "meta-#"; id = "change_window"; data = "43"; },
      { key = "meta-$"; id = "change_window"; data = "44"; },
      { key = "meta-%"; id = "change_window"; data = "45"; },
      { key = "meta-^"; id = "change_window"; data = "46"; },
      { key = "meta-&"; id = "change_window"; data = "47"; },
      { key = "meta-*"; id = "change_window"; data = "48"; },
      { key = "meta-("; id = "change_window"; data = "49"; },
      { key = "meta-)"; id = "change_window"; data = "50"; },
      { key = "meta-Q"; id = "change_window"; data = "51"; },
      { key = "meta-W"; id = "change_window"; data = "52"; },
      { key = "meta-E"; id = "change_window"; data = "53"; },
      { key = "meta-R"; id = "change_window"; data = "54"; },
      { key = "meta-T"; id = "change_window"; data = "55"; },
      { key = "meta-Y"; id = "change_window"; data = "56"; },
      { key = "meta-U"; id = "change_window"; data = "57"; },
      { key = "meta-I"; id = "change_window"; data = "58"; },
      { key = "meta-O"; id = "change_window"; data = "59"; },
      { key = "meta-P"; id = "change_window"; data = "60"; },
      { key = "meta-A"; id = "change_window"; data = "61"; },
      { key = "meta-S"; id = "change_window"; data = "62"; },
      { key = "meta-D"; id = "change_window"; data = "63"; },
      { key = "meta-F"; id = "change_window"; data = "64"; },
      { key = "meta-G"; id = "change_window"; data = "65"; },
      { key = "meta-H"; id = "change_window"; data = "66"; },
      { key = "meta-J"; id = "change_window"; data = "67"; },
      { key = "meta-K"; id = "change_window"; data = "68"; },
      { key = "meta-L"; id = "change_window"; data = "69"; },
      { key = "meta-:"; id = "change_window"; data = "70"; },
      { key = "meta-Z"; id = "change_window"; data = "71"; },
      { key = "meta-X"; id = "change_window"; data = "72"; },
      { key = "meta-C"; id = "change_window"; data = "73"; },
      { key = "meta-V"; id = "change_window"; data = "74"; },
      { key = "meta-B"; id = "change_window"; data = "75"; },
      { key = "meta-N"; id = "change_window"; data = "76"; },
      { key = "meta-M"; id = "change_window"; data = "77"; },
      { key = "meta-<"; id = "change_window"; data = "78"; },
      { key = "meta->"; id = "change_window"; data = "79"; },
      { key = "meta-?"; id = "change_window"; data = "80"; },
      { key = "meta-p"; id = "change_window"; data = "20"; },
      { key = "home"; id = "beginning_of_line"; data = ""; },
      { key = "end"; id = "end_of_line"; data = ""; },
      { key = "^R"; id = "command"; data = "history_search "; }
    );

