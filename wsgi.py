#!/usr/bin/env python
import os
from mdweb.MDSite import MDSite

# If all required environment variables are set use them to build a site class
if ( 'SITE_NAME' in os.environ and
     'DEBUG' in os.environ and
     'SECRET_KEY' in os.environ and
     'CONTENT_PATH' in os.environ and
     'THEME' in os.environ
    ):
    
    class SiteClass(MDSite):
        class MDConfig:
            DEBUG = os.environ['DEBUG']
            SECRET_KEY = os.environ['SECRET_KEY']
            CONTENT_PATH = os.environ['CONTENT_PATH']
            THEME = os.environ['THEME']

    app = SiteClass(
        os.environ['SITE_NAME'],
        app_options={} # Flask options that will be passed through to the Flask() constructor
    )

else:
    from sites.MySite import MySite
    app = MySite(
        "MySite",
        app_options={}  # Flask options that will be passed through to the Flask() constructor
    )

if __name__ == "__main__":
    app.start()
    app.run()
