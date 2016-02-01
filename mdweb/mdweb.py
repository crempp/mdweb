"""
MDWeb - Not a CMS
http://mdweb.lapinlabs.com

Copyright 2015 Chad Rempp
Released under the MIT license
http://mdweb.lapinlabs.com/license

Date: 2015-07-30
"""

import logging
import os
import re

import blinker
import jinja2
import markdown
from flask import (
    Flask,
    render_template,
    current_app,
)
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from werkzeug.exceptions import abort

from Page import PageMetaInf, Page
from mdweb.Exceptions import *

# Setup signals
sig_namespace = blinker.Namespace()
mdw_signaler = {
    'pre-boot' : sig_namespace.signal('pre-boot'),
    'pre-config' : sig_namespace.signal('pre-config'),
    'post-config' : sig_namespace.signal('post-config'),
    'pre-app-start' : sig_namespace.signal('pre-app-start'),
    'post-app-start' : sig_namespace.signal('post-app-start'),
    'pre-content-scan': sig_namespace.signal('pre-content-scan'),
    'post-content-scan': sig_namespace.signal('post-content-scan'),
    'post-boot': sig_namespace.signal('post-boot'),
}

BASE_SETTINGS = {
    'DEBUG': True,

    'TESTING': False,

    'SECRET_KEY': 'super_secret_development_key',

    # A pre-compiled regex for extracting meta information (and comments)
    'META_INF_REGEX': r'/\*(.*)\*/',

    # Path to page content
    'CONTENT_PATH': 'content/',

    # Name of theme (should be a sub-folder in themes/
    'THEME': 'alpha',
}



class Page(View):
    """MDWeb Page"""

    def __init__(self, app, file_string, page_path):
        """
        Content Page

        :param app: Flask application
        :param file_string: Raw page content as a string
        :param page_path: Filesystme path to the page
        :return:
        """
        self.app = app

        self.path = page_path

        # Extract the part of the page_path that will be used as the URL path
        # I can't get the last '/' excluded in the regex so I am just stripping it.
        # TODO: Solve this regex puzzle
        pattern = r'^%s(?P<path>[^\0]*?)(index)?(\.md)' % self.app.config['CONTENT_PATH']
        matches = re.match(pattern, page_path)
        if matches:
            self.url_path = matches.group('path').rstrip('/')
        else:
            raise Exception("Unable to parse page path [%s]" % self.app.config['CONTENT_PATH'])

        self._meta_inf_regex = app.config['META_INF_REGEX']

        # Extract meta information
        self.meta_inf = PageMetaInf(app, file_string)

        # Strip the meta information and comments
        self.markdown_str = self._meta_inf_regex.sub('', file_string)

        # The page will be rendered on first view
        self.page_html = self.parse_markdown(self.markdown_str)

        # Cache of the full rendered page
        self.page_cache = None

    def parse_markdown(self, page_markdown):
        """Parse given markdown string into rendered html."""
        page_html = markdown.markdown(page_markdown)

        return page_html


class Index(View):
    """The one view to rule them all. MDWeb has one single entry point. The
    MDWeb routing system (not Flasks) determines the how to handle the request
    and what markdown file to load.
    """

    methods = ['GET']

    def dispatch_request(self, path):
        """Dispatch request"""

        page = current_app.find_page(path)

        if page is None:
            abort(404)

        if page.meta_inf.template:
            page_template = page.meta_inf.template
        else:
            page_template = 'page.html'

        context = {
            'page': page.page_html,
            'meta': page.meta_inf,
        }

        if page.page_cache is None:
            page.page_cache = render_template(page_template, **context)

        return page.page_cache


class NavigationLevel(object):
    """TODO: Describe"""
    def __init__(self, name='', page=None):
        """Create a navigation instance """
        self.name = name
        self.page = page
        self.children = {}

    @property
    def path(self):
        return self.page.path

    @property
    def order(self):
        return self.page.meta_inf.order

    @property
    def meta(self):
        return self.page.meta_inf

    def add_page_at_path(self, section_path, page):
        # If this is the root path (home) set the
        if (len(section_path) is 1 and section_path[0] == '') or len(section_path) == 0:
            self.page = page
        else:
            s = section_path.pop(0)
            if not self.has_child(s):
                p = page if len(section_path) == 0 else None
                self.add_child(NavigationLevel(s, page=p))
                if len(section_path) > 0:
                    self.children[s].add_page_at_path(section_path, page)
            else:
                self.children[s].add_page_at_path(section_path, page)

    def add_child(self, child_nav_level):
        self.children[child_nav_level.name] = child_nav_level
        return child_nav_level

    def get_child(self, name):
        return self.children[name]

    def has_child(self, name):
        return name in self.children


