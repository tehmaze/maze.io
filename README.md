maze.io - cooked.py
===================

Simple static site generator, makes use of Jinja2 templates.


Installation
------------

Installation is easy:

    $ pip -r requirements.txt

To install support for all readers (for formatting):

    $ pip -r requirements-recommended.txt


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


Template metadata
-----------------

You can embed a small header in the templates to override some of the defaults
for the given file type. For example, to embed site content in a layout
template, you may use:

    ---
    reader: jinja2
    template: page.html
    ---

This will parse the file using the Jinja2 template engine and then look for
page.html in project/_layout and provide the generated template via the
page.content variable. See
[maze/_layout/page.html](https://github.com/tehmaze/maze.io/blob/master/maze/_layout/page.html)
and
[maze/index.html](https://github.com/tehmaze/maze.io/blob/master/maze/index.html)
for an example on how to use this.


Configuration file
------------------

See [maze.cfg](https://github.com/tehmaze/maze.io/blob/master/maze.cfg) for an
example, use the source Luke!
