"""
MDWeb Base Navigation Item.

This is broken out into a seperate file to avoid circular imports.
"""


class NavigationBaseItem(object):
    #: Type of navigation item
    @property
    def nav_type(self):
        return self.__class__.__name__
