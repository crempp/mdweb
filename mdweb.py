#!/usr/bin/env python
"""
MDWeb is a markdown based web site framework.  MDWeb is painstakingly designed
to be as minimalistic as possible while taking less than 5 minutes to setup
and less than one minute to add content.  This project was borne out of my
frustration with maintaining websites and adding content. I'm a firm believer
in the ethos that CMS is an evil that should be rid from this world. I spent
years fighting horrific battles with enemies such as Drupal, Wordpress and
Joomla. The things I saw during those dark days can not be unseen.  After
years of batlle, this weary web development soldier built himself a a tiny
oasis. This is MDWeb, I hope you find respite in it.
"""

import logging
import markdown
import os
import re
import blinker
import jinja2
from werkzeug.exceptions import abort
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from flask import (
    Flask,
    Config,
    render_template,
    render_template_string,
    current_app,
)
from flask.helpers import get_root_path
from flask.views import View

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


class ThemeException(Exception):
    pass


class ConfigException(Exception):
    pass


class ContentException(Exception):
    pass


class PageMetaInf(object):
    """MDWeb Page Meta Information"""

    def __init__(self, app, file_string):
        """Content page meta-information.

        If a page defines a non-standard meta value it is blindly included.

        :param app: Flask application

        :param file_string: Raw page content as a string
        """

        meta_inf_regex = app.config['META_INF_REGEX']
        match = meta_inf_regex.search(file_string)

        self.title = None
        self.description = None
        self.author = None
        self.date = None
        self.order = 0
        self.template = None
        self.robots = None

        if match:
            self._parse_meta_inf(match.group(1))

    def _parse_meta_inf(self, meta_inf_string):
        """Parse given meta information string into a dictionary of meta
        information key:value pairs.

        :param meta_inf_string: Raw meta content
        """

        lines = meta_inf_string.split('\n')

        for l in lines:
            if l == '':
                continue
            (k, v) = l.split(':')
            setattr(self, k.lower(), v.strip())


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
        pattern = r'^%s(?P<path>[a-zA-Z0-9_\/]*?)(index)?(\.md)' % self.app.config['CONTENT_PATH']
        matches = re.match(pattern, page_path)
        self.url_path = matches.group('path').rstrip('/')

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
        if len(section_path) is 1 and section_path[0] == '':
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
        """Go through the boot up process sending signals for each stage.

        :param site_name: The name of the site, will be used as the flask
                          import_name.

        :param config_filename: Application configuration filename.

        :param app_options: Additional parameters to be passed to Flask
                            constructor
        """
        self.site_name = site_name
        self.app_options = app_options
        self.pages = []

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
        self._load_config(config_filename)
        mdw_signaler['post-config'].send(self)

        #: SCAN FOR CONTENT
        mdw_signaler['pre-content-scan'].send(self)
        self._content_scan()
        mdw_signaler['post-content-scan'].send(self)

        #: FINISH THINGS UP
        self._post_boot()
        mdw_signaler['post-boot'].send(self)

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

        # Build the full path the the theme folder using the theme name
        self.config['THEME_FOLDER'] = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'themes',
            self.config['THEME']
        )

        # TODO: Check for existence of theme folder

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

        # Compile the regex
        if 'META_INF_REGEX' in self.config and \
                        self.config['META_INF_REGEX'] is not None:
            self.config['META_INF_REGEX'] = re.compile(self.config['META_INF_REGEX'],
                                                       flags=re.DOTALL)
        else:
            raise ConfigException("Meta information regex missing")

    def _content_scan(self):
        """Scan site content."""

        # Create navigation
        self.navigation = NavigationLevel()

        # Scan and parse content
        for dir_path, dir_names, file_names in os.walk(self.config['CONTENT_PATH']):
            section_path = re.sub(r'^%s' % self.config['CONTENT_PATH'], '', dir_path).split('/')

            # Load index page for current directory
            index_path = os.path.join(dir_path, 'index.md')
            page = self._parse_page(index_path)

            self.pages.append(page)

            self.navigation.add_page_at_path(section_path, page)

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
    app_options = {"port": cmd_args.port }

    if cmd_args.debug_mode:
        app_options["debug"] = True
        app_options["use_debugger"] = False
        app_options["use_reloader"] = False

    site = MDSite('MDWeb', app_options=app_options)
    site.run()