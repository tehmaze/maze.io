#!/usr/bin/env python

import codecs
from collections import defaultdict
import datetime
import fnmatch
import os
import re
import shutil
import sys
try:
    from BeautifulSoup import BeautifulSoup
    from jinja2 import Environment, FileSystemLoader, nodes
    from jinja2.exceptions import TemplateSyntaxError
    from jinja2.ext import Extension
except ImportError, e:
    print >>sys.stdout, ' '.join(e.args)
    print >>sys.stdout, 'Some dependancies are not installed, see README.md'
    sys.exit(1)

def maybe(*names):
    for name in names:
        try:
            if '.' in name:
                part, name = name.split('.', 1)
                return getattr(__import__(part), name)
            else:
                return __import__(name)
        except (AttributeError, ImportError):
            pass

bbcode   = maybe('bbcode.Parser')
markdown = maybe('markdown.markdown')
textile  = maybe('textile.textile')

# Defaults
DEFAULTS = dict(
    # Default coding
    coding = 'utf-8',
    # Default output file
    result = dict(
        post      = '%(year)04d/%(month)02d/%(day)02d/%(slug)s.html',
        archives  = (
            '%(year)04d/index.html',
            '%(year)04d/%(month)02d/index.html',
            '%(year)04d/%(month)02d/%(day)02d/index.html',
        ),
    ),
    # Default files to render
    render = ('*.html', '*.htm', '*.xml', '*.rss', '*.atom'),
    # Default posts directory
    posts  = '{base}/_posts',
    # Default output directory
    output = '{base}/_site',
    # Default layout directory
    layout = '{base}/_layouts',
    # Default file name regular expression
    regexp = '(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)-(?P<slug>.*)(?P<extension>\.[^.]+)$',
    # Default formatter
    format = dict(
        default  = 'markdown',
        template = 'post.html',
        output   = 'html5',
    )
)
# Default Markdown extensions
MARKDOWN_EXTENSIONS = ['abbr', 'codehilite', 'def_list', 'footnotes']


