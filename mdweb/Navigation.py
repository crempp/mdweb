"""
MDWeb Navigation structure and parsing.

TODO: Describe navigation parsing

Navigation structure
  Navigation(
    _content_path: /my/content
    _root_content_path: /my/content
    child_navs: [
      Navigation(
        _content_path: /my/content/about
        _root_content_path: /my/content
        child_navs: []
        child_pages: [
          Page(),
          Page(),
          ...
        ]
        has_page: True
        has_children: False
        is_top: False
        level: 1
        name: 'about'
        page: Page()
      ),
      ...
    ]
    child_pages: []
    has_page: True
    has_children: True
    is_top: True
    level: 0
    name: None
    page: Page()
  )


Future Features:
    * Ordering navigation levels
"""

import re
import os
import sys

from mdweb.Exceptions import *
from mdweb.Page import Page
from mdweb.NavigationBaseItem import NavigationBaseItem

class Navigation(NavigationBaseItem):
    """ Navigation level representation
    Navigation is built rescursivly by walking the content directory. Each
    directory represents a navigation level, each file represents a page.

    Each nav level's name is determined by the directory name.
    """
    #: Allowed extensions for content files
    extensions = ['md']

    #: Special files to skip
    skip_files = [
        '400.md',
        '403.md',
        '404.md',
        '500.md',
    ]

    #: Root path to content
    _root_content_path = None

    def __init__(self, content_path, nav_level=0):
        #: path to content for current navigation level
        self._content_path = os.path.abspath(content_path)

        #: Ordered list of child Navigatyion objects
        self.child_navs = []

        #: Ordered list of child Page object
        self.child_pages = []

        #: Is this the top level of navigation
        self.is_top = nav_level == 0

        #: Navigation level
        self.level = nav_level

        #: Navigation level name (populated during scan)
        self.name = None

        #: Navigation page if one is provided (populated during scan)
        self.page = None

        #: Does the nav level have an associated page?  (populated during scan)
        self.has_page = False

        #: Path to the root path to content
        if self.level == 0:
            Navigation._root_content_path = self._content_path
            self.name = None
        else:
            # Extract directory name and use as nav name
            relative_nav_path = re.sub(r"^%s" % self._root_content_path,
                                       '', self._content_path)
            self.name = os.path.split(relative_nav_path)[-1]

        # Build the nav level
        self._scan()

    @property
    def has_children(self):
        return len(self.child_navs) > 0 or \
               len(self.child_pages) > 0

    @property
    def children(self):
        return self.child_navs + self.child_pages

    def _scan(self):
        # Get a list of files in content_directory
        directory_files = os.listdir(self._content_path)

        # Traverse through all files
        for filename in directory_files:
            if filename in self.skip_files:
                continue

            filepath = os.path.join(self._content_path, filename)

            # Check if it's a normal file or directory
            if os.path.isfile(filepath):
                page_name = os.path.splitext(os.path.basename(filepath))[0]

                # Only allow index at the top level
                # Allowing pages other than index at the top leads to
                # a confusing navigation structure.
                if self.level == 0 and 'index' != page_name:
                    raise ContentStructureException(
                            "Only index allowed in top level navigation,"
                            " found %s" % page_name)

                # Check if the file has an extension allowable for nav
                for extension in self.extensions:
                    # Not a content file, ignore
                    if not filepath.endswith(extension):
                        continue

                    # We have got a nav file!
                    page = Page(self._root_content_path, filepath)

                    # If it's an index file use it for the page for this nav
                    # object
                    if 'index' == page_name:
                        self.page = page
                        self.has_page = True
                    else:
                        self.child_pages.append(page)

            elif os.path.isdir(filepath):
                # We got a directory, create a new nav level
                self.child_navs.append(Navigation(filepath, self.level + 1))

    def get_page_dict(self, nav=None):
        """Return a flattened dictionary of pages."""
        pages = {}

        # If no nav is given start at self (top level)
        if nav is None:
            nav = self

        if nav.page is not None:
            pages[nav.page.url_path] = nav.page

        for page in nav.child_pages:
            pages[page.url_path] = page

        for child_nav in nav.child_navs:
            p = self.get_page_dict(nav=child_nav)
            pages.update(p)

        return pages

    def print_debug_nav(self, nav=None, level=0, out=sys.stdout):
        """Print the navigation structure for debugging.

        :param nav: Navigation object to print
        :param level: Nav level of the
        """
        indentation_inc = 2
        navigation_level = 0 if nav is None else nav.level
        nav_indentation = ' ' * navigation_level
        page_indentation = ' ' * (navigation_level + indentation_inc)

        # If no nav is given start at self (top level)
        if nav is None:
            nav = self

            # Print header
            out.write("+-Navigation Structure----------------------------+")
            out.write("|   N  = Navigtion Level                          |")
            out.write("|          [*:9]] = [has_page:nav_level]          |")
            out.write("|   P = Page                                      |")
            out.write("+-------------------------------------------------+")

        hp = nav.has_page
        out.write('%sN[%s:%s] %s (%s) {%s}' % (nav_indentation, '*' if hp else '-',
                                               navigation_level, nav.name,
                                               nav._content_path,
                                               nav.page.url_path if hp else '-'))

        for page in nav.child_pages:
            out.write('%sP %s' % (page_indentation,
                                  os.path.basename(page.page_path)))

        for child_nav in nav.child_navs:
            self.print_debug_nav(child_nav, navigation_level + indentation_inc)