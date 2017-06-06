"""MDWeb Page Objects."""
import codecs
import os
import re

import markdown

from mdweb.BaseObjects import NavigationBaseItem, MetaInfParser
from mdweb.Exceptions import (
    ContentException,
    PageParseException,
)

#: A regex to extract the url path from the file path
URL_PATH_REGEX = r'^%s(?P<path>[^\0]*?)(index)?(\.md)'

#: A regex for extracting meta information (and comments).
META_INF_REGEX = r'(/\*(?P<metainf>.*)\*/)?(?P<content>.*)'


class PageMetaInf(MetaInfParser):  # pylint: disable=R0903
    """MDWeb Page Meta Information."""

    def __init__(self, meta_string):
        """Content page meta-information.

        If a page defines a non-standard meta value it is blindly included.

        :param meta_string: Raw meta-inf content as a string
        """
        super(PageMetaInf, self).__init__(meta_string)
        self.nav_name = self.title if self.nav_name is None else self.nav_name


def load_page(content_path, page_path):
    """Load the page file and return the path, URL and contents"""

    # Extract the part of the page_path that will be used as the URL path
    pattern = URL_PATH_REGEX % content_path
    matches = re.match(pattern, page_path)
    if matches:
        url_path = matches.group('path').rstrip('/').lstrip('/')
    else:
        raise PageParseException("Unable to parse page path [%s]" %
                                 content_path)

    if not os.path.exists(page_path):
        raise ContentException('Could not find file for content page "%s"' %
                               page_path)

    # Read the page file
    with codecs.open(page_path, 'r', encoding='utf8') as f:
        file_string = f.read()

    return page_path, url_path, file_string


class Page(NavigationBaseItem):
    """MDWeb Page View."""

    def __init__(self, page_path, url_path, file_string):
        """Initialize Page object."""

        self.page_path = page_path
        self.url_path = url_path

        # Separate the meta information and the page content
        meta_inf_regex = re.compile(META_INF_REGEX, flags=re.DOTALL)
        match = meta_inf_regex.search(file_string)
        meta_inf_string = match.group('metainf') if match.group('metainf') \
            else ''
        content_string = match.group('content')

        self.meta_inf = PageMetaInf(meta_inf_string)

        # Strip the meta information and comments
        self.markdown_str = content_string

        # The page will be rendered on first view
        self.page_html = self.parse_markdown(self.markdown_str)

        self.abstract = self.page_html[0:100]
        
    @property
    def is_published(self):
        return self.meta_inf.published

    @staticmethod
    def parse_markdown(page_markdown):
        """Parse given markdown string into rendered html.

        :param page_markdown: Markdown to be parsed
        :return: Rendered page HTML
        """
        page_html = markdown.markdown(page_markdown)

        return page_html

    def __repr__(self):
        return '{0}'.format(self.page_path)
