/*
Title: Dev Server
Nav Name: Dev Server
Order: 4
*/

#MDWeb Development Server

The `dev_server` script starts a minimal development server which is based on
the Werkzeug (WSGI) server. This is not for production use and will perform
abysmally under even trivial loads.

    usage: dev_server [-h] [-d] [-p PORT] [-n NAME] [-l] [--log-level LOG_LEVEL]
                      site
    
    Development Server Help
    
    positional arguments:
      site                  site class
    
    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           run in debug mode (for use with PyCharm)
      -p PORT, --port PORT  port of server (default:5000)
      -n NAME, --name NAME  application name
      -l, --list-sites      list available applications
      --log-level LOG_LEVEL
                            logging level ('CRITICAL', 'ERROR, 'WARNING','INFO',
                            'DEBUG', 'NOTSET')

