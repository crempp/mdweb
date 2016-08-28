#!/usr/bin/env python
"""WSGI server implementation for use by Gunicorn.

If the following OS environment variables are provided they will be used to
generate a site class
  * SITE_NAME
  * DEBUG
  * SECRET_KEY
  * CONTENT_PATH
  * THEME
otherwise the default MySite will be used.
"""
import os
from mdweb.MDSite import MDSite

# If all required environment variables are set use them to build a site class
if ('SITE_NAME' in os.environ and
    'DEBUG' in os.environ and
    'SECRET_KEY' in os.environ and
    'CONTENT_PATH' in os.environ and
    'THEME' in os.environ
    ):
    class SiteClass(MDSite):

        """SiteClass is MDSite class created from OS env vars."""

        class MDConfig:  # pylint: disable=R0903

            """Set the config values based on OS env vars."""

            DEBUG = os.environ['DEBUG']
            SECRET_KEY = os.environ['SECRET_KEY']
            CONTENT_PATH = os.environ['CONTENT_PATH']
            THEME = os.environ['THEME']

    app = SiteClass(
        os.environ['SITE_NAME'],
        # Flask options that will be passed through to the Flask() constructor
        app_options={}
    )

else:
    from sites.MySite import MySite
    app = MySite(
        "MySite",
        # Flask options that will be passed through to the Flask() constructor
        app_options={}
    )

if __name__ == "__main__":
    app.start()
    app.run()
