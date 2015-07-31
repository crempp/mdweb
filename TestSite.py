#!/usr/bin/env python
from mdweb import MDSite

my_site = MDSite(
    'MyTestSite',  # Site name, this gets passed in as the Flask name
    config_filename='TestSiteConfig.py',  # Config file name for the site
    app_options={}  # Flask options that will be passed through to the Flask() constructor
)

my_site.run()
