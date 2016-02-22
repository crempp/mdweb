"""
Tests for the MDWeb Index

"""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
import unittest
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock

from mdweb.MDSite import MDSite


class MDTestSite(MDSite):
    """Site to use for testing"""
    class MDConfig:
        DEBUG = False
        SECRET_KEY = '\x85\xa2\x1c\xfd\x07MF\xcb_ ]\x1e\x9e\xab\xa2qn\xd1\x82\xcb^\x11x\xc5'
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True

    pass


class TestIndex(fake_filesystem_unittest.TestCase):
    """Index object tests """

    def setUp(self):
        """Create fake filesystem and flask app"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md')
        self.fs.CreateFile('/my/content/contact/index.md')

        self.fs.CreateFile('/my/theme/assets/robots.txt')
        self.fs.CreateFile('/my/theme/assets/css/style.css')
        self.fs.CreateFile('/my/theme/assets/js/site.js')
        self.fs.CreateFile('/my/theme/templates/layout.html')
        self.fs.CreateFile('/my/theme/templates/navigation.html')
        self.fs.CreateFile('/my/theme/templates/page.html')
        self.fs.CreateFile('/my/theme/templates/page_home.html')

        self.app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        self.app.start()

    def tearDown(self):
        pass

    def test_basic_request(self):
        """Request to "/" should return 200."""
        with self.app.test_client() as c:
            result = c.get('/')

        self.assertEqual(result.status_code, 200)

    def test_404_request(self):
        """Request to "/nowhere" should return 404."""
        with self.app.test_client() as c:
            result = c.get('/nowhere')

        self.assertEqual(result.status_code, 404)

    @unittest.skip("Test not implemented")
    def test_root_level_asset(self):
        """Special root-level assets should be returned properly."""
        with self.app.test_client() as c:
            result = c.get('/robots.txt')

        self.assertEqual(result.status_code, 200)
