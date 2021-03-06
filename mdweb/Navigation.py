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
        id: 'd5324c9d8797e07c58b139b50efc5cf0'
        slug: 'about'
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
    id: 'd5324c9d8797e07c58b139b50efc5cf0'
    slug: '_'
    has_children: True
    is_top: True
    level: 0
    name: None
    page: Page()
  )


Future Features:
    * Ordering navigation levels
"""
from collections import OrderedDict
import hashlib
import os
import re
from six import string_types

from mdweb.Exceptions import ContentException, ContentStructureException
from mdweb.Page import Page, load_page
from mdweb.BaseObjects import NavigationBaseItem, MetaInfParser


class NavigationMetaInf(MetaInfParser):   # pylint: disable=R0903
    """MDWeb Navigation Meta Information."""

    FIELD_TYPES = {
        'nav_name': ('unicode', None),
        'order': ('int', 0),
    }


class Navigation(NavigationBaseItem):
    """Navigation level representation.

    Navigation is built recursively by walking the content directory. Each
    directory represents a navigation level, each file represents a page.

    Each nav level's name is determined by the directory name.
    """

    #: MetaInf file name
    nav_metainf_file_name = '_navlevel.txt'

    #: Allowed extensions for content files
    extensions = ['.md']

    #: Special files to skip
    skip_files = [
        '400.md',
        '403.md',
        '404.md',
        '405.md',
        '500.md',
    ]

    skip_directories = [
        'assets',
    ]

    #: Root path to content
    _root_content_path = None

    def __init__(self, content_path, nav_level=0):
        """Initialize navigation level."""
        #: path to content for current navigation level
        self._content_path = os.path.abspath(content_path)

        #: Navigation level
        self.level = nav_level

        #: Navigation level name (populated during scan)
        if self.level == 0:
            Navigation._root_content_path = self._content_path
            self.name = None
        else:
            # Extract directory name and use as nav name
            relative_nav_path = re.sub(r"^%s" % self._root_content_path,
                                       '', self._content_path)
            self.name = os.path.split(relative_nav_path)[-1].lower()

        #: Relative path to navigation
        self.path = content_path.replace(self._root_content_path, '')

        #: Navigation level meta information
        self.meta_inf = None

        #: Ordered list of child Navigatyion objects
        self.child_navs = []

        #: Ordered list of child Page object
        self.child_pages = []

        #: Is this the top level of navigation
        self.is_top = nav_level == 0

        #: Navigation page if one is provided (populated during scan)
        self.page = None

        #: Does the nav level have an associated page?  (populated during scan)
        self.has_page = False

        #: Order in the navigation
        self.order = 0

        #: Navigation slug
        self.slug = self.path.replace('.md', '').strip('/') \
            .replace('/', '_').replace('.', '_') if self.path != '' else '_'

        #: Navigation ID
        self.id = hashlib.md5(self.slug.encode('utf-8')).hexdigest().lower()

        #: Navigation level published status
        self.published = True

        # Build the nav level
        self._scan()

        # Ensure a root index
        if 0 == self.level and (self.page is None or '' != self.page.url_path):
            raise ContentException("Missing root index.md")

    @property
    def has_children(self):
        """Check if the navigation level has any pages or nav children."""
        return len(self.child_navs) > 0 or \
            len(self.child_pages) > 0

    @property
    def children(self):
        """Return a list of the child_navs and child_pages."""
        return self.child_navs + self.child_pages

    @property
    def root_content_path(self):
        """Return the root_content_path."""
        return self._root_content_path

    @property
    def content_path(self):
        """Return the content_path."""
        return self._content_path
    
    @property
    def is_published(self):
        return self.published
    
    def get_child_by_name(self, name):
        """Find the child with the given name"""
        for child in self.child_navs:
            if child.name == name.lower():
                return child
        return None
    
    def get_child_by_id(self, id):
        """Find the child with the given ID"""
        for child in self.child_navs:
            if child.id == id.lower():
                return child
        return None

    def _scan(self):
        """Scan the root content path recursively for pages and navigation."""
        # Get a list of files in content_directory
        directory_files = os.listdir(self._content_path)

        if self.nav_metainf_file_name in directory_files:
            # We have a nav-level metainf file, parse it
            absolute_meta_inf_path = os.path.join(self._content_path,
                                                  self.nav_metainf_file_name)
            # Read the meta-inf file
            with open(absolute_meta_inf_path, 'r') as file:
                file_string = file.read()
            self.meta_inf = NavigationMetaInf(file_string)

            if hasattr(self.meta_inf, 'order'):
                self.order = self.meta_inf.order

            if hasattr(self.meta_inf, 'nav_name'):
                self.name = self.meta_inf.nav_name.lower() if \
                    self.meta_inf.nav_name is not None else None
                
            if hasattr(self.meta_inf, 'published'):
                if isinstance(self.meta_inf.published, string_types):
                    self.published = self.meta_inf.published.lower() == 'true'
                elif isinstance(self.meta_inf.published, bool):
                    self.published = self.meta_inf.published
                else:
                    self.published = True

        # Traverse through all files
        for file_name in directory_files:
            file_path = os.path.join(self._content_path, file_name)

            # Check if it's a normal file or directory
            if os.path.isfile(file_path):
                if file_name in self.skip_files:
                    continue

                page_name, ext = os.path.splitext(os.path.basename(file_path))
                if ext not in self.extensions:
                    continue

                # Only allow index at the top level
                # Allowing pages other than index at the top leads to
                # a confusing navigation structure.
                if self.level == 0 and 'index' != page_name:
                    raise ContentStructureException(
                        "Only index allowed in top level navigation, found %s"
                        % page_name)

                # We have got a nav file!
                page = Page(*load_page(self._root_content_path, file_path))

                # If it's an index file use it for the page for this nav  object
                if 'index' == page_name:
                    self.page = page
                    self.has_page = True
                else:
                    self.child_pages.append(page)

            elif os.path.isdir(file_path):
                if file_name in self.skip_directories:
                    continue

                # We got a directory, create a new nav level
                self.child_navs.append(Navigation(file_path, self.level + 1))

        # Now sort
        self.child_navs.sort(key=lambda x: x.order)
        self.child_pages.sort(key=lambda x: x.meta_inf.order)

    def get_page_dict(self, nav=None):
        """Return a flattened dictionary of pages."""
        pages = OrderedDict()

        # If no nav is given start at self (top level)
        if nav is None:
            nav = self

        if nav.page is not None:
            pages[nav.page.url_path] = nav.page

        for page in nav.child_pages:
            pages[page.url_path] = page

        for child_nav in nav.child_navs:
            page = self.get_page_dict(nav=child_nav)
            pages.update(page)

        return pages

    def __repr__(self):
        return '{0}'.format(self.path)
