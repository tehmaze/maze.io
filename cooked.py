#!/usr/bin/env python

# Python modules
from collections import defaultdict
import ConfigParser
import codecs
import datetime
import fnmatch
import os
import re
import shlex
import shutil
import string
import subprocess
import sys
# External modules
try:
    from BeautifulSoup import BeautifulSoup
    from jinja2 import Environment, FileSystemLoader, nodes
    from jinja2.exceptions import TemplateSyntaxError
    from jinja2.ext import Extension
except ImportError, e:
    print >>sys.stdout, ' '.join(e.args)
    print >>sys.stdout, 'Some dependancies are not installed, see README.md'
    sys.exit(1)
# Optional imports for the formatters
try:
    import bbcode
except ImportError, e:
    print >>sys.stdout, 'Warning, failed to import bbcode: %s' % str(e)
try:
    import docutils.core
except ImportError, e:
    print >>sys.stdout, 'Warning, failed to import docutils: %s' % str(e)
try:
    import markdown
except ImportError, e:
    print >>sys.stdout, 'Warning, failed to import markdown: %s' % str(e)
try:
    import textile
except ImportError, e:
    print >>sys.stdout, 'Warning, failed to import textile: %s' % str(e)

class Reader(object):
    formatter = None
    
    def __init__(self, cooked):
        self.cooked = cooked
        self.section = 'format:{0}'.format(self.formatter)
        if self.cooked.config.has_section(self.section):
            self.config = dict(self.cooked.config.items(self.section))
        else:
            self.config = dict()
        
    def render(self, content):
        raise NotImplementedError


class BBCodeReader(Reader):
    formatter = 'bbcode'

    def render(self, content):
        if 'bbcode' not in sys.modules:
            raise NotImplementedError('You need to install bbcode')

        parser = bbcode.Parser(**self.config)
        return parser.format(content)


class JinjaReader(Reader):
    formatter = 'jinja'
    
    def render(self, content):
        env = self.cooked._render_env(self.cooked.config.get('cooked', 'source'))
        template = env.from_string(content)
        return template.render(site=self.cooked.context)


class MarkdownReader(Reader):
    formatter = 'markdown'
    
    def __init__(self, *args, **kwargs):
        super(MarkdownReader, self).__init__(*args, **kwargs)
        if 'extensions' in self.config:
            self.config['extensions'] = map(string.strip,
                self.config['extensions'].split(',')
            )
    
    def render(self, content):
        if 'markdown' not in sys.modules:
            raise NotImplementedError('You need to install markdown')
            
        return markdown.markdown(content, **self.config)


class NullReader(Reader):
    def render(self, content):
        return content


class RestructuredTextReader(Reader):
    formatter = 'restructuredtext'
    
    def render(self, content):
        if 'docutils.core' not in sys.modules:
            raise NotImplementedError('You need to install docutils')
            
        parts = docutils.core.publish_parts(content, writer_name='html',
            settings_overrides=self.config)
        return parts['body']


class TextileReader(Reader):
    formatter = 'textile'

    def render(self, content):
        if 'textile' not in sys.modules:
            raise NotImplementedError('You need to install textile')
            
        return textile.textile(content, **self.config)


