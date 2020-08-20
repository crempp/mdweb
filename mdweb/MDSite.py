"""The MDWeb Site object."""
import blinker
import jinja2
import json
import logging
import os
import six
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from werkzeug.debug import get_current_traceback
if not six.PY2:
    from html import escape as html_escape
else:
    from cgi import escape as html_escape

from flask import (
    Flask,
    abort,
    request,
    send_file,
    send_from_directory,
)

from mdweb.Index import Index
from mdweb.SiteMapView import SiteMapView
from mdweb.Navigation import Navigation
from mdweb.Page import Page, load_page
from mdweb.metafields import META_FIELDS

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

path_to_here = os.path.dirname(os.path.realpath(__file__))
BASE_PATH = os.path.abspath(os.path.join(path_to_here, os.pardir))

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

    #: Debug helper for exposing context variables, config and other useful
    # information in the browser. Helpful for plugin and them development.
    'DEBUG_HELPER': False
}

BASE_SITE_OPTIONS = {
    #: Python logging level
    'logging_level': "ERROR",
    'testing': False,
}


def load_module(fqcn):
    components = fqcn.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


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
        self.context_processor(self._inject_debug_helper)
        self.context_processor(self._inject_current_page)
        self.context_processor(self._inject_opengraph)
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
            if page.url_path.strip('/') == url_path.strip('/'):
                return page

        return None

    def get_page_from_request(self, req):
        """Lookup the page given a request object.

        :param req:
        :return: Page object matching the request url path
        """
        return self.get_page(req.path)

    def error_page(self, error):
        """Show custom error pages.

        :param error:
        """
        def render_custom_error(code, path):
            """Render an error page with a custom content file."""
            if code == 500:
                track = get_current_traceback(skip=1, show_hidden_frames=True,
                                              ignore_system_exceptions=False)
                if not self.site_options['testing']:
                    track.log()

            page = Page(*load_page(self.config['CONTENT_PATH'], path))
            return Index.render(page), code

        def render_simple_error(code):
            """Render an error page without a content file."""
            if code == 500:
                track = get_current_traceback(skip=1, show_hidden_frames=True,
                                              ignore_system_exceptions=False)
                if not self.site_options['testing']:
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
        """Create the Flask application.

        Setup special root-level asset routes

        NOTE: The usage of url_for doesn't work here. Rather, use a view with
        send_from_directory() - http://stackoverflow.com/a/20648053/1436323
        """

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
        mod = load_module(self_fqcn)
        self.config.from_object(mod.MDConfig)

        # Extend the base config with the loaded config values. This will ensure
        # we have every config set.
        self.config = dict(BASE_SETTINGS, **self.config)
        
        self.config['BASE_PATH'] = BASE_PATH
        
        self.config['PARTIALS_TEMPLATE_PATH'] = os.path.join(
            self.config['BASE_PATH'], 'mdweb', 'partials')

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
        # directory - http://stackoverflow.com/a/13598839
        my_loader = jinja2.ChoiceLoader([
            self.jinja_loader,
            jinja2.FileSystemLoader([
                os.path.join(self.config['THEME_FOLDER'], 'templates'),
            ]),
        ])
        self.jinja_loader = my_loader

        self.jinja_env.filters['sorted_pages'] = self._sorted_pages_filter
        self.jinja_env.filters['published'] = self._published_filter

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
        context.

        We render directly with Jinja to avoid context processor recursion.
        Since this rendering is done within a context processor the context
        processors will run, recurse until stack overflow."""
        context = dict(ga_tracking="")
        if self.config['GA_TRACKING_ID']:
            partial_context = {'ga_id': self.config['GA_TRACKING_ID']}
            ga_code = jinja2.Environment(
                loader=jinja2.FileSystemLoader(
                    self.config['PARTIALS_TEMPLATE_PATH'] + '/')
            ).get_template('google_analytics.html').render(partial_context)
            context['ga_tracking'] = ga_code

        return context

    def _inject_debug_helper(self):
        nav_fields = [
            '_content_path',
            '_root_content_path',
            'child_navs',
            'child_pages',
            'has_page',
            'has_children',
            'is_top',
            'level',
            'name',
            'page',
        ]

        page_fields = [
            'meta_inf',
            'markdown_str',
            'page_html',
            'abstract',
        ]

        context = dict(debug_helper="")

        def nav_to_dict(nav):
            nav_dict = {}
            for f in nav_fields:
                if f in 'child_navs':
                    nav_dict[f] = []
                    for subnav in nav.child_navs:
                        nav_dict[f].append(nav_to_dict(subnav))
                else:
                    nav_dict[f] = getattr(nav, f)

            return nav_dict

        def page_to_dict(p):
            page_dict = {}

            if p is not None:
                for f in page_fields:
                    if f in ['page_html', 'abstract']:
                        value = html_escape(getattr(p, f))
                    elif f == 'meta_inf':
                        value = metainf_to_dict(getattr(p, f))
                    else:
                        value = getattr(p, f)

                    page_dict[f] = value

            return page_dict

        def metainf_to_dict(meta_inf):
            metainf_dict = {}

            for f in META_FIELDS:
                metainf_dict[f] = getattr(meta_inf, f)

            return metainf_dict

        if self.config['DEBUG_HELPER']:
            config = json.dumps(self.config, indent=4, sort_keys=True,
                                default=lambda x: str(x))
            navigation = json.dumps(nav_to_dict(self.navigation), indent=4,
                                    sort_keys=True, default=lambda x: str(x))
            page = json.dumps(page_to_dict(self.get_page(request.path)),
                              indent=4, sort_keys=True,
                              default=lambda x: str(x))

            partial_context = {
                'debug': {
                    'config': config,
                    'navigation': navigation,
                    'page': page,
                }
            }

            debug_output = jinja2.Environment(
                loader=jinja2.FileSystemLoader(
                    self.config['PARTIALS_TEMPLATE_PATH'] + '/')
            ).get_template('debug_helper.html').render(partial_context)
            context['debug_helper'] = debug_output

        return context

    def _inject_current_page(self):
        """Inject the entire navigation structure into the context"""
        page = self.get_page_from_request(request)
        return dict(current_page=page)

    @staticmethod
    def _sorted_pages_filter(page_list, attribute, page_count, reverse):
        def key_getter(d):
            v = getattr(d.meta_inf, attribute) \
                if hasattr(d.meta_inf, attribute) else d.meta_inf.order
            if v is None:
                return d.meta_inf.order
            elif isinstance(v, six.string_types):
                return v.lower()
            else:
                return v

        l = sorted(page_list, key=key_getter, reverse=reverse)
        if page_count is not None:
            l = l[0:page_count]
        return l

    def _inject_opengraph(self):
        """Inject Opengraph tags into the context"""
        page = self.get_page_from_request(request)

        partial_context = {
            'page': page
        }
        og_code = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                self.config['PARTIALS_TEMPLATE_PATH'] + '/')
        ).get_template('opengraph.html').render(partial_context)

        return {'opengraph': og_code}

    @staticmethod
    def _published_filter(page_list):
        return filter(lambda p: p.is_published, page_list)