class MDSite(Flask):
    """ MDWeb site

    An MDWeb Site is very closely related to a Flask application.
    """
    navigation = None

    def __init__(self, site_name, config_filename=None, app_options={}):
        """
        Initialize the Flask application and start the app.

        :param site_name: The name of the site, will be used as the flask
                          import_name.

        :param config_filename: Application configuration filename.

        :param app_options: Additional parameters to be passed to Flask
                            constructor
        """
        self.site_name = site_name
        self.app_options = app_options
        self.config_filename = config_filename
        self.pages = []
        self.content_observer = None
        self.theme_observer = None

        self.start()
        self._register_observers()

    def start(self):
        """Go through the boot up process sending signals for each stage."""
        #: START THE BOOT PROCESS
        mdw_signaler['pre-boot'].send(self)
        self._pre_boot()

        #: START THE FLASK APP
        # We must start the app straight away because we can't get the config
        # easily until we do. The rest of the boot tasks will require the
        # config.
        mdw_signaler['pre-app-start'].send(self)
        self._create_app()
        mdw_signaler['post-app-start'].send(self)

        #: LOAD THE CONFIG
        mdw_signaler['pre-config'].send(self)
        self._load_config(self.config_filename)
        mdw_signaler['post-config'].send(self)

        #: SCAN FOR CONTENT
        mdw_signaler['pre-content-scan'].send(self)
        self._content_scan()
        mdw_signaler['post-content-scan'].send(self)

        #: FINISH THINGS UP
        self._post_boot()
        mdw_signaler['post-boot'].send(self)

    def stop(self):
        """Stop the application"""
        print("Stop")
        if self.content_observer:
            self.content_observer.stop()
        if self.theme_observer:
            self.theme_observer.stop()

    def _register_observers(self):
        """Setup a watcher to rebuild the nav whenever a file has changed in
        content."""
        _this = self

        class ContentHandler(FileSystemEventHandler):
            def on_modified(self, event):
                logging.debug('%s "%s" was "%s"' % (
                    'Directory' if event.is_directory else "File",
                    event.src_path,
                    event.event_type
                ))

                # _this.stop()
                _this.start()
                _this._clear_page_cache()

        event_handler = ContentHandler()

        # Listen for content changes
        self.content_observer = Observer()
        self.content_observer.schedule(event_handler, self.config['CONTENT_PATH'], recursive=True)
        self.content_observer.start()

        # If we're debugging, listen for theme changes
        if self.debug:
            self.theme_observer = Observer()
            self.theme_observer.schedule(event_handler, self.config['THEME_FOLDER'], recursive=True)
            self.theme_observer.start()

    def _pre_boot(self):
        """Do pre-boot tasks."""
        pass

    def _create_app(self):
        """Create the Flask application."""

        # self.app = Flask()
        super(MDSite, self).__init__(self.site_name, **self.app_options)
        # import_name, static_path=None, static_url_path=None,
        # static_folder='static', template_folder='templates',
        # instance_path=None, instance_relative_config=False

        # Route all requests to the index view
        self.add_url_rule('/', view_func=Index.as_view('index'), defaults={'path': ''})
        self.add_url_rule('/<path:path>', view_func=Index.as_view('index_with_path'))

        # Setup error handler pages
        self.error_handler_spec[None][404] = self.error_page_not_found

        # Setup logging
        logging.basicConfig(level=logging.DEBUG if self.config['DEBUG'] else logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def _load_config(self, filename):
        """Load the configuration of the application being started.

         :param filename: Application's configuration filename
         """
        self.config.from_pyfile(filename)

        self.config['BASE_PATH'] = os.path.dirname(os.path.realpath(__file__))

        # Build the full path the the theme folder using the theme name
        self.config['THEME_FOLDER'] = os.path.join(
            self.config['BASE_PATH'],
            'themes',
            self.config['THEME']
        )

        # Ensure theme directory exists
        if not os.path.isdir(self.config['THEME_FOLDER']) or \
                not os.path.exists(self.config['THEME_FOLDER']):
            raise FileExistsError("Theme directory %s does not exist" % self.config['THEME_FOLDER'])

        # Set the template directory to the configured theme's template directory
        # http://stackoverflow.com/a/13598839
        my_loader = jinja2.ChoiceLoader([
                self.jinja_loader,
                jinja2.FileSystemLoader([
                    os.path.join(self.config['THEME_FOLDER'], 'templates'),
                ]),
            ])
        self.jinja_loader = my_loader

        # Set the static folder path
        self.static_folder = os.path.join(self.config['THEME_FOLDER'], 'assets')

        # Extend the content path to the absolute path
        if not self.config['CONTENT_PATH'].startswith('/'):
            self.config['CONTENT_PATH'] = os.path.join(
                self.config['BASE_PATH'],
                self.config['CONTENT_PATH']
            )

        # Ensure content directory exists
        if not os.path.isdir(self.config['CONTENT_PATH']) or \
                not os.path.exists(self.config['CONTENT_PATH']):
            raise FileExistsError("Content directory %s does not exist" % self.config['CONTENT_PATH'])

        # Compile the regex
        if 'META_INF_REGEX' in self.config and \
                        self.config['META_INF_REGEX'] is not None:
            self.config['META_INF_REGEX'] = re.compile(self.config['META_INF_REGEX'],
                                                       flags=re.DOTALL)
        else:
            raise ConfigException("Meta information regex missing")

    def _content_scan(self):
        """Scan site content."""
        special_case_files = [
            'index.md',
            '404.md',
        ]

        # Create navigation
        self.navigation = NavigationLevel()

        # Scan and parse content
        for dir_path, dir_names, file_names in os.walk(self.config['CONTENT_PATH']):
            section_path = re.sub(r'^%s' % self.config['CONTENT_PATH'], '', dir_path).split('/')

            # Remove special case files from our list
            file_names = [f for f in file_names if f not in special_case_files]

            # Load index page for current directory
            index_path = os.path.join(dir_path, 'index.md')
            if os.path.exists(index_path):
                page = self._parse_page(index_path)
                self.pages.append(page)
                self.navigation.add_page_at_path(section_path[:], page)

            for file_name in file_names:
                file_path = os.path.join(dir_path, file_name)
                if os.path.exists(file_path):
                    page = self._parse_page(file_path)
                    self.pages.append(page)
                    self.navigation.add_page_at_path(section_path[:], page)

        # Now setup the navigation context processor
        self.context_processor(self._inject_navigation)



    def _post_boot(self):
        """Do post-boot tasks."""
        pass

    def _parse_page(self, page_path):
        """Parse a content page

        :param page_path: Path for content page to parse
        """
        if not os.path.exists(page_path):
            raise ContentException('Could not find file for content page "%s"' % page_path)

        with open(page_path, 'r') as f:
            file_string = f.read()

        return Page(self, file_string, page_path)

    def _inject_navigation(self):
        return dict(navigation=self.navigation)

    def _clear_page_cache(self):
        """Remove all cached pages."""
        for p in self.pages:
            p.page_cache = None

    def error_page_not_found(self, e):
        """ Show custom 404 page

        :param e:
        """
        # TODO: Make this use the 404.md
        return "404 - TODO: Make this use the 404.md", 404

    def find_page(self, path):
        """

        :param path:
        """
        for p in self.pages:
            if p.url_path == path:
                return p

        return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Development Server Help')
    parser.add_argument("-d", "--debug", action="store_true", dest="debug_mode",
                  help="run in debug mode (for use with PyCharm)", default=False)
    parser.add_argument("-p", "--port", dest="port",
                  help="port of server (default:%(default)s)", type=int, default=5000)

    cmd_args = parser.parse_args()
    run_options = {"port": cmd_args.port }

    if cmd_args.debug_mode:
        run_options["debug"] = True
        run_options["use_debugger"] = False
        run_options["use_reloader"] = False

    my_site = MDSite(
        'MDWeb',        # Site name, this gets passed in as the Flask name
        config_filename='TestSiteConfig.py',  # Config file name for the site
        app_options={}  # Flask options that will be passed through to the Flask() constructor
    )
    my_site.run(**run_options)