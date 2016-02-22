"""
Tests for the MDWeb Site
"""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock

from mdweb.Navigation import Navigation
from mdweb.Page import Page


class TestSite(fake_filesystem_unittest.TestCase):
    """MDSite object tests """

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
