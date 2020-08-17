"""
Tests for the MDWeb Index

"""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from flask_testing import TestCase
from mdweb.MDSite import MDSite


class MDTestSite(MDSite):
    """Site to use for testing."""

    class MDConfig:  # pylint: disable=R0903
        """Config for testing use."""

        DEBUG = False
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True


class TestIndex(fake_filesystem_unittest.TestCase, TestCase):
    """Index object tests."""

    def create_app(self):
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
        self.fs.CreateFile('/my/theme/templates/layout.html',
                           contents="""<html><body>
{% block body %}{% endblock %}
</body></html>""")
        self.fs.CreateFile('/my/theme/templates/navigation.html')
        self.fs.CreateFile('/my/theme/templates/page.html',
                           contents="""{% extends "layout.html" %}
{% block body %}{{ page | safe}}{% endblock %}""")
        self.fs.CreateFile('/my/theme/templates/page_home.html')

        self.fs.CreateFile('/my/content/404.md', contents='''404 Test''')
        self.fs.CreateFile('/my/content/500.md', contents='''500 Test''')

        app = MDTestSite(
            "MDWeb",
            app_options={},
            site_options={
                'logging_level': 'CRITICAL',
                'testing': True,
            }
        )
        app.start()

        return app

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

    def test_404_custom_renders(self):
        """Custom 4XX should render on those status.'"""
        with self.app.test_client() as client:
            result = client.get('/nowhere')
            self.assertEqual(result.status_code, 404)
            self.assertEqual(result.data,
                             b'<html><body>\n<p>404 Test</p>\n</body></html>')
    
    def test_500_custom_renders(self):
        """Custom 5XX should render on those status.'"""
        with self.app.test_client() as client:
            result = client.get('/boom')
            self.assertEqual(result.status_code, 500)
            self.assertEqual(result.data,
                             b'<html><body>\n<p>500 Test</p>\n</body></html>')

    def test_4xx_non_custom_renders(self):
        """4XX without custom files should render with default message.'"""
        with self.app.test_client() as client:
            result = client.put('/')
            self.assertEqual(result.status_code, 405)
            self.assertEqual(
                result.data,
                b'The method is not allowed for the requested URL.')
