#!/usr/bin/env python
from mdweb import MDSite

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

    app_options = {
        'static_path': None,
        'static_url_path': None,
        'static_folder': 'static',
        'template_folder': 'templates',
        'instance_path': None,
        'instance_relative_config': False,
    }

    my_site = MDSite(
        'MyTestSite',  # Site name, this gets passed in as the Flask name
        config_filename='TestSiteConfig.py',  # Config file name for the site
        app_options=app_options  # Flask options that will be passed through to the Flask() constructor
    )

    my_site.run(**run_options)