class Cooked(object):
    # Maximum recursion depth
    MAX_DEPTH = 10
    
    reader = dict(
        bbcode=BBCodeReader,
        jinja=JinjaReader,
        markdown=MarkdownReader,
        null=NullReader,
        textile=TextileReader,
        rest=RestructuredTextReader,
        restructuredtext=RestructuredTextReader,
    )
    
    template_extensions = (
        'jinja2.ext.loopcontrols',
        'jinja2.ext.with_',
    )
    template_filters = dict(
        date=lambda value, format: value.strftime(format),
        first=lambda html: BeautifulSoup(html).find('p'),
    )
    
    def __init__(self, options):
        self.options = options
        self.configure(self.options.config)
    
    def configure(self, filename):
        self.config = ConfigParser.ConfigParser()
        self.config.read(filename)
        
        # Needs post-processing
        self.pattern = map(string.strip,
            self.config.get('cooked', 'pattern').split(','))
        
        # Site context
        self.context = dict(self.config.items('site'))
        self.context['posts'] = []
    
    def read_metadata(self, filename):
        '''
        Read the contents of a file, extracting metadata embedded in the header.
        
        The metadata can only consist of simple key value pairs separated by a
        colon. The header is delimited by three or more dashes. No blank lines
        inside the header are allowed, comments may be inserted prefixing the
        line with a hash sign (#) or a semi colon (;).
        '''
        print 'Parsing', filename
        with codecs.open(filename, 'r',
            encoding=self.config.get('cooked', 'encoding')) as handle:
            
            metadata = dict()
            header = handle.read(3)
            # Header marker found, read until the next header marker
            if header == '---':
                # Read until EOL
                handle.readline()
                while True:
                    line = handle.readline().strip()
                    # End of header marker
                    if line.startswith('---'):
                        break
                        
                    # Comment
                    elif line[0] in '#;':
                        continue
                        
                    # Key value pair
                    elif ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                        
                    else:
                        raise ValueError('Invalid header syntax: {0}'.format(line))
                
                filedata = []
                while True:
                    chunk = handle.read(4096)
                    if chunk:
                        filedata.append(chunk)
                    else:
                        break

                filedata = u''.join(filedata)
                
            # No header marker found
            else:
                filedata = u''.join([header, handle.read()])
                        
            # Parse the reader
            if 'reader' in metadata:
                metadata['reader'] = self.reader.get(metadata['reader'])
            else:
                extension = metadata.get('extension', os.path.splitext(filename)[1])
                if self.config.has_option('reader', extension):
                    metadata['reader'] = self.reader.get(
                        self.config.get('reader', extension),
                        self.config.get('reader', 'default')
                    )
                
                else:
                    metadata['reader'] = self.reader.get(
                        self.config.get('reader', 'default')
                    )

            if metadata['reader'] is None:
                raise TypeError('No suitable reader could be found')
            
            return filedata, metadata
    
    def open(self, filename, mode='r', encoding=None):
        # Make sure the target directory exists if a file is opened for
        # writing (or appending)
        if 'w' in mode or 'a' in mode:
            dirname = os.path.dirname(os.path.abspath(filename))
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            
        encoding = encoding or self.config.get('cooked', 'encoding')
        if encoding == 'binary':
            mode += 'b'
            return open(filename, mode=mode)
        else:
            return codecs.open(filename, mode=mode, encoding=encoding)
    
    def output(self, filename, content_or_handle, encoding=None):
        if hasattr(content_or_handle, 'read'):
            content = content_or_handle.read()
        else:
            content = content_or_handle
        
        encoding = encoding or self.config.get('cooked', 'encoding')
        for pattern, commands in self.config.items('filter'):
            if fnmatch.fnmatch(filename, pattern):
                commands = commands.format(
                    filename=filename,
                    stdout='/dev/stdout',
                    stderr='/dev/stderr',
                    stdin='/dev/stdin',
                )
                print 'Filters', filename
                # We support multiple pipes, the output of one pipe is the
                # input for the next one (yes that's what piping is ;-)
                for command in commands.split('|'):
                    print '      |', command
                    pipe = subprocess.Popen(shlex.split(command.strip()),
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                    )
                    
                    if encoding == 'binary':
                        result = pipe.communicate(content)
                    else:
                        result = pipe.communicate(content.encode(encoding))
                    
                    if pipe.returncode == 0:
                        content = result[0]
                        if encoding != 'binary':
                            content = content.decode(encoding)
                    elif self.config.getboolean('filter', 'ignore_errors'):
                        pass
                    else:
                        raise RuntimeError(result[1])
                break
        
        print 'Writing', filename
        with self.open(filename, 'w', encoding=encoding) as handle:
            handle.write(content)
    
    def _post_sort(self, a, b):
        if a['year'] == b['year']:
            return cmp(a['date'], b['date'])
        else:
            return cmp(a['year'], b['year'])
    
    def parse_archive(self, archives):
        targets = (
            self.config.get('archive', 'target_y'),
            self.config.get('archive', 'target_ym'),
            self.config.get('archive', 'target_ymd'),
        )
        for date, posts in archives.iteritems():
            target = targets[len(date) - 1]
            metadata = dict(zip(('year', 'month', 'day'), date))
            metadata.update(dict(
                date=datetime.date(*(list(date) + [1] * (3 - len(date)))),
                site=self.context,
                posts=posts,
            ))
            
            # Sort posts by date (ascending)
            posts.sort(self._post_sort)
            
            # Render archive
            content = self.render_template(
                self.config.get('cooked', 'source_layout'),
                self.config.get('archive', 'template'),
                metadata,
            )
            
            # Ouput filename
            copyname = os.path.abspath(os.path.join(
                self.config.get('cooked', 'target'),
                target,
            )).format(**metadata)
            
            # Output data
            self.output(copyname, content)
        
        # Tell the site context about the archives
        self.context['archives'] = archives
        self.context['posts'].sort(self._post_sort)
    
    def parse_file(self, filename):
        print 'Reading', filename
        copyname = filename.replace(
            os.path.abspath(self.config.get('cooked', 'source')),
            os.path.abspath(self.config.get('cooked', 'target')),
        )

        for pattern in self.pattern:
            if fnmatch.fnmatch(filename, pattern):
                try:
                    filedata, metadata = self.read_metadata(filename)
                except TypeError, e:
                    print 'Failure', filename
                    raise
                content = metadata['reader'](self).render(filedata)
                
                # This file wants to be rendered inside a template, let's
                # make it so
                template = metadata.get('template')
                if template:
                    if not '.' in template:
                        template = '.'.join([template, 'html'])
                        
                    # Pass site context to template
                    metadata['site'] = self.context
                    metadata['content'] = content
                    content = self.render_template(
                        self.config.get('cooked', 'source_layout'),
                        template, metadata
                    )
                
                # Output data
                self.output(copyname, content)
                return
        
        # Still here? Just copy the file over
        print 'Copying', copyname
        dirname = os.path.dirname(copyname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
        with open(filename, 'rb') as handle:
            self.output(copyname, handle, encoding='binary')
        
        # Copy the original file attributes
        shutil.copystat(filename, copyname)
    
    def parse_post(self, filename, filedata, metadata={}):
        '''
        Parse a post. Optionally you can provide a dictionary with metadata
        which can be embedded in the header of the post, overriding what is
        detected based on the file name or the default settings.
        '''
        pattern = self.config.get('post', 'pattern')
        match = re.search(pattern, filename)
        if match:
            for key, value in match.groupdict().iteritems():
                if not key in metadata:
                    metadata[key] = value

        # Parse the date
        for key in ['year', 'month', 'day']:
            try:
                metadata[key] = int(metadata[key])
            except (KeyError, ValueError):
                metadata[key] = 0
        
        # Parsed date
        metadata['date'] = datetime.date(metadata['year'], metadata['month'], metadata['day'])
        metadata['link'] = '/' + self.config.get('post', 'target').format(**metadata)

        # Parse the content
        metadata['content'] = metadata['reader'](self).render(filedata)
        
        # Render the content
        template = metadata.get('template', self.config.get('post', 'template'))
        if not '.' in template:
            template = '.'.join([template, 'html'])

        # Write the content
        content = self.render_template(
            self.config.get('cooked', 'source_layout'),
            template, dict(
                site=self.context,
                page=metadata,
            ),
        )
        
        # Compose copyname
        copyname = os.path.abspath(os.path.join(
            self.config.get('cooked', 'target'),
            self.config.get('post', 'target'),
        )).replace(os.sep + os.sep, os.sep).format(**metadata)

        # Output the file and copy the original file attributes
        self.output(copyname, content)
        shutil.copystat(filename, copyname)
        
        # Add the post to the site context
        self.context['posts'].append(metadata)

    def _render_env(self, dirname):
        env = Environment(
            extensions=self.template_extensions,
            loader=FileSystemLoader(dirname),
            lstrip_blocks=False,
        )
        env.filters.update(self.template_filters)
        return env

    def render_string(self, dirname, content, context):
        return self._render_env(dirname).from_string(content).render(context)
    
    def render_template(self, dirname, template, context):
        return self._render_env(dirname).get_template(template).render(context)

    def scan(self):
        # Scan posts
        for item in self.scan_posts():
            yield item
        
        # Scan archives
        for item in self.scan_archives():
            yield item
        
        # Scan files
        for item in self.scan_files():
            yield item
    
    def scan_archives(self):
        '''
        Scan for posts that are to be put in the archives.
        '''
        
        posts = defaultdict(list)
        for post in self.context['posts']:
            posts[(post['year'],)].append(post)
            posts[(post['year'], post['month'])].append(post)
            posts[(post['year'], post['month'], post['day'])].append(post)
        
        yield self.parse_archive, (posts,)
    
    def scan_files(self, dirname=None, depth=0):
        '''
        Scan for files.
        '''

        dirname = os.path.abspath(dirname or \
            self.config.get('cooked', 'source'))

        if depth > self.MAX_DEPTH:
            raise RecursionError('Maximum recursion level reached')

        for name in os.listdir(dirname):
            # Skip files prefixed with an underscore, it's like magic
            if name.startswith('_') or name.startswith('._'):
                continue
                
            path = os.path.join(dirname, name)
            if os.path.isfile(path):
                yield self.parse_file, (path,)
            
            elif os.path.isdir(path):
                for item in self.scan_files(path, depth=depth + 1):
                    yield item

    def scan_posts(self, dirname=None, depth=0):
        '''
        Scan for posts.
        '''
        dirname = os.path.abspath(dirname or \
            self.config.get('cooked', 'source_posts'))

        if depth > self.MAX_DEPTH:
            raise RecursionError('Maximum recursion level reached')
        
        for name in os.listdir(dirname):
            path = os.path.join(dirname, name)
            if os.path.isfile(path):
                filedata, metadata = self.read_metadata(path)
                yield self.parse_post, (path, filedata, metadata)
            
            elif os.path.isdir(path):
                for item in self.scan_posts(path, depth + 1):
                    yield item
            

def run():
    import optparse
    
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', default='cooked.cfg',
        help='Configuration file (default: cooked.cfg)')
    
    options, args = parser.parse_args()
    if not os.path.isfile(options.config):
        parser.error('{0}: no such file'.format(options.config))
        return 1
    
    cooked = Cooked(options)
    for parser, args in cooked.scan():
        parser(*args)

if __name__ == '__main__':
    sys.exit(run())
