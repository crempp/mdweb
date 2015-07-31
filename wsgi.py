from mdweb import MDSite

app = MDSite(
    'MyTestSite',  # Site name, this gets passed in as the Flask name
    config_filename='TestSiteConfig.py',  # Config file name for the site
    app_options={}  # Flask options that will be passed through to the Flask() constructor
)

if __name__ == "__main__":
    app.run()
