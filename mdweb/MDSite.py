"""The MDWeb Site object."""
import glob
import logging
import os

import blinker
import jinja2
from flask import (
    Flask,
    send_from_directory,
    send_file,
    abort,
)
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from werkzeug.debug import get_current_traceback

from mdweb.Index import Index
from mdweb.SiteMapView import SiteMapView
from mdweb.Navigation import Navigation
from mdweb.Page import Page

# Shim Python 3.x Exceptions
if 'FileExistsError' not in __builtins__.keys():
    from mdweb.Exceptions import FileExistsError  # pylint: disable=W0622

# Setup signals
SIG_NAMESPACE = blinker.Namespace()
MDW_SIGNALER = {
    'pre-boot': SIG_NAMESPACE.signal('pre-boot'),
    'pre-navigation-scan': SIG_NAMESPACE.signal('pre-navigation-scan'),
    'post-navigation-scan': SIG_NAMESPACE.signal('post-navigation-scan'),
    'pre-app-start': SIG_NAMESPACE.signal('pre-app-start'),
    'post-app-start': SIG_NAMESPACE.signal('post-app-start'),
    'pre-config': SIG_NAMESPACE.signal('pre-config'),
    'post-config': SIG_NAMESPACE.signal('post-config'),
    'post-boot': SIG_NAMESPACE.signal('post-boot'),
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
    
    #: Google Analytics tracking ID. If False GA tracking will not be used.
    # Your GA tracking ID will look like 'UA-00000000-1'
    'GA_TRACKING_ID': False,
}

BASE_SITE_OPTIONS = {
    #: Python logging level
    'logging_level': "ERROR",
}


class MDSite(Flask):
    """MDWeb site.

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

    # pylint: disable=W0231
    def __init__(self, site_name, app_options=None, site_options=None):
        """Initialize the Flask application and start the app.

        :param site_name: The name of the site, will be used as the flask
                          import_name.
        :param app_options: Additional parameters to be passed to Flask
                            constructor
        :param site_options: Options specific to MDWeb sites
        """
        self.site_name = site_name
        self.app_options = {} if app_options is None else app_options
        self.site_options = BASE_SITE_OPTIONS
        self.site_options.update({} if site_options is None else site_options)
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
        MDW_SIGNALER['pre-boot'].send(self)
        self._stage_pre_boot()

        #: START THE FLASK APP
        # We must start the app straight away because we can't get the config
        # easily until we do. The rest of the boot tasks will require the
        # config.
        MDW_SIGNALER['pre-app-start'].send(self)
        self._stage_create_app()
        MDW_SIGNALER['post-app-start'].send(self)

        #: LOAD THE CONFIG
        MDW_SIGNALER['pre-config'].send(self)
        self._stage_load_config()
        MDW_SIGNALER['post-config'].send(self)

        #: SETUP NAVIGATION
        MDW_SIGNALER['pre-navigation-scan'].send(self)
        self.navigation = Navigation(self.config['CONTENT_PATH'])
        self.pages = self.navigation.get_page_dict()
        self.context_processor(self._inject_navigation)
        self.context_processor(self._inject_ga_tracking)
        MDW_SIGNALER['post-navigation-scan'].send(self)

        #: FINISH THINGS UP
        self._stage_post_boot()
        MDW_SIGNALER['post-boot'].send(self)

    def get_page(self, url_path):
        """Lookup the page for the given url path.

        :param url_path:
        :return: Page object matching the requested url path
        """
        for page_url, page in self.pages.items():
            if page.url_path == url_path:
                return page

        return None

    def error_page(self, error):
        """Show custom error pages.

        :param error:
        """
        def render_custom_error(code, path):
            """Render an error page with a custom content file."""
            track = get_current_traceback(skip=1, show_hidden_frames=True,
                                          ignore_system_exceptions=False)
            track.log()
            
            page = Page(self.config['CONTENT_PATH'], path)
            return Index.render(page), code
        
        def render_simple_error(code):
            """Render an error page without a content file."""
            track = get_current_traceback(skip=1, show_hidden_frames=True,
                                          ignore_system_exceptions=False)
            track.log()
            
            if hasattr(error, 'description'):
                error_message = error.description
            else:
                error_message = str(error)
                
            return error_message, code

        # Determine the error code for this error
        if not hasattr(error, 'code') and isinstance(error, Exception):
            error_code = 500
        else:
            error_code = error.code

        # Construct the path to the content file for this error
        custom_file_path = os.path.join(self.config['CONTENT_PATH'],
                                        '%s.md' % error_code)
        
        # If there exists a file for this error use it, otherwise just return
        # a simple error message
        if os.path.isfile(custom_file_path):
            return render_custom_error(error_code, custom_file_path)
        else:
            return render_simple_error(error_code)

    def _register_observers(self):
        """Setup a watcher to rebuild the nav whenever a file has changed."""
        _this = self

        class ContentHandler(FileSystemEventHandler):

            """Custom event handler for changed files."""

            def on_modified(self, event):
                logging.debug('%s "%s" was "%s"',
                              'Directory' if event.is_directory else "File",
                              event.src_path,
                              event.event_type)

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
        def special_root_file(root_filename):
            """Root file Flask view."""
            path = os.path.join(self.config['CONTENT_PATH'], root_filename)
            if os.path.isfile(path):
                return send_file(path)
            else:
                abort(404)
                
        for asset in self.ROOT_LEVEL_ASSETS:
            self.add_url_rule('/%s' % asset, view_func=special_root_file,
                              defaults={'root_filename': asset})
        
        def boom():
            """A view that will result in a server error.
            
            Used to test 500 errors
            """
            a = 1 / 0
            return a
        self.add_url_rule('/boom', view_func=boom)

        # Setup content asset route
        def custom_static(asset_filename):
            """Custom static file Flask view."""
            return send_from_directory(self.config['CONTENT_ASSET_PATH'],
                                       asset_filename)
        self.add_url_rule('/contentassets/<path:asset_filename>',
                          view_func=custom_static)

        # Sitemap route
        self.add_url_rule('/sitemap.xml',
                          view_func=SiteMapView.as_view('sitemap'))

        # Route all remaining requests to the index view
        self.add_url_rule('/', view_func=Index.as_view('index'),
                          defaults={'path': ''})
        self.add_url_rule('/<path:path>',
                          view_func=Index.as_view('index_with_path'))

        # Setup error handler
        for code in [400, 403, 404, 405, 410, 500, 501, 503, Exception]:
            # self.error_handler_spec[None][code] = self.error_page
            self.register_error_handler(code, self.error_page)

        # Setup logging
        log_level = getattr(logging, self.site_options['logging_level'])
        logging.basicConfig(level=log_level,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def _stage_load_config(self):
        """Load the configuration of the application being started."""
        self_fqcn = self.__module__ + "." + self.__class__.__name__
        self.config.from_object('%s.MDConfig' % self_fqcn)
        
        # Extend the base config with the loaded config values. This will ensure
        # we have every config set.
        self.config = dict(BASE_SETTINGS, **self.config)

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
        """Inject the entire navigation structure into the context"""
        return dict(navigation=self.navigation)

    def _inject_ga_tracking(self):
        """Render the Google Analytics tracking code if enabled and add to the
        context."""
        context = dict(ga_tracking="")
        if self.config['GA_TRACKING_ID']:
            context['ga_tracking'] = """<script>
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
    
    ga('create', '%s', 'auto');
    ga('send', 'pageview');
</script>""" % self.config['GA_TRACKING_ID']
        
        return context
