"""
MDWeb Base Navigation Item.

This is broken out into a seperate file to avoid circular imports.
"""
import re

from mdweb.Exceptions import PageMetaInfFieldException


class NavigationBaseItem(object):
    #: Type of navigation item
    @property
    def nav_type(self):
        return self.__class__.__name__


class MetaInfParser(object):
    """ Base Meta Inf Parser """
    FIELD_TYPES = {}
    FIELD_VALUE_REGEX = ""

    def __init__(self, meta_string):

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
