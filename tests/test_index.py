"""
Tests for the MDWeb Index

"""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from mdweb.MDSite import MDSite


class MDTestSite(MDSite):

    """Site to use for testing."""

    class MDConfig:

        """Config for testing use."""

        DEBUG = False
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True


class TestIndex(fake_filesystem_unittest.TestCase):

    """Index object tests."""

    def setUp(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/content/robots.txt')
        self.fs.CreateFile('/my/content/humans.txt')
        self.fs.CreateFile('/my/content/favicon.ico')
        self.fs.CreateFile('/my/content/crossdomain.xml')

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

    def test_basic_request(self):
        """Request to "/" should return 200."""
        with self.app.test_client() as client:
            result = client.get('/')

        self.assertEqual(result.status_code, 200)

    def test_404_request(self):
        """Request to "/nowhere" should return 404."""
        with self.app.test_client() as client:
            result = client.get('/nowhere')

        self.assertEqual(result.status_code, 404)

    def test_root_level_asset(self):
        """Special root-level assets should be returned properly."""
        with self.app.test_client() as client:
            result = client.get('/robots.txt')
            self.assertEqual(result.status_code, 200)

            result = client.get('/humans.txt')
            self.assertEqual(result.status_code, 200)

            result = client.get('/favicon.ico')
            self.assertEqual(result.status_code, 200)

            result = client.get('/crossdomain.xml')
            self.assertEqual(result.status_code, 200)
