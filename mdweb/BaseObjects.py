"""MDWeb Base Navigation Item.

This is broken out into a separate file to avoid circular imports.
"""
import re

from mdweb.Exceptions import PageMetaInfFieldException


class NavigationBaseItem(object):  # pylint: disable=R0903

    """Base object for navigation items such as nav-levels or pages."""

    #: Type of navigation item
    @property
    def nav_type(self):
        """Return the type of this nav item (the class name)."""
        return self.__class__.__name__


class MetaInfParser(object):  # pylint: disable=R0903

    """Base Meta Inf Parser."""

    FIELD_TYPES = {}
    FIELD_VALUE_REGEX = r'^(?P<key>[a-zA-Z0-9 ]*):(?P<value>.*)$'

    def __init__(self, meta_string):
        """Initialize the parser."""
        # Initialize attributes defined in FIELD_TYPES
        for attribute, attribute_details in self.FIELD_TYPES.items():
            setattr(self, attribute, attribute_details[1])

        self._parse_meta_inf(meta_string)

    def _parse_meta_inf(self, meta_inf_string):
        """Parse given meta information string into a dictionary.

        :param meta_inf_string: Raw meta content
        """
        lines = meta_inf_string.split('\n')

        for line in lines:
            if line.strip(' ') == '' or re.match(r'^ *#', line):
                continue
            match = re.search(self.FIELD_VALUE_REGEX, line)
            key = match.group('key').strip().lower().replace(' ', '_')
            value = match.group('value').strip()
            if key not in self.FIELD_TYPES.keys():
                raise PageMetaInfFieldException("Unsupported field '%s'" % key)
            # Cast field value to appropriate type
            if '' == value:
                raise PageMetaInfFieldException(
                    "Empty value for meta-inf field '%s'" % key)
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
