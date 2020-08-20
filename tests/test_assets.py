"""
Tests for the MDWeb Index

"""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from mdweb.MDSite import MDSite


class MDTestSite(MDSite):
    """Site to use for testing."""

    class MDConfig:  # pylint: disable=R0903
        """Config for testing use."""

        DEBUG = False
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True


class TestAssets(fake_filesystem_unittest.TestCase):
    """Asset tests."""

    def setUp(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.create_file('/my/content/robots.txt')
        self.fs.create_file('/my/content/humans.txt')
        self.fs.create_file('/my/content/favicon.ico')
        self.fs.create_file('/my/content/crossdomain.xml')

        self.fs.create_file('/my/content/index.md')
        self.fs.create_file('/my/content/about/index.md')
        self.fs.create_file('/my/content/contact/index.md')
        self.fs.create_file('/my/content/assets/logo.png')

        self.fs.create_file('/my/theme/assets/robots.txt')
        self.fs.create_file('/my/theme/assets/css/style.css')
        self.fs.create_file('/my/theme/assets/js/site.js')
        self.fs.create_file('/my/theme/templates/layout.html')
        self.fs.create_file('/my/theme/templates/navigation.html')
        self.fs.create_file('/my/theme/templates/page.html')
        self.fs.create_file('/my/theme/templates/page_home.html')

        self.app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        self.app.start()

    def test_basic_asset_request(self):
        """Request to "/contentassets/logo.png" should return 200."""
        with self.app.test_client() as client:
            result = client.get('/contentassets/logo.png')

        self.assertEqual(result.status_code, 200)


class TestMissingAssets(fake_filesystem_unittest.TestCase):
    """Index object tests."""

    def setUp(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.create_file('/my/content/index.md')
        self.fs.create_file('/my/content/about/index.md')
        self.fs.create_file('/my/content/contact/index.md')
        self.fs.create_file('/my/content/assets/logo.png')

        self.fs.create_file('/my/theme/assets/robots.txt')
        self.fs.create_file('/my/theme/assets/css/style.css')
        self.fs.create_file('/my/theme/assets/js/site.js')
        self.fs.create_file('/my/theme/templates/layout.html')
        self.fs.create_file('/my/theme/templates/navigation.html')
        self.fs.create_file('/my/theme/templates/page.html')
        self.fs.create_file('/my/theme/templates/page_home.html')

        self.app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        self.app.start()

    def test_missing_asset(self):
        """Request to missing asset should return 404."""
        with self.app.test_client() as client:
            result = client.get('/contentassets/logo_small.png')

        self.assertEqual(result.status_code, 404)

    def test_missing_favicon(self):
        """Request to missing favicon should return 404.

        This is a regression test for
        https://github.com/crempp/mdweb/issues/28
        """
        with self.app.test_client() as client:
            result = client.get('/favicon.ico')

        self.assertEqual(result.status_code, 404)

    def test_missing_crossdomain(self):
        """Request to missing crossdomain.xml should return 404.

        This is a regression test for
        https://github.com/crempp/mdweb/issues/28
        """
        with self.app.test_client() as client:
            result = client.get('/crossdomain.xml')

        self.assertEqual(result.status_code, 404)

    def test_missing_humans_txt(self):
        """Request to missing humans.txt should return 404.

        This is a regression test for
        https://github.com/crempp/mdweb/issues/28
        """
        with self.app.test_client() as client:
            result = client.get('/humans.txt')

        self.assertEqual(result.status_code, 404)

    def test_missing_robots_txt(self):
        """Request to missing robots.txt should return 404.

        This is a regression test for
        https://github.com/crempp/mdweb/issues/28
        """
        with self.app.test_client() as client:
            result = client.get('/robots.txt')

        self.assertEqual(result.status_code, 404)
