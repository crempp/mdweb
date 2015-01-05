# from contextlib import closing
import logging
import markdown
import os
import re

import jinja2

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from flask import (
    Flask,
    render_template,
    render_template_string,
)
from flask.views import View

#### DEBUGGING
from pprint import pprint

# Create application
app = Flask('MDWeb')
app.config.from_object('config.Config')

logging.basicConfig(level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

theme_folder = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'themes',
    app.config['THEME']
)

# Set the template directory to the configured theme's template directory
# http://stackoverflow.com/a/13598839
my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([
            os.path.join(theme_folder, 'templates'),
        ]),
    ])
app.jinja_loader = my_loader

# Set the static directory to the configured theme's asset directory
# Patch the static path
app.static_folder = os.path.join(theme_folder, 'assets')


class PageMetaInf(object):
    title = None
    subtitle = None
    description = None
    order = 0
    author = None


class Index(View):
    """The one view to rule them all. MDWeb has one single entry point. The
    MDWeb routing system (not Flasks) determines the how to handle the request
    and what markdown file to load.
    """

    navigation = None

    # A pre-compiled regex for extracting meta information (and comments)
    meta_inf_regex = re.compile(app.config['META_INF_REGEX'], flags=re.DOTALL)

    def _load_page_markdown(self, path):
        """Load the markdown file for the given route."""
        # Use provided path to get correct file
        if path == '':
            file_path = os.path.join(app.config['CONTENT_PATH'], 'index.md')
        else:
            file_path = os.path.join(app.config['CONTENT_PATH'], '%s' % path)

            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, 'index.md')

            # If requested path does not exist show 404 file or message
            # TODO: If we have a 404 throw an exception so the caller knows
            if not os.path.exists(file_path):
                path_404 = os.path.join(app.config['CONTENT_PATH'], '404.md')
                if os.path.exists(path_404):
                    file_path = path_404
                else:
                    return "404: not found"

        # Load the file contents
        with open(file_path, 'r') as f:
            file_string = f.read()

        # Extract meta information
        match = self.meta_inf_regex.search(file_string)
        meta_inf = parse_meta_inf(match.group(1)) if match else {}

        # Strip all comments
        markdown_str = self.meta_inf_regex.sub('', file_string)

        return markdown_str, meta_inf

    @classmethod
    def update_navigation(cls, navigation):
        cls.navigation = navigation

    def dispatch_request(self, path):
        """Dispatch request"""
        page_markdown, meta_inf = self._load_page_markdown(path)

        context = {
            'navigation': self.navigation['content'],
            'page': parse_markdown(page_markdown),
            'meta': meta_inf,
        }
        return render_template('page.html', **context)


def parse_markdown(page_markdown):
    """Parse given markdown string into rendered html."""
    page_html = markdown.markdown(page_markdown)

    return page_html


def parse_meta_inf(meta_inf_string):
    """Parse given meta information string into a dictionary of meta
    information key:value pairs"""
    lines = meta_inf_string.split('\n')
    meta_inf = {}

    for l in lines:
        if l == '':
            continue
        (k, v) = l.split(':')
        meta_inf[k.lower()] = v

    return meta_inf


def build_nav():
    """Build navigation dictionary"""
    logging.debug('Building navigation')

    meta_inf_regex = re.compile(app.config['META_INF_REGEX'], flags=re.DOTALL)

    navigation = {}
    for dirpath, dirnames, filenames in os.walk(app.config['CONTENT_PATH']):
        # Use the index meta info for the directory's meta info
        index_path = os.path.join(dirpath, 'index.md')

        if not os.path.exists(index_path):
            raise 'Could not find index file for content directory "%s"' % index_path

        with open(index_path, 'r') as f:
            file_string = f.read()

        # Extract meta information
        match = meta_inf_regex.search(file_string)
        meta_inf = parse_meta_inf(match.group(1)) if match else {}

        # Assemble the info for this navigation level
        nav_level = {
            'path': re.sub(r'^/?content/?', '/', dirpath),
            'order': meta_inf['order'] if 'order' in meta_inf.keys() else None,
            'meta': meta_inf,
            'index_html': None,
            'children': {},
        }

        # Inject the navigation level in to the navigation dict by
        # deconstructing the dirpath and using the directories as keys in the
        # hierarchical dict.
        #
        # This strategy depends on the correct ordering of the directories
        # walked over by os.walk. The current directory must be preceded by
        # all parent directories.
        nav_parts = dirpath.strip('/').split('/')
        # walk down the pieces of the path
        nav_end = navigation
        for p in nav_parts[:-1]:
            if p == 'content':
                nav_end = nav_end[p]
            else:
                nav_end = nav_end['children'][p]

        # Inject the nav level
        if nav_parts[-1] == 'content':
            nav_end[nav_parts[-1]] = nav_level
        else:
            nav_end['children'][nav_parts[-1]] = nav_level

    Index.update_navigation(navigation)


@app.before_first_request
def before_first_request():
    """ Setup application on the first request"""
    # Build the navigation object
    build_nav()

    # Setup a watcher to rebuild the nav whenever a file has changed in content
    #event_handler = LoggingEventHandler()
    class ContentHandler(FileSystemEventHandler):
        def on_modified(self, event):
            logging.debug('%s "%s" was "%s"' % (
                'Directory' if event.is_directory else "File",
                event.src_path,
                event.event_type
            ))

            if not event.is_directory:
                build_nav()

    event_handler = ContentHandler()
    observer = Observer()
    observer.schedule(event_handler, app.config['CONTENT_PATH'], recursive=True)
    observer.start()


@app.errorhandler(404)
def page_not_found(e):
    """Show custom 404 page"""
    # TODO: Make this use the 404.md
    return "404 - TODO: Make this use the 404.md", 404


# Route all requests to the index view
app.add_url_rule('/', view_func=Index.as_view('index'), defaults={'path': ''})
app.add_url_rule('/<path:path>', view_func=Index.as_view('index_with_path'))


if __name__ == '__main__':
    app.run()