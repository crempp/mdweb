"""
Tests for the MDWeb Site
"""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from flask.ext.testing import TestCase
import unittest
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock

from mdweb.MDSite import MDSite

# Shim Python 3.x Exceptions
if 'FileExistsError' not in __builtins__.keys():
    from mdweb.Exceptions import FileExistsError


class MDTestSite(MDSite):
    """Site to use for testing"""
    class MDConfig:
        DEBUG = False
        SECRET_KEY = '\x85\xa2\x1c\xfd\x07MF\xcb_ ]\x1e\x9e\xab\xa2qn\xd1\x82\xcb^\x11x\xc5'
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True

    pass


class TestSite(fake_filesystem_unittest.TestCase, TestCase):
    """MDSite object tests """

    def create_app(self):
        """Create fake filesystem and flask app"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/content/400.md')
        self.fs.CreateFile('/my/content/403.md')
        self.fs.CreateFile('/my/content/404.md')
        self.fs.CreateFile('/my/content/500.md')
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

        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_site_created(self):
        """Site should initalize properly."""
        self.assertEqual(self.app.site_name, 'MDWeb')
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
        p = self.app.get_page('')
        self.assertEqual(p.page_path, '/my/content/index.md')

        p = self.app.get_page('about')
        self.assertEqual(p.page_path, '/my/content/about/index.md')

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
        with self.app.test_client() as c:
            result = c.get('/about')
            self.assertContext('navigation', self.app.navigation)


class TestSiteBoot(fake_filesystem_unittest.TestCase):
    """MDSite object tests """

    def setUp(self):
        """Create fake filesystem and flask app"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

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

    # @mock.patch('mdweb.MDSite.MDSite._stage_load_config')
    # def test_stage_load_config(self, mock_stage_load_config):
    #     """Load config stage should run."""
    #     app = MDTestSite(
    #         "MDWeb",
    #         app_options={}
    #     )
    #     app.start()
    #
    #     self.assertTrue(mock_stage_load_config.called)

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
    """MDSite object tests """

    def setUp(self):
        """Create fake filesystem and flask app"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/content/index.md')

    def test_no_theme_directory(self):
        """Missing theme directory should raise FileExistsError."""
        self.assertRaises(FileExistsError, MDTestSite, "MDWeb")


class TestSiteMissingContent(fake_filesystem_unittest.TestCase):
    """MDSite object tests """

    def setUp(self):
        """Create fake filesystem and flask app"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/theme/assets/css/style.css')
        self.fs.CreateFile('/my/theme/assets/js/site.js')
        self.fs.CreateFile('/my/theme/templates/layout.html')
        self.fs.CreateFile('/my/theme/templates/navigation.html')
        self.fs.CreateFile('/my/theme/templates/page.html')
        self.fs.CreateFile('/my/theme/templates/page_home.html')

    def test_no_content_directory(self):
        """Missing content directory should raise FileExistsError."""
        self.assertRaises(FileExistsError, MDTestSite, "MDWeb")
