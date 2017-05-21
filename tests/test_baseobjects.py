"""Tests for the MDWeb Base Objects."""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
import unittest
from mdweb.BaseObjects import MetaInfParser
from mdweb.Exceptions import PageMetaInfFieldException
from mdweb.Navigation import Navigation
from mdweb.Page import Page, load_page


class TesNavigationBaseItem(fake_filesystem_unittest.TestCase):

    """MDSite Navigation Base tests."""

    def setUp(self):
        """Create fake filesystem."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

    def test_navigation_type(self):
        """A directory should have navigation type 'Navigation'."""
        self.fs.CreateFile('/my/content/index.md')
        nav = Navigation('/my/content')

        self.assertEqual(nav.nav_type, "Navigation")

    def test_page_type(self):
        """A file in a directory should have navigation type 'Page'."""
        file_string = u""
        self.fs.CreateFile('/my/content/index.md',
                           contents=file_string)

        page = Page(*load_page('/my/content', '/my/content/index.md'))

        self.assertEqual(page.nav_type, "Page")


class TestMetaInfParser(unittest.TestCase):

    """Index object tests."""

    class MockMetaInf(MetaInfParser):  # pylint: disable=R0903

        """MDWeb Navigation Meta Information."""

        FIELD_TYPES = {
            'nav_name': ('unicode', None),
            'order': ('int', 0),
        }

    def test_blank_value(self):
        """A blank value in a meta-inf definition should raise exception."""
        self.assertRaises(PageMetaInfFieldException,
                          self.MockMetaInf,
                          '''Nav Name: Documentation
Order: ''')
