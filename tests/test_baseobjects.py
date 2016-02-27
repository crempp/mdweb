"""
Tests for the MDWeb Base Objects
"""
import unittest
from pyfakefs import fake_filesystem_unittest, fake_filesystem
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock

from mdweb.BaseObjects import MetaInfParser
from mdweb.Exceptions import PageMetaInfFieldException
from mdweb.Navigation import Navigation
from mdweb.Page import Page


class TesNavigationBaseItem(fake_filesystem_unittest.TestCase):
    """MDSite Navigation Base tests """

    def setUp(self):
        """Create fake filesystem"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

    def tearDown(self):
        pass

    def test_navigation_type(self):
        self.fs.CreateFile('/my/content/index.md')
        nav = Navigation('/my/content')

        self.assertEqual(nav.nav_type, "Navigation")

    def test_page_type(self):
        file_string = u""
        self.fs.CreateFile('/my/content/index.md',
                           contents=file_string)

        p = Page('/my/content', '/my/content/index.md')

        self.assertEqual(p.nav_type, "Page")


class TestMetaInfParserx(unittest.TestCase):
    """Index object tests """

    class MockMetaInf(MetaInfParser):
        """MDWeb Navigation Meta Information"""

        FIELD_TYPES = {
            'nav_name': ('unicode', None),
            'order': ('int', 0),
        }

    def test_blank_value(self):
        self.assertRaises(PageMetaInfFieldException,
                          self.MockMetaInf,
                          '''Nav Name: Documentation
Order: ''')
