import logging
import os

import blinker
import jinja2
from flask import (
    Flask,
    send_from_directory,
    send_file,
)
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mdweb.Index import Index
from mdweb.SiteMapView import SiteMapView
from mdweb.Navigation import Navigation

# Shim Python 3.x Exceptions
if 'FileExistsError' not in __builtins__.keys():
    from mdweb.Exceptions import FileExistsError

# Setup signals
sig_namespace = blinker.Namespace()
mdw_signaler = {
    'pre-boot' : sig_namespace.signal('pre-boot'),
    'pre-navigation-scan': sig_namespace.signal('pre-navigation-scan'),
    'post-navigation-scan': sig_namespace.signal('post-navigation-scan'),
    'pre-app-start' : sig_namespace.signal('pre-app-start'),
    'post-app-start' : sig_namespace.signal('post-app-start'),
    'pre-config' : sig_namespace.signal('pre-config'),
    'post-config' : sig_namespace.signal('post-config'),
    'post-boot': sig_namespace.signal('post-boot'),
}

BASE_SETTINGS = {
    #: enable/disable Flask debug mode
    'DEBUG': False,

    #: enable/disable Flask testing mode
    'TESTING': False,

    #: Flask secret key
    # To generate a secret key you can use the os.urandom function
    #
    # >>> import os
    # >>> os.urandom(24)
    'SECRET_KEY': 'super_secret_development_key',

    #: Path to page content relative to application root
    'CONTENT_PATH': 'content/',

    #: Name of theme (should be a sub-folder in themes/
    'THEME': 'alpha',
}

BASE_SITE_OPTIONS = {
    #: Python logging level
    'logging_level': "ERROR",
}

