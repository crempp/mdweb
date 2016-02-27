class ThemeException(Exception):
    pass


class ConfigException(Exception):
    pass


class ContentException(Exception):

    """Markdown content exception."""

    pass


class ContentStructureException(Exception):

    """Invalid structure of content directory."""

    pass


class PageMetaInfFieldException(Exception):

    """Invalid field in page metadata."""

    pass


class PageParseException(Exception):

    """Error parsing page markdown."""

    pass


class FileExistsError(Exception): # pylint: disable=W0622

    """Shim for FileExistsError in Python 2.x."""

    pass


class PermissionError(Exception): # pylint: disable=W0622

    """Shim for FileExistsError in Python 2.x."""

    pass
