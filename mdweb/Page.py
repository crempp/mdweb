import re
from flask.views import View
import markdown
import os

from mdweb.Exceptions import (
    PageMetaInfFieldException,
    ContentException,
    PageParseException,
)
from mdweb.NavigationBaseItem import NavigationBaseItem


class PageMetaInf(object):
    """MDWeb Page Meta Information"""

    FIELD_VALUE_REGEX = r'^(?P<key>[a-zA-Z0-9 ]*):(?P<value>.*)$'

    FIELD_TYPES = {
        'title': ('unicode', None),
        'nav_name': ('unicode', None),
        'description': ('unicode', None),
        'author': ('unicode', None),
        'date': ('unicode', None),
        'order': ('int', 0),
        'template': ('unicode', None),
        'robots': ('unicode', None),
    }

    def __init__(self, meta_string):
        """Content page meta-information.

        If a page defines a non-standard meta value it is blindly included.

        :param file_string: Raw page content as a string
        """

        # Initialize attributes defined in FIELD_TYPES
        for attribute, attribute_details in self.FIELD_TYPES.items():
            setattr(self, attribute, attribute_details[1])

        self._parse_meta_inf(meta_string)

    def _parse_meta_inf(self, meta_inf_string):
        """Parse given meta information string into a dictionary of meta
        information key:value pairs.

        :param meta_inf_string: Raw meta content
        """

        lines = meta_inf_string.split('\n')

        for l in lines:
            if l.strip(' ') == '' or re.match(r'^ *#', l):
                continue
            match = re.search(self.FIELD_VALUE_REGEX, l)
            key = match.group('key').strip().lower().replace(' ', '_')
            value = match.group('value').strip()
            if key not in self.FIELD_TYPES.keys():
                raise PageMetaInfFieldException("Unsupported field '%s'" % key)
            # Cast field value to appropriate type
            if 'int' == self.FIELD_TYPES[key][0]:
                value = int(value)
            elif 'unicode' == self.FIELD_TYPES[key][0]:
                if 'unicode' in __builtins__.keys():
                    # Python 2.x
                    value = __builtins__['unicode'](value)
                else:
                    # Python 3.x
                    value = str(value)

            setattr(self, key, value)

        self.nav_name = self.title if self.nav_name is None else self.nav_name

class Page(View, NavigationBaseItem):
    """MDWeb Page View"""

    #: A regex for extracting meta information (and comments).
    META_INF_REGEX = r'(/\*(?P<metainf>.*)\*/)?(?P<content>.*)'

    #: A regex to extract the url path from the file path
    URL_PATH_REGEX = r'^%s(?P<path>[^\0]*?)(index)?(\.md)'

    def __init__(self, content_path, page_path):
        self.page_path = page_path

        # Extract the part of the page_path that will be used as the URL path
        pattern = self.URL_PATH_REGEX % content_path
        matches = re.match(pattern, self.page_path)
        if matches:
            self.url_path = matches.group('path').rstrip('/').lstrip('/')
        else:
            raise PageParseException("Unable to parse page path [%s]" %
                                     content_path)

        if not os.path.exists(self.page_path):
            raise ContentException('Could not find file for content page "%s"' %
                                   page_path)

        # Read the page file
        with open(self.page_path, 'r') as f:
            file_string = f.read()

        # Separate the meta information and the page content
        meta_inf_regex = re.compile(self.META_INF_REGEX, flags=re.DOTALL)
        match = meta_inf_regex.search(file_string)
        meta_inf_string = match.group('metainf') if match.group('metainf') else ''
        content_string = match.group('content')

        self.meta_inf = PageMetaInf(meta_inf_string)

        # Strip the meta information and comments
        self.markdown_str = content_string

        # The page will be rendered on first view
        self.page_html = self.parse_markdown(self.markdown_str)

    def parse_markdown(self, page_markdown):
        """Parse given markdown string into rendered html."""
        page_html = markdown.markdown(page_markdown)

        return page_html

    def __repr__(self):
        return '{0}'.format(self.page_path)
