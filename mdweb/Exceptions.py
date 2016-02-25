class ThemeException(Exception):
    pass


class ConfigException(Exception):
    pass


class ContentException(Exception):
    pass


class ContentStructureException(Exception):
    pass


class PageMetaInfFieldException(Exception):
    pass


class PageParseException(Exception):
    pass


# Shims for Python 3.x Exceptions
class FileExistsError(Exception):
    pass


class PermissionError(Exception):
    pass
