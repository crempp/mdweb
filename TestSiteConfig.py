#: enable/disable Flask debug mode
DEBUG = True

#: Flask secret key
# To generate a secret key you can use the os.urandom function
#
# >>> import os
# >>> os.urandom(24)
SECRET_KEY = '\x85\xa2\x1c\xfd\x07MF\xcb_ ]\x1e\x9e\xab\xa2qn\xd1\x82\xcb^\x11x\xc5'

#: A regex for extracting meta information (and comments). This will be
# replaced with a compiled version of the regex at boot time.
META_INF_REGEX = r'/\*(.*)\*/'

#: Path to page content relative to application root
CONTENT_PATH = 'demo-content/'

#: Name of theme (should be a sub-folder in themes/
THEME = 'bootstrap'