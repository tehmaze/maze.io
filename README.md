maze.io - cooked.py
===================

Simple static site generator, makes use of Jinja2 templates.


Installation
------------

Installation is easy:

    $ pip -r requirements.txt


Directory layout
----------------

Typical layout:

    project/            Site root
    |-- _layout/        Site layout templates
    |-- _post/          Site posts, can be in several formats (see below)
    |-- _site/          Here your generated content will be
    `-- *.html/css/rss  Site content


Formats
-------

We support serveral formats:

*.bb, *.bbcode
:       Will be formatted with a BBCode reader

*.md, *.markdown
:       Will be formatted with a Markdown reader

*.rst, *.rest
:       Will be formatted with a reStructuredText reader

*.tt, *.textile
:       Will be formatted with a Textile reader


Configuration file
------------------

See [maze.cfg](https://github.com/tehmaze/maze.io/blob/master/maze.cfg) for an
example, use the source Luke!
