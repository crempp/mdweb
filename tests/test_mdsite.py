"""Tests for the MDWeb Site."""
from pyfakefs import fake_filesystem_unittest, fake_filesystem

from flask.ext.testing import TestCase
try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock
    
from mdweb.Page import Page
from mdweb.MDSite import MDSite
from tests.sites import (MDTestSite, MDFakeFSTestSite,
                         MDFakeFSNoThemeTestSite, MDFakeFSNoContentTestSite,
                         populate_fakefs)

# Shim Python 3.x Exceptions
if 'FileExistsError' not in __builtins__.keys():
    from mdweb.Exceptions import FileExistsError  # pylint: disable=W0622

        
class TestSite(fake_filesystem_unittest.TestCase, TestCase):

    """MDSite object tests."""

    def create_app(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        populate_fakefs(self)
        
        app = MDFakeFSTestSite(
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
        with self.app.test_client() as client:
            response = client.get('/contentassets/logo.png')

        self.assert200(response)

    def test_missing_content_asset(self):
        """Missing content assets should be returned with a 404 status."""
        with self.app.test_client() as client:
            response = client.get('/contentassets/missing_logo.png')
        self.assert404(response)

    def test_page_lookup(self):
        """Page lookup should return the correct page based on URL path."""
        page = self.app.get_page('')
        self.assertEqual(page.page_path, '/my/content/index.md')

        page = self.app.get_page('about')
        self.assertEqual(page.page_path, '/my/content/about/index.md')

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


class TestSiteBoot(fake_filesystem_unittest.TestCase):

    """MDSite object tests."""

    def setUp(self):
        """Create fake filesystem and flask app."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        populate_fakefs(self)

    @mock.patch('mdweb.MDSite.MDSite._stage_pre_boot')
    def test_stage_pre_boot(self, mock_stage_pre_boot):
        """Pre-boot stage should run."""
        app = MDFakeFSTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        self.assertTrue(mock_stage_pre_boot.called)

    @mock.patch('mdweb.MDSite.MDSite._stage_create_app')
    def test_stage_create_app(self, mock_stage_create_app):
        """Create app stage should run."""
        app = MDFakeFSTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        self.assertTrue(mock_stage_create_app.called)

    @mock.patch('mdweb.MDSite.MDSite._stage_post_boot')
    def test_stage_post_boot(self, mock_stage_post_boot):
        """Post-boot stage should run."""
        app = MDFakeFSTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        self.assertTrue(mock_stage_post_boot.called)


class TestSiteMissingTemplate(fake_filesystem_unittest.TestCase):

    """MDSite missing template directory tests."""

    def setUp(self):
        """Create fake filesystem."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        populate_fakefs(self)

    def test_no_theme_directory(self):
        """Missing theme directory should raise FileExistsError."""
        self.assertRaises(FileExistsError, MDFakeFSNoThemeTestSite, "MDWeb")


class TestSiteMissingContent(fake_filesystem_unittest.TestCase):

    """MDSite missing content directory tests."""

    def setUp(self):
        """Create fake filesystem."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

        populate_fakefs(self)

    def test_no_content_directory(self):
        """Missing content directory should raise FileExistsError."""
        self.assertRaises(FileExistsError, MDFakeFSNoContentTestSite, "MDWeb")


class TestPartials(TestCase):
    
    """Can't use pyfakefs for this or partials won't load"""
    
    def create_app(self):
        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()
        
        return app

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


class TestSortFilter(unittest.TestCase):
    # date sort
    # reverse
    # order
    # title
    # page count
    def setUp(self):
        self.page_list = []
        self.page_list.append(Page('/path/to/story3.md', '/to/story3', u"""/*
Title: Blog Story 3
Date: 2016/05/12
Nav Name: Story 3
Order: 3
*/
"""))
        self.page_list.append(Page('/path/to/other-page.md', '/to/other-page',
                                   u"""/*
Title: Other Story
Date: 2016/04/02
Nav Name: Another Story
Order: 2
*/
"""))
        self.page_list.append(Page('/path/to/story2.md', '/to/story2', u"""/*
Title: blog story 2
Date: 2016/03/21
Nav Name: Story 1
Order: 2
*/
"""))
        self.page_list.append(Page('/path/to/story1.md', '/to/story1', u"""/*
Title: Blog Story 1
Date: 2016/02/01
Nav Name: Story 1
Order: 1
*/
"""))

    def test_sort_title(self):
        sorted_list = MDSite._sorted_pages(self.page_list, 'title', 6, False)
        
        self.assertEqual(sorted_list[0].meta_inf.title, 'Blog Story 1')
        self.assertEqual(sorted_list[1].meta_inf.title, 'blog story 2')
        self.assertEqual(sorted_list[2].meta_inf.title, 'Blog Story 3')
        self.assertEqual(sorted_list[3].meta_inf.title, 'Other Story')

    def test_sort_title_reversed(self):
        sorted_list = MDSite._sorted_pages(self.page_list, 'title', 6, True)

        self.assertEqual(sorted_list[0].meta_inf.title, 'Other Story')
        self.assertEqual(sorted_list[1].meta_inf.title, 'Blog Story 3')
        self.assertEqual(sorted_list[2].meta_inf.title, 'blog story 2')
        self.assertEqual(sorted_list[3].meta_inf.title, 'Blog Story 1')
        
    def test_sort_date(self):
        sorted_list = MDSite._sorted_pages(self.page_list, 'date', 6, False)

        self.assertEqual(sorted_list[0].meta_inf.title, 'Blog Story 1')
        self.assertEqual(sorted_list[1].meta_inf.title, 'blog story 2')
        self.assertEqual(sorted_list[2].meta_inf.title, 'Other Story')
        self.assertEqual(sorted_list[3].meta_inf.title, 'Blog Story 3')
    
    def test_sort_date_reversed(self):
        sorted_list = MDSite._sorted_pages(self.page_list, 'date', 6, True)

        self.assertEqual(sorted_list[0].meta_inf.title, 'Blog Story 3')
        self.assertEqual(sorted_list[1].meta_inf.title, 'Other Story')
        self.assertEqual(sorted_list[2].meta_inf.title, 'blog story 2')
        self.assertEqual(sorted_list[3].meta_inf.title, 'Blog Story 1')
        
    def test_sort_order(self):
        sorted_list = MDSite._sorted_pages(self.page_list, 'order', 6, False)

        self.assertEqual(sorted_list[0].meta_inf.title, 'Blog Story 1')
        self.assertEqual(sorted_list[1].meta_inf.title, 'Other Story')
        self.assertEqual(sorted_list[2].meta_inf.title, 'blog story 2')
        self.assertEqual(sorted_list[3].meta_inf.title, 'Blog Story 3')

    def test_sort_order_reversed(self):
        sorted_list = MDSite._sorted_pages(self.page_list, 'order', 6, True)

        self.assertEqual(sorted_list[0].meta_inf.title, 'Blog Story 3')
        self.assertEqual(sorted_list[1].meta_inf.title, 'Other Story')
        self.assertEqual(sorted_list[2].meta_inf.title, 'blog story 2')
        self.assertEqual(sorted_list[3].meta_inf.title, 'Blog Story 1')
    
    def test_page_count(self):
        sorted_list = MDSite._sorted_pages(self.page_list, 'title', 2, False)

        self.assertEqual(sorted_list[0].meta_inf.title, 'Blog Story 1')
        self.assertEqual(sorted_list[1].meta_inf.title, 'blog story 2')
        self.assertEqual(len(sorted_list), 2)


class TestCurrentPageContext(TestCase):
    """Can't use pyfakefs for this or partials won't load"""
    
    def create_app(self):
        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()
        
        return app
    
    def test_index_in_context(self):
        """"Current page should exist in context."""
        path = '/'
        with self.app.test_client() as client:
            client.get(path)
        self.assertContext('current_page', self.app.get_page(path))

    def test_no_such_page(self):
        """"Even a non-existent page (None) should inject"""
        path = '/no/such/page'
        with self.app.test_client() as client:
            client.get(path)
        self.assertContext('current_page', self.app.get_page(path))

    def test_blah_in_context(self):
        """"Current page should exist in context."""
        path = '/about/history'
        with self.app.test_client() as client:
            client.get(path)
        self.assertContext('current_page', self.app.get_page(path))
