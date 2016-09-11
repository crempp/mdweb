"""Tests for the MDWeb Site."""
from dateutil import parser
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from flask.ext.testing import TestCase
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock

from mdweb.MDSite import MDSite

# Shim Python 3.x Exceptions
if 'FileExistsError' not in __builtins__.keys():
    from mdweb.Exceptions import FileExistsError  # pylint: disable=W0622


class MDTestSite(MDSite):

    """Site to use for testing."""

    class MDConfig:  # pylint: disable=R0903

        """Config class for testing."""

        DEBUG = False
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True
        GA_TRACKING_ID = 'UA-00000000-1'


class TestSite(fake_filesystem_unittest.TestCase, TestCase):

    """MDSite object tests."""

    def create_app(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        file_string = u"""/*
Title: MDWeb
Description: The minimalistic markdown NaCMS
Date: February 1st, 2016
Sitemap Priority: 0.9
Sitemap ChangeFreq: daily
*/
"""

        self.fs.CreateFile('/my/content/400.md')
        self.fs.CreateFile('/my/content/403.md')
        self.fs.CreateFile('/my/content/404.md')
        self.fs.CreateFile('/my/content/500.md')
        self.fs.CreateFile('/my/content/index.md',
                           contents=file_string).SetMTime(
            parser.parse('Thu, 28 Jun 2015 14:17:15 +0000')
        )
        self.fs.CreateFile('/my/content/about/index.md').SetMTime(
            parser.parse('Wed, 27 Jun 2015 13:12:15 +0000')
        )
        self.fs.CreateFile('/my/content/contact/index.md').SetMTime(
            parser.parse('Tue, 26 Jun 2015 12:06:15 +0000')
        )
        self.fs.CreateFile('/my/content/assets/logo.png')

        self.fs.CreateFile('/my/theme/assets/css/style.css')
        self.fs.CreateFile('/my/theme/assets/js/site.js')
        self.fs.CreateFile('/my/theme/templates/layout.html')
        self.fs.CreateFile('/my/theme/templates/navigation.html')
        self.fs.CreateFile('/my/theme/templates/page.html')
        self.fs.CreateFile('/my/theme/templates/page_home.html')

        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        return app

    def test_site_created(self):
        """Site should initalize properly."""
        self.assertEqual(self.app.site_name, 'MDWeb')
        # pylint: disable=W0212
        self.assertEqual(self.app._static_folder, '/my/theme/assets')
        self.assertIsNotNone(self.app.navigation)
        self.assertGreater(len(self.app.pages), 0)

    def test_existing_content_asset(self):
        """Content assets should be returned with a 200 status."""
        response = self.client.get('/contentassets/logo.png')

        self.assert200(response)

    def test_missing_content_asset(self):
        """Missing content assets should be returned with a 404 status."""
        response = self.client.get('/contentassets/missing_logo.png')

        self.assert404(response)

    def test_page_lookup(self):
        """Page lookup should return the correct page based on URL path."""
        page = self.app.get_page('')
        self.assertEqual(page.page_path, '/my/content/index.md')

        page = self.app.get_page('about')
        self.assertEqual(page.page_path, '/my/content/about/index.md')

    def test_error_page(self):
        """Error should return status 404 and content from 404 template."""
        response = self.client.get('/non/existent/page')

        # TODO: Test that the 404 template was used
        # self.assert_template_used('404.html')

        self.assert404(response)

    # @unittest.skip("Test not implemented")
    # def test_template_observer(self):
    #     """Changes to template files should restart application."""
    #     pass

    # @unittest.skip("Test not implemented")
    # def test_content_observer(self):
    #     """Changes to content files should restart application."""
    #     pass

    def test_navigation_context(self):
        """Navigation should be added to context."""
        with self.app.test_client() as client:
            client.get('/about')
            self.assertContext('navigation', self.app.navigation)

    def test_sitemap_xml(self):
        """Sitemap XML should be generated correctly."""
        with self.app.test_client() as client:
            response = client.get('/sitemap.xml')

        self.assert200(response)
        # pylint: disable=C0301
        # pylint: disable=E501
        self.assertEqual(response.data, b"""<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <url>
        <loc>http://localhost/</loc>
        <lastmod>2015-06-28T14:17:15+0000</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url><url>
        <loc>http://localhost/about</loc>
        <lastmod>2015-06-27T13:12:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/contact</loc>
        <lastmod>2015-06-26T12:06:15+0000</lastmod>
    </url>
</urlset>""")
        
    def test_ga_tracking_context(self):
        """GA Tracking should be added to context."""
        with self.app.test_client() as client:
            client.get('/')
        self.assertContext('ga_tracking', '''<script>
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
    
    ga('create', 'UA-00000000-1', 'auto');
    ga('send', 'pageview');
</script>''')
        

class TestSiteBoot(fake_filesystem_unittest.TestCase):

    """MDSite object tests."""

    def setUp(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/content/400.md')
        self.fs.CreateFile('/my/content/403.md')
        self.fs.CreateFile('/my/content/404.md')
        self.fs.CreateFile('/my/content/500.md')
        self.fs.CreateFile('/my/content/robots.txt')
        self.fs.CreateFile('/my/content/humans.txt')
        self.fs.CreateFile('/my/content/favicon.ico')
        self.fs.CreateFile('/my/content/crossdomain.xml')
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md')
        self.fs.CreateFile('/my/content/contact/index.md')
        self.fs.CreateFile('/my/content/assets/logo.png')

        self.fs.CreateFile('/my/theme/assets/css/style.css')
        self.fs.CreateFile('/my/theme/assets/js/site.js')
        self.fs.CreateFile('/my/theme/templates/layout.html')
        self.fs.CreateFile('/my/theme/templates/navigation.html')
        self.fs.CreateFile('/my/theme/templates/page.html')
        self.fs.CreateFile('/my/theme/templates/page_home.html')

    @mock.patch('mdweb.MDSite.MDSite._stage_pre_boot')
    def test_stage_pre_boot(self, mock_stage_pre_boot):
        """Pre-boot stage should run."""
        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        self.assertTrue(mock_stage_pre_boot.called)

    @mock.patch('mdweb.MDSite.MDSite._stage_create_app')
    def test_stage_create_app(self, mock_stage_create_app):
        """Create app stage should run."""
        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        self.assertTrue(mock_stage_create_app.called)

    @mock.patch('mdweb.MDSite.MDSite._stage_post_boot')
    def test_stage_post_boot(self, mock_stage_post_boot):
        """Post-boot stage should run."""
        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        self.assertTrue(mock_stage_post_boot.called)


class TestSiteMissingTemplate(fake_filesystem_unittest.TestCase):

    """MDSite object tests."""

    def setUp(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/content/index.md')

    def test_no_theme_directory(self):
        """Missing theme directory should raise FileExistsError."""
        self.assertRaises(FileExistsError, MDTestSite, "MDWeb")


class TestSiteMissingContent(fake_filesystem_unittest.TestCase):

    """MDSite object tests."""

    def setUp(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/theme/assets/css/style.css')
        self.fs.CreateFile('/my/theme/assets/js/site.js')
        self.fs.CreateFile('/my/theme/templates/layout.html')
        self.fs.CreateFile('/my/theme/templates/navigation.html')
        self.fs.CreateFile('/my/theme/templates/page.html')
        self.fs.CreateFile('/my/theme/templates/page_home.html')

    def test_no_content_directory(self):
        """Missing content directory should raise FileExistsError."""
        self.assertRaises(FileExistsError, MDTestSite, "MDWeb")
