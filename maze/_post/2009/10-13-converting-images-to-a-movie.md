---
title: Converting images to a movie
category: hacking
---
My good friend zarya had a couple of webcams positioned to capture frames of
the work being done on his parent’s house. Four cameras have been capturing
images every five minutes for four months in total. This resulted in a giant
pile of stills… Very nice, but not very usable, so we spent some time creating
animated sequences of them.

## Step 1: determine frame-rate

We have an image every 5 minutes, so that’s 12 frames per minute. In order to
be able to see what is happening on the camera’s, we decided to use a framerate
of 10 fps.

## Step 2: mencoder, stich!

Now we can use mencoder to start stiching the movie to an AVI file:

    :::shell
    $ mencoder mf://cam1/*/*/*.jpg -mf fps=10:type=jpg \
        -ovc lavc -oac copy -o cam1.avi
    MEncoder dev-SVN-r26940 (C) 2000-2008 MPlayer Team
    CPU: Intel(R) XEON(TM) CPU 2.40GHz (Family: 15, Model: 2, Stepping: 4)
    CPUflags: Type: 15 MMX: 1 MMX2: 1 3DNow: 0 3DNow2: 0 SSE: 1 SSE2: 1
    Compiled with runtime CPU detection.
    success: format: 16  data: 0x0 - 0x0
    MF file format detected.
    [mf] search expr: cam1/*/*/*.jpg
    [mf] number of files: 3879 (15516)
    VIDEO:  [IJPG]  0x0  24bpp  10.000 fps    0.0 kbps ( 0.0 kbyte/s)
    [V] filefmt:16  fourcc:0x47504A49  size:0x0  fps:10.000  ftime:=0.1000
    Opening video filter: [expand osd=1]
    Expand: -1 x -1, -1 ; -1, osd: 1, aspect: 0.000000, round: 1
    ==========================================================================
    Opening video decoder: [ffmpeg] FFmpeg's libavcodec codec family
    Selected video codec: [ffmjpeg] vfm: ffmpeg (FFmpeg MJPEG decoder)
    ==========================================================================
    VDec: vo config request - 704 x 576 (preferred colorspace: Planar 422P)
    Could not find matching colorspace - retrying with -vf scale...
    Opening video filter: [scale]
    VDec: using Planar 422P as output csp (no 1)
    Movie-Aspect is undefined - no prescaling applied.
    SwScaler: reducing / aligning filtersize 1 -> 4
    Writing header...
    Pos:   2.4s     24f ( 0%) 13.45fps Trem:   0min   0mb  A-V:0.000 [1349:0]
    ...

Parameters explained:

`mf://cam1/*/*/*.jpg`
:    Images reside in sub directories tagged `YYYY/MM/DD/SEQUENCE.jpg`

`-mf fps=10:type=jpg`
:    We wanted 10 fps, source image type is JPG

`-ovc lavc`
:    Use libavcodec fast library to encode the AVI

`-oac copy`
:    We have no audio, so a blank stream will be copied

`-o cam1`
:    Write the result to cam1.avi

## Step 3: ffmpeg, convert to DVD

We wanted to have a DVD with the footage, so convert the movie(s) to DVD
compatible MPEG-4:

    :::shell
    $ ffmpeg -i cam1.avi -target pal-dvd -aspect 4:3 -sameq cam1.mpg
    FFmpeg version SVN-rUNKNOWN, Copyright (c) 2000-2007 Fabrice Bellard, et al.
      configuration: --enable-gpl --enable-pp --enable-swscaler --enable-pthreads --enable-libvorbis
        --enable-libtheora --enable-libogg --enable-libgsm --enable-dc1394
      libavutil version: 1d.49.3.0
      libavcodec version: 1d.51.38.0
      libavformat version: 1d.51.10.0
      built on Mar 16 2009 21:16:26, gcc: 4.2.4 (Ubuntu 4.2.4-1ubuntu3)
    Input #0, avi, from 'cam1.avi':
      Duration: 00:06:29.4, start: 0.000000, bitrate: 809 kb/s
      Stream #0.0: Video: mpeg4, yuv420p, 704x576, 10.00 fps(r)
    Output #0, dvd, to 'cam1.mpg':
      Stream #0.0: Video: mpeg2video, yuv420p, 720x576, q=2-31, 6000 kb/s, 25.00 fps(c)
    Stream mapping:
      Stream #0.0 -> #0.0
    Press [q] to stop encoding
    frame=   12 q=0.0 Lsize=     532kB time=0.4 bitrate=9904.9kbits/s
    video:270kB audio:0kB global headers:0kB muxing overhead 97.308936%
    ...

## Step 4: dvdauthor, rounding up

Now use dvdauthor to create your DVD filesystem layout (we ended up with 5
movies):

    :::shell
    $ dvdauthor --title -f all.mpg -f cam1.mpg -f cam2.mpg -f cam3.mpg -f cam4.mpg -o DVD
    DVDAuthor::dvdauthor, version 0.6.14.
    Build options: gnugetopt magick iconv freetype
    Send bugs to <dvdauthor-users@lists.sourceforge.net>

    INFO: dvdauthor creating VTS
    STAT: Picking VTS 01

    STAT: Processing all.mpg...
    STAT: VOBU 800 at 349MB, 1 PGCS
    INFO: Video pts = 0.500 .. 389.780

    STAT: Processing cam1.mpg...
    STAT: VOBU 1611 at 541MB, 1 PGCS
    INFO: Video pts = 0.500 .. 388.300

    STAT: Processing cam2.mpg...
    STAT: VOBU 2419 at 741MB, 1 PGCS
    INFO: Video pts = 0.500 .. 388.100

    STAT: Processing cam3.mpg...
    STAT: VOBU 3227 at 1112MB, 1 PGCS
    INFO: Video pts = 0.500 .. 388.580

    STAT: Processing cam4.mpg...
    STAT: VOBU 4029 at 1436MB, 1 PGCS
    INFO: Video pts = 0.500 .. 388.900
    STAT: VOBU 4039 at 1440MB, 1 PGCS
    INFO: Generating VTS with the following video attributes:
    INFO: MPEG version: mpeg2
    INFO: TV standard: pal
    INFO: Aspect ratio: 4:3
    INFO: Resolution: 720x576

    STAT: fixed 4039 VOBUS
    $ dvdauthor -T -o DVD
    DVDAuthor::dvdauthor, version 0.6.14.
    Build options: gnugetopt magick iconv freetype
    Send bugs to <dvdauthor-users@lists.sourceforge.net>

    INFO: dvdauthor creating table of contents
    INFO: Scanning DVD/VIDEO_TS/VTS_01_0.IFO

Now we have a file-tree we can burn on a DVD-R:

    :::shell
    $ tree DVD
    DVD
    |-- AUDIO_TS
    `-- VIDEO_TS
        |-- VIDEO_TS.BUP
        |-- VIDEO_TS.IFO
        |-- VTS_01_0.BUP
        |-- VTS_01_0.IFO
        |-- VTS_01_1.VOB
        `-- VTS_01_2.VOB

2 directories, 6 files
