import re
from flask.views import View

from mdweb.Exceptions import PageMetaInfFieldException


class PageMetaInf(object):
    """MDWeb Page Meta Information"""
    #: A regex for extracting meta information (and comments). This will be
    # replaced with a compiled version of the regex at boot time.
    META_INF_REGEX = r'/\*(.*)\*/'

    FIELD_TYPES = {
        'title': str,
        'description': str,
        'author': str,
        'date': str,
        'order': int,
        'template': str,
        'robots': str,
    }

    def __init__(self, file_string):
        """Content page meta-information.

        If a page defines a non-standard meta value it is blindly included.

        :param file_string: Raw page content as a string
        """

        meta_inf_regex = re.compile(self.META_INF_REGEX,  flags=re.DOTALL)
        match = meta_inf_regex.search(file_string)

        self.title = None
        self.description = None
        self.author = None
        self.date = None
        self.order = 0
        self.template = None
        self.robots = None

        if match:
            self._parse_meta_inf(match.group(1))

    def _parse_meta_inf(self, meta_inf_string):
        """Parse given meta information string into a dictionary of meta
        information key:value pairs.

        :param meta_inf_string: Raw meta content
        """

        lines = meta_inf_string.split('\n')

        for l in lines:
            if l.strip(' ') == '' or re.match(r'^ *#', l):
                continue
            match = re.search(r'^(?P<key>[a-zA-Z0-9 ]*):(?P<value>.*)$', l)
            key = match.group('key').strip().lower()
            value = match.group('value').strip()
            if key not in self.FIELD_TYPES.keys():
                raise PageMetaInfFieldException("Unsupported field '%s'" % key)
            # Cast field value to appropriate type
            value = self.FIELD_TYPES[key](value)
            setattr(self, key, value)


class Page(View):
    """MDWeb Page View"""
    def __init__(self, filepath):
        self.filepath = filepath

    def __repr__(self):
        return '{0}'.format(self.filepath)

