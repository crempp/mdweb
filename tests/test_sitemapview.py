"""Tests for the MDWeb Sitemap View.

TODO: Test that the sitemap cache is regenerated when a file changes
"""
from dateutil import parser
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from flask.ext.testing import TestCase

from mdweb.MDSite import MDSite
from mdweb.SiteMapView import SiteMapView


class MDTestSite(MDSite):

    """Site to use for testing."""

    class MDConfig:  # pylint: disable=R0903

        """Config class for testing."""

        DEBUG = False
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True


class TestSiteMapView(fake_filesystem_unittest.TestCase, TestCase):

    """Navigation object tests."""

    def create_app(self):
        """Create fake filesystem."""
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
            parser.parse('Thu, 26 Jun 2015 11:21:15 +0000')
        )
        self.fs.CreateFile('/my/content/about/index.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 12:21:15 +0000')
        )
        self.fs.CreateFile('/my/content/contact/index.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 13:22:15 +0000')
        )
        self.fs.CreateFile('/my/content/contact/westcoast.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 14:23:15 +0000')
        )
        self.fs.CreateFile('/my/content/contact/eastcoast.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 15:24:15 +0000')
        )
        self.fs.CreateFile('/my/content/work/portfolio/index.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 16:25:15 +0000')
        )
        self.fs.CreateFile('/my/content/work/portfolio/landscapes.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 17:26:15 +0000')
        )
        self.fs.CreateFile('/my/content/work/portfolio/portraits.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 18:27:15 +0000')
        )
        self.fs.CreateFile('/my/content/work/portfolio/nature.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 19:28:15 +0000')
        )
        self.fs.CreateFile('/my/content/order/digitalprints.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 20:28:15 +0000')
        )
        self.fs.CreateFile('/my/content/order/framed.md').SetMTime(
            parser.parse('Thu, 26 Jun 2015 21:28:15 +0000')
        )
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

    def test_sitemap_generation(self):
        """Generated sitemap should match pages in the filesystem."""
        sitemap = SiteMapView.generate_sitemap()

        # pylint: disable=C0301
        self.assertEqual(sitemap, '''<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <url>
        <loc>http://localhost/</loc>
        <lastmod>2015-06-26T11:21:15+0000</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url><url>
        <loc>http://localhost/about</loc>
        <lastmod>2015-06-26T12:21:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/contact</loc>
        <lastmod>2015-06-26T13:22:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/contact/eastcoast</loc>
        <lastmod>2015-06-26T15:24:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/contact/westcoast</loc>
        <lastmod>2015-06-26T14:23:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/order/digitalprints</loc>
        <lastmod>2015-06-26T20:28:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/order/framed</loc>
        <lastmod>2015-06-26T21:28:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/work/portfolio</loc>
        <lastmod>2015-06-26T16:25:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/work/portfolio/landscapes</loc>
        <lastmod>2015-06-26T17:26:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/work/portfolio/nature</loc>
        <lastmod>2015-06-26T19:28:15+0000</lastmod>
    </url><url>
        <loc>http://localhost/work/portfolio/portraits</loc>
        <lastmod>2015-06-26T18:27:15+0000</lastmod>
    </url>
</urlset>''')