class FormatExtension(Extension):
    tags = set(['format'])
    
    def parse(self, parser):
        line = parser.stream.next().lineno
        args = [parser.parse_expression()]
        body = parser.parse_statements(['name:endformat'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_format', args),
            [], [], body).set_lineno(line)

    def _format(self, name, caller):
        content = caller()
        if name == 'markdown':
            return markdown(content,
                extensions=MARKDOWN_EXTENSIONS,
            )
        
        elif name == 'textile':
            return textile(text, auto_link=True, head_offset=1)            
        
        else:
            raise TypeError('Unsupported formatter requested')


class Cooked(object):
    encoding = 'utf-8'
    extension = {
        '.md':       'markdown',
        '.markdown': 'markdown',
        '.tt':       'textile',
        '.textile':  'textile',
    }
    template_extensions = [
        'jinja2.ext.loopcontrols',
        'jinja2.ext.with_',
        FormatExtension,
    ]
    template_filters = dict(
        date=lambda value, format: value.strftime(format),
        first=lambda html: BeautifulSoup(html).find('p'),
    )

    def __init__(self, base=None, context={}, **config):
        self.config = DEFAULTS.copy()
        self.config.update(dict(
            base=base or os.getcwd(),
        ))
        self.config.update(config)
        self.context = context.copy()
        self.context.update(dict(posts=[]))

    def get(self, key):
        if key in self.config:
            value = self.config[key]
            if hasattr(value, 'format'):
                value = value.format(**self.config)
            return value

    def scan(self):
        # Scan posts
        source = self.get('posts')
        posts = []
        for filename in os.listdir(source):
            # Ignore files starting with underscores
            if filename.startswith('_'):
                continue
                
            filepath = os.path.join(source, filename)
            if os.path.isfile(filepath) and \
                    re.match(self.get('regexp'), filename):
                posts.append(filepath)
        
        # Make sure we return the posts in the right order
        posts.sort()
        for filepath in posts[::-1]:
            yield self.parse_post, filepath
        
        # Make archives
        yield self.parse_archive, None

        # Scan files
        for dirpath, dirs, files in os.walk(self.get('base'), False):
            relative = os.path.abspath(dirpath).replace(
                os.path.abspath(self.get('base')), '').lstrip(os.sep)
            
            # Ignore directories starting with underscores
            if relative.startswith('_'):
                if self.get('verbose'):
                    print 'Ignores', dirpath
                continue
                
            for filename in files:
                # Ignore files starting with underscores
                if filename.startswith('_'):
                    continue

                render_file = False
                for pattern in self.get('render'):
                    filepath = os.path.join(dirpath, filename)
                    if fnmatch.fnmatch(filename, pattern):
                        render_file = True
                        break
                
                if render_file:
                    yield self.parse_file, filepath
                else:
                    yield self.parse_copy, filepath
    
    def open(self, filename, mode='r', buffering=0):
        if 'w' in mode or 'a' in mode:
            dirname = os.path.dirname(filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
        return codecs.open(filename, mode, encoding=self.get('coding'),
            buffering=buffering)

    def parse_copy(self, filename):
        destname = self.render_filename(filename)
        if self.get('verbose'):
            print 'Cloning', filename, '->', destname.replace(self.get('base'), '')
        if not os.path.isdir(os.path.dirname(destname)):
            os.makedirs(os.path.dirname(destname))
        shutil.copy2(filename, destname)

    def parse_file(self, filename):
        destname = self.render_filename(filename)
        if self.get('verbose'):
            print 'Renders', filename

        # Render file
        metadata, filedata = self.read_template(filename)
        content = self.render_string(self.get('base'), filedata,
            dict(site=self.context))

        # Get template
        layout = metadata.get('layout', 'page.html')
        if not '.' in layout:
            layout = '.'.join([layout, 'html'])

        # Render file wrapping template
        context = dict(
            content=content,
            site=self.context,
        )
        with self.open(destname, 'w') as fd:
            fd.write(self.render_layout_template(layout, context))

    def parse_post(self, filename):
        basename = os.path.basename(filename)
        matches = re.match(self.get('regexp'), basename)
        if not matches:
            raise TypeError('Not a valid post "%s": pattern does not match' % (basename,))

        context = matches.groupdict()
        for key in ['year', 'month', 'day']:
            try:
                context[key] = int(context[key])
            except (KeyError, ValueError):
                context[key] = 0

        filepath = os.path.join(self.get('output'),
            self.get('result')['post'] % context,
        )

        context['site'] = self.context
        context['page'] = dict(
            date=datetime.date(context['year'], context['month'], context['day']),
            link=os.path.abspath(filepath).replace(
                os.path.abspath(self.get('output')), ''),
            type='link',
            title=context['slug'].replace('-', ' ').title(),
        )

        if self.get('verbose'):
            print 'Writing', filepath

        with self.open(filepath, 'w') as fd:
            fd.write(self.render(filename, context))

        # Record this post to the global context
        self.context['posts'].append(context['page'])
    
    def parse_archive(self, filename=None):
        # Render the archives
        archives = defaultdict(list)
        for post in self.context['posts']:
            archives[(post['date'].year,)].append(post)
            archives[(post['date'].year, post['date'].month)].append(post)
            archives[(post['date'].year, post['date'].month,
                           post['date'].day)].append(post)
        
        date_part = ('year', 'month', 'day')
        for date, posts in archives.iteritems():
            context = dict(zip(date_part, date))
            context.update(dict(
                date=datetime.date(*(list(date) + [1] * (3 - len(date)))),
                site=self.context,
                posts=posts,
            ))
            filename = os.path.join(
                self.get('output'),
                self.get('result')['archives'][len(date) - 1],
            ) % context
            content = self.render_layout_template('archive.html', context)
            if self.get('verbose'):
                print 'Writing', filename
            with open(filename, 'w') as fd:
                fd.write(content)

    def read_template(self, filename):
        with open(filename, 'r') as fd:
            metadata = {}
            marker = fd.read(3)
            if marker == '---':
                # Read until EOL
                line = fd.readline()
                # This is a header, read until we find triple dashes
                while True:
                    line = fd.readline().strip()
                    if line == '---':
                        break
                    elif ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                    else:
                        print 'Bogus!?', line
            
                filedata = fd.read()
            else:
                filedata = marker + fd.read()

            return metadata, filedata.decode(self.get('coding'))

    def render(self, filename, context):
        metadata, filedata = self.read_template(filename)
        context['page'].update(metadata)
        content = self.formatted(filedata, context['extension'])
        context['content'] = context['page']['content'] = content
        return self.render_layout_template('post.html', context)

    def render_layout_template(self, name, context):
        return self.render_template(self.get('layout'), name, context)
        
    def render_template(self, base, name, context):
        env = Environment(
            extensions=self.template_extensions,
            loader=FileSystemLoader(base),
        )
        env.filters.update(self.template_filters)
        template = env.get_template(name)
        return template.render(context)

    def render_string(self, base, string, context):
        env = Environment(
            extensions=self.template_extensions,
            loader=FileSystemLoader(base),
        )
        env.filters.update(self.template_filters)
        template = env.from_string(string)
        return template.render(context)

    def render_filename(self, filename):
        '''
        Return a filename as it would be in the output (target) directory.
        '''
        filename = os.path.abspath(filename)
        return filename.replace(
            os.path.abspath(self.get('base')),
            os.path.abspath(self.get('output'))
        )

    def format_bbcode(self, text):
        return bbcode(escape_html=False).render(text)

    def format_markdown(self, text):
        return markdown(text,
            output_format=self.get('format')['output'],
            extensions=['abbr', 'codehilite', 'footnotes'],
        )

    def format_textile(self, text):
        return textile(text,
            auto_link=True,
            head_offset=1,
            html_type=self.get('format')['output'].rstrip('145')
        )

    def formatted(self, filedata, extension):
        parser = self.extension.get(extension, self.get('format')['default'])
        return getattr(self, '_'.join(['format', parser]))(filedata)


def run():
    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', default='',
        help='Read configuration from file (default: no)')
    parser.add_option('-d', '--dir', default='',
        help='Run cooked in this directory')
    parser.add_option('-s', '--server', default=False, action='store_true',
        help='Run testing web server')
    parser.add_option('-b', '--bind', default='localhost',
        help='Server host (default: localhost)')
    parser.add_option('-p', '--port', default=8000, type='int',
        help='Server port (default: 8000)')
    parser.add_option('-v', '--verbose', default=False, action='store_true',
        help='Be verbose')
    options, args = parser.parse_args()

    context = {}
    if options.config:
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(options.config)
        if config.has_section('cooked'):
            for name, value in config.items('cooked'):
                setattr(options, name, value)
        for section in config.sections():
            if section == 'cooked':
                continue
            else:
                context[section] = dict(config.items(section))

    cooked = Cooked(base=options.dir, verbose=options.verbose, context=context)
    if options.server:
        from werkzeug.serving import run_simple
        from werkzeug.wsgi import SharedDataMiddleware
        from werkzeug.wrappers import Request, Response

        class App(object):
            def __call__(self, environ, start_response):
                return self.wsgi_app(environ, start_response)

            def dispatch_request(self, request, start_response=None):
                '''
                No static file was found, retry with 'index.html' appended.
                '''
                if request.path.endswith('/'):
                    path = os.path.join(cooked.get('output'),
                        str(request.path).rstrip('/'),
                        'index.html')
                    
                    if os.path.isfile(path):
                        return Response('', status=302, headers=dict(
                            Location=request.path + 'index.html',
                        ))

                return Response('Not found', status=404)

            def wsgi_app(self, environ, start_response):
                request = Request(environ)
                response = self.dispatch_request(request, start_response)
                return response(environ, start_response)

        app = App()
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/': cooked.get('output'),
        })
        print 'Starting webserver on http://%s:%d/' % (options.bind,
            options.port)
        return run_simple(options.bind, options.port, app)

    else:
        for parser, filename in cooked.scan():
            if options.verbose:
                print 'Reading', filename
            parser(filename)


if __name__ == '__main__':
    sys.exit(run())
