"""Sample site class."""
from mdweb.MDSite import MDSite


class MySite(MDSite):
    """An example MDWeb site."""

    class MDConfig:  # pylint: disable=R0903
        """Configuration of the example site."""

        #: enable/disable Flask debug mode
        DEBUG = True

        #: Flask secret key
        # To generate a secret key you can use the os.urandom function
        #
        # >>> import os
        # >>> os.urandom(24)
        SECRET_KEY = 'create_a_secret_key_for_use_in_production'

        #: Path to page content relative to application root
        CONTENT_PATH = 'demo-content/'

        #: Name of theme (should be a sub-folder in themes/
        THEME = 'bootstrap'

        #: Google Analytics tracking ID. If False GA tracking will not be used.
        # Your GA tracking ID will look like 'UA-00000000-1'
        GA_TRACKING_ID = False

        DEBUG_HELPER = False