class MDSite(Flask):
    """ MDWeb site

    An MDWeb Site is very closely related to a Flask application.
    """

    #: Assets that must live at the root level and thus require special routing
    ROOT_LEVEL_ASSETS = [
        'crossdomain.xml',
        'favicon.ico',
        'humans.txt',
        'robots.txt',
    ]

    #: Navigation structure
    navigation = None

    def __init__(self, site_name, app_options={}, site_options={}):
        """
        Initialize the Flask application and start the app.

        :param site_name: The name of the site, will be used as the flask
                          import_name.

        :param app_options: Additional parameters to be passed to Flask
                            constructor

        :param site_options: Options specific to MDWeb sites
        """

        self.site_name = site_name
        self.app_options = app_options
        self.site_options = BASE_SITE_OPTIONS
        self.site_options.update(site_options)
        self.pages = []
        self.content_observer = None
        self.theme_observer = None
        self.navigation = None

        self.start()
        if not self.config['TESTING']:
            self._register_observers()

    def start(self):
        """Go through the boot up process sending signals for each stage."""
        super(MDSite, self).__init__(self.site_name, **self.app_options)

        #: START THE BOOT PROCESS
        mdw_signaler['pre-boot'].send(self)
        self._stage_pre_boot()

        #: START THE FLASK APP
        # We must start the app straight away because we can't get the config
        # easily until we do. The rest of the boot tasks will require the
        # config.
        mdw_signaler['pre-app-start'].send(self)
        self._stage_create_app()
        mdw_signaler['post-app-start'].send(self)

        #: LOAD THE CONFIG
        mdw_signaler['pre-config'].send(self)
        self._stage_load_config()
        mdw_signaler['post-config'].send(self)

        #: SETUP NAVIGATION
        mdw_signaler['pre-navigation-scan'].send(self)
        self.navigation = Navigation(self.config['CONTENT_PATH'])
        self.pages = self.navigation.get_page_dict()
        self.context_processor(self._inject_navigation)
        mdw_signaler['post-navigation-scan'].send(self)

        #: FINISH THINGS UP
        self._stage_post_boot()
        mdw_signaler['post-boot'].send(self)

    def get_page(self, url_path):
        """
        Lookup the page for the given url path

        :param url_path:
        :return: Page object matching the requested url path
        """
        for page_url, page in self.pages.items():
            if page.url_path == url_path:
                return page

        return None

    def error_page_not_found(self, e):
        """ Show custom 404 page

        :param e:
        """
        # TODO: Make this use the 404.md
        return "404 - TODO: Make this use the 404.md", 404

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

                _this.start()

        event_handler = ContentHandler()

        # Listen for content changes
        self.content_observer = Observer()
        self.content_observer.schedule(event_handler,
                                       self.config['CONTENT_PATH'],
                                       recursive=True)
        self.content_observer.start()

        # If we're debugging, listen for theme changes
        if self.debug:
            self.theme_observer = Observer()
            self.theme_observer.schedule(event_handler,
                                         self.config['THEME_FOLDER'],
                                         recursive=True)
            self.theme_observer.start()

    def _stage_pre_boot(self):
        """Do pre-boot tasks."""
        pass

    def _stage_create_app(self):
        """Create the Flask application."""

        # Setup special root-level asset routes
        # NOTE: The usage of url_for doesn't work here. Rather, use a view with
        # send_from_directory() - http://stackoverflow.com/a/20648053/1436323
        def special_root_file(filename):
            return send_file(os.path.join(self.config['CONTENT_PATH'],
                                          filename))
        for asset in self.ROOT_LEVEL_ASSETS:
            self.add_url_rule('/%s' % asset, view_func=special_root_file,
                              defaults={'filename': asset})

        # Setup content asset route
        def custom_static(filename):
            return send_from_directory(self.config['CONTENT_ASSET_PATH'],
                                       filename)
        self.add_url_rule('/contentassets/<path:filename>',
                          view_func=custom_static)

        # Sitemap route
        self.add_url_rule('/sitemap.xml',
                          view_func=SiteMapView.as_view('sitemap'))

        # Route all remaining requests to the index view
        self.add_url_rule('/', view_func=Index.as_view('index'),
                          defaults={'path': ''})
        self.add_url_rule('/<path:path>',
                          view_func=Index.as_view('index_with_path'))

        # Setup error handler pages
        self.error_handler_spec[None][404] = self.error_page_not_found

        # Setup logging
        log_level = getattr(logging, self.site_options['logging_level'])
        logging.basicConfig(level=log_level,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def _stage_load_config(self):
        """Load the configuration of the application being started.

         :param filename: Application's configuration filename
         """
        self_fqcn = self.__module__ + "." + self.__class__.__name__
        self.config.from_object('%s.MDConfig' % self_fqcn)

        path_to_here = os.path.dirname(os.path.realpath(__file__))
        self.config['BASE_PATH'] = os.path.abspath(os.path.join(path_to_here,
                                                                os.pardir))

        # Build the full path the the theme folder using the theme name
        self.config['THEME_FOLDER'] = os.path.join(
            self.config['BASE_PATH'],
            'themes',
            self.config['THEME']
        )

        # Ensure theme directory exists
        if not os.path.isdir(self.config['THEME_FOLDER']) or \
                not os.path.exists(self.config['THEME_FOLDER']):
            raise FileExistsError("Theme directory %s does not exist" %
                                  self.config['THEME_FOLDER'])

        # Set the template directory to the configured theme's template
        # directory
        # http://stackoverflow.com/a/13598839
        my_loader = jinja2.ChoiceLoader([
                self.jinja_loader,
                jinja2.FileSystemLoader([
                    os.path.join(self.config['THEME_FOLDER'], 'templates'),
                ]),
            ])
        self.jinja_loader = my_loader

        # Extend the content path to the absolute path
        if not self.config['CONTENT_PATH'].startswith('/'):
            self.config['CONTENT_PATH'] = os.path.join(
                self.config['BASE_PATH'],
                self.config['CONTENT_PATH']
            )

        # Ensure content directory exists
        if not os.path.isdir(self.config['CONTENT_PATH']) or \
                not os.path.exists(self.config['CONTENT_PATH']):
            raise FileExistsError("Content directory %s does not exist" %
                                  self.config['CONTENT_PATH'])

        # Set the static theme assets folder path
        self.static_folder = os.path.join(self.config['THEME_FOLDER'],
                                          'assets')

        # Set the content asset path
        self.config['CONTENT_ASSET_PATH'] = os.path.join(
            self.config['CONTENT_PATH'], 'assets')

    def _stage_post_boot(self):
        """Do post-boot tasks."""
        pass

    def _inject_navigation(self):
        return dict(navigation=self.navigation)
