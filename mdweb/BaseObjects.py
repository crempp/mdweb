"""MDWeb Base Navigation Item.

This is broken out into a separate file to avoid circular imports.
"""
import re

from mdweb.Exceptions import PageMetaInfFieldException
from mdweb.metafields import META_FIELDS as MDW_META_FIELDS


class NavigationBaseItem(object):  # pylint: disable=R0903

    """Base object for navigation items such as nav-levels or pages."""

    #: Type of navigation item
    @property
    def nav_type(self):
        """Return the type of this nav item (the class name)."""
        return self.__class__.__name__


class MetaInfParser(object):  # pylint: disable=R0903

    """Base Meta Inf Parser."""

    #: Registered meta fields, can be overridden by inheriting class.
    META_FIELDS = MDW_META_FIELDS

    #: Regular expression to extract meta field key-value pairs.
    # can be overridden by inheriting class.
    FIELD_VALUE_REGEX = r"^(?P<key>[a-zA-Z0-9 ]+):(?P<value>.+)$"

    def __init__(self, meta_string):
        """Initialize the parser."""
        # Initialize attributes defined in FIELD_TYPES
        for attribute, attribute_details in self.META_FIELDS.items():
            setattr(self, attribute, attribute_details[1])

        self._parse_meta_inf(meta_string)

    def _parse_meta_inf(self, meta_inf_string):
        """Parse given meta information string into a dictionary.

        :param meta_inf_string: Raw meta content
        """
        # Metainf fields now support multi-line values. New lines must be
        # indented with at least one whitespace character.
        # NOTE: This regex leaves blank lines and comments in but that will
        # be handled in the line processing loop
        line_regex = '(?P<line>[a-zA-Z0-9 ]+:(?:(?![\n]+\w)[\w\W\r\n])+)'
        line_matches = re.findall(line_regex, meta_inf_string)
        line_blocks = line_matches

        for line_block in line_blocks:
            # Split the line block into seperate lines and process each line
            lines = line_block.split('\n')
            processed_line = ''
            for line in lines:
                # Remove blank lines and comments
                if line.strip(' ') == '' or re.match(r'^ *#', line):
                    continue
                # Strip beginning and trailing whitespace and newlines
                line = line.strip(' \t\n\r')

                processed_line += ' ' + line

            match = re.search(self.FIELD_VALUE_REGEX, processed_line)
            if match is None:
                raise PageMetaInfFieldException(
                    "Improperly formated metainf line '%s'" % processed_line)
            key = match.group('key').strip().lower().replace(' ', '_')
            value = match.group('value').strip()
            if key not in self.META_FIELDS.keys():
                raise PageMetaInfFieldException("Unsupported field '%s'" % key)
            # Cast field value to appropriate type
            if '' == value:
                raise PageMetaInfFieldException(
                    "Empty value for meta-inf field '%s'" % key)
            if 'int' == self.META_FIELDS[key][0]:
                value = int(value)
            elif 'unicode' == self.META_FIELDS[key][0]:
                if 'unicode' in __builtins__.keys():
                    # Python 2.x
                    value = __builtins__['unicode'](value)
                else:
                    # Python 3.x
                    value = str(value)

            setattr(self, key, value)
