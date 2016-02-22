"""
Tests for the MDWeb Site
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


class TestSite(fake_filesystem_unittest.TestCase):
    """MDSite object tests """

    def setUp(self):
        """Create fake filesystem and flask app"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md')
        self.fs.CreateFile('/my/content/contact/index.md')

        self.fs.CreateFile('/my/theme/assets/css/style.css')
        self.fs.CreateFile('/my/theme/assets/js/site.js')
        self.fs.CreateFile('/my/theme/templates/layout.html')
        self.fs.CreateFile('/my/theme/templates/navigation.html')
        self.fs.CreateFile('/my/theme/templates/page.html')
        self.fs.CreateFile('/my/theme/templates/page_home.html')

    def tearDown(self):
        pass

    def test_site_created(self):
        """Site should initalize properly."""
        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        self.assertEqual(app.site_name, 'MDWeb')
        self.assertEqual(app._static_folder, '/my/theme/assets')
        self.assertIsNotNone(app.navigation)
        self.assertGreater(len(app.pages), 0)

    @unittest.skip("Test not implemented")
    def test_no_theme_directory(self):
        """Missing theme directory should raise FileExistsError."""
        pass

    @unittest.skip("Test not implemented")
    def test_no_content_directory(self):
        """Missing content directory should raise FileExistsError."""
        pass

    @unittest.skip("Test not implemented")
    def test_page_lookup(self):
        """Page lookup should return the correct page based on URL path."""
        pass

    @unittest.skip("Test not implemented")
    def test_error_page(self):
        """Error should return status 404 and content from 404 template."""
        pass

    @unittest.skip("Test not implemented")
    def test_template_observer(self):
        """Changes to template files should restart application."""
        pass

    @unittest.skip("Test not implemented")
    def test_content_observer(self):
        """Changes to content files should restart application."""
        pass

    @unittest.skip("Test not implemented")
    def test_stage_pre_boot(self):
        """Pre-boot stage should run."""
        pass

    @unittest.skip("Test not implemented")
    def test_stage_create_app(self):
        """Create app stage should run."""
        pass

    @unittest.skip("Test not implemented")
    def test_stage_load_config(self):
        """Load config stage should run."""
        pass

    @unittest.skip("Test not implemented")
    def test_stage_post_boot(self):
        """Post-boot stage should run."""
        pass

    @unittest.skip("Test not implemented")
    def test_navigation_context(self):
        """Navigation should be added to context."""
        pass

