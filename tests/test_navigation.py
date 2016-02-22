# -*- coding: utf-8 -*-
"""
Tests for the MDWeb Navigation parser

"""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
import unittest
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock

from mdweb.Navigation import Navigation
from mdweb.Exceptions import *


class TestNavigation(fake_filesystem_unittest.TestCase):
    """Navigation object tests """

    def setUp(self):
        """Create fake filesystem"""
        self.setUpPyfakefs()
        self.os = fake_filesystem.FakeOsModule(self.fs)

    def tearDown(self):
        pass

    def test_empty_content_directory(self):
        """An empty content directory should create an empty nav structure."""
        self.fs.CreateDirectory('/my/content')

        nav = Navigation('/my/content')

        self.assertListEqual(nav.child_navs, [])
        self.assertListEqual(nav.child_pages, [])
        self.assertFalse(nav.has_page)
        self.assertEqual(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertIsNone(nav.page)
        self.assertIsNone(nav.name)
        self.assertFalse(nav.has_children)
        self.assertEqual(len(nav.children), 0)

    def test_single_page(self):
        """A single index page should generate a single-page nav structure."""
        self.fs.CreateFile('/my/content/index.md')

        nav = Navigation('/my/content')

        self.assertEqual(nav._root_content_path, '/my/content')
        self.assertListEqual(nav.child_navs, [])
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(nav.has_page, True)
        self.assertEqual(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertEqual(nav.page.page_path, '/my/content/index.md')
        self.assertEqual(nav.page.url_path, '')
        self.assertFalse(nav.has_children)
        self.assertEqual(len(nav.children), 0)

    def test_multiple_pages_at_top_level(self):
        """ Multiple pages at the top level should raise an error.
        Only index supported at the top level. Allowing pages other than
        index at the top leads to a confusing navigation structure.
        """
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/other_page.md')
        self.assertRaises(ContentStructureException, Navigation, '/my/content')

    def test_simple_nested_structure(self):
        """ A simple nested structure with only index.md files should
        create a nested navigation structure.
        """
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md')
        self.fs.CreateFile('/my/content/contact/index.md')

        nav = Navigation('/my/content')

        self.assertEqual(nav._root_content_path, '/my/content')
        self.assertEqual(nav.page.page_path, '/my/content/index.md')
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(len(nav.child_navs), 2)
        self.assertEqual(nav.has_page, True)
        self.assertTrue(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertEqual(nav.page.url_path, '')
        self.assertTrue(nav.has_children)
        self.assertEqual(len(nav.children), 2)

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav._root_content_path, '/my/content')
        self.assertEqual(about_nav.page.page_path,
                         '/my/content/about/index.md')
        self.assertListEqual(about_nav.child_pages, [])
        self.assertListEqual(about_nav.child_navs, [])
        self.assertEqual(about_nav.has_page, True)
        self.assertEqual(about_nav.is_top, False)
        self.assertEqual(about_nav.level, 1)
        self.assertEqual(about_nav.name, 'about')
        self.assertEqual(about_nav.page.url_path, 'about')
        self.assertFalse(about_nav.has_children)
        self.assertEqual(len(about_nav.children), 0)

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav._root_content_path, '/my/content')
        self.assertEqual(contact_nav.page.page_path,
                         '/my/content/contact/index.md')
        self.assertListEqual(contact_nav.child_pages, [])
        self.assertListEqual(contact_nav.child_navs, [])
        self.assertEqual(contact_nav.has_page, True)
        self.assertEqual(contact_nav.is_top, False)
        self.assertEqual(contact_nav.level, 1)
        self.assertEqual(contact_nav.name, 'contact')
        self.assertEqual(contact_nav.page.url_path, 'contact')
        self.assertFalse(contact_nav.has_children)
        self.assertEqual(len(contact_nav.children), 0)


    def test_complex_nested_structure(self):
        """ A complex nested structure with some index files and some
        non-index files should create the appropriate navigation structure.
        """
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/400.md')
        self.fs.CreateFile('/my/content/403.md')
        self.fs.CreateFile('/my/content/404.md')
        self.fs.CreateFile('/my/content/500.md')

        self.fs.CreateFile('/my/content/about/index.md')

        self.fs.CreateFile('/my/content/contact/index.md')
        self.fs.CreateFile('/my/content/contact/westcoast.md')
        self.fs.CreateFile('/my/content/contact/eastcoast.md')

        self.fs.CreateFile('/my/content/work/portfolio/index.md')
        self.fs.CreateFile('/my/content/work/portfolio/landscapes.md')
        self.fs.CreateFile('/my/content/work/portfolio/portraits.md')
        self.fs.CreateFile('/my/content/work/portfolio/nature.md')

        self.fs.CreateFile('/my/content/order/digitalprints.md')
        self.fs.CreateFile('/my/content/order/framed.md')

        nav = Navigation('/my/content')

        self.assertEqual(nav._root_content_path, '/my/content')
        self.assertEqual(nav.page.page_path, '/my/content/index.md')
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(len(nav.child_navs), 4)
        self.assertEqual(nav.has_page, True)
        self.assertEqual(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertEqual(nav.page.url_path, '')
        self.assertTrue(nav.has_children)
        self.assertEqual(len(nav.children), 4)

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav._root_content_path, '/my/content')
        self.assertEqual(about_nav.page.page_path,
                         '/my/content/about/index.md')
        self.assertListEqual(about_nav.child_pages, [])
        self.assertListEqual(about_nav.child_navs, [])
        self.assertEqual(about_nav.has_page, True)
        self.assertEqual(about_nav.is_top, False)
        self.assertEqual(about_nav.level, 1)
        self.assertEqual(about_nav.name, 'about')
        self.assertEqual(about_nav.page.url_path, 'about')
        self.assertFalse(about_nav.has_children)
        self.assertEqual(len(about_nav.children), 0)

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav._root_content_path, '/my/content')
        self.assertEqual(contact_nav.page.page_path,
                         '/my/content/contact/index.md')
        self.assertEqual(len(contact_nav.child_pages), 2)
        self.assertListEqual(contact_nav.child_navs, [])
        self.assertEqual(contact_nav.has_page, True)
        self.assertEqual(contact_nav.is_top, False)
        self.assertEqual(contact_nav.level, 1)
        self.assertEqual(contact_nav.name, 'contact')
        self.assertEqual(contact_nav.child_pages[0].page_path,
                         '/my/content/contact/eastcoast.md')
        self.assertEqual(contact_nav.child_pages[1].page_path,
                         '/my/content/contact/westcoast.md')
        self.assertEqual(contact_nav.page.url_path, 'contact')
        self.assertEqual(contact_nav.child_pages[0].url_path,
                         'contact/eastcoast')
        self.assertEqual(contact_nav.child_pages[1].url_path,
                         'contact/westcoast')
        self.assertTrue(contact_nav.has_children)
        self.assertEqual(len(contact_nav.children), 2)

        order_nav = nav.child_navs[2]
        self.assertEqual(order_nav._root_content_path, '/my/content')
        self.assertIsNone(order_nav.page)
        self.assertEqual(len(order_nav.child_pages), 2)
        self.assertListEqual(order_nav.child_navs, [])
        self.assertEqual(order_nav.has_page, False)
        self.assertEqual(order_nav.is_top, False)
        self.assertEqual(order_nav.level, 1)
        self.assertEqual(order_nav.name, 'order')
        self.assertEqual(order_nav.child_pages[0].page_path,
                         '/my/content/order/digitalprints.md')
        self.assertEqual(order_nav.child_pages[1].page_path,
                         '/my/content/order/framed.md')
        self.assertEqual(order_nav.child_pages[0].url_path,
                         'order/digitalprints')
        self.assertEqual(order_nav.child_pages[1].url_path,
                         'order/framed')
        self.assertTrue(order_nav.has_children)
        self.assertEqual(len(order_nav.children), 2)

        work_nav = nav.child_navs[3]
        self.assertEqual(work_nav._root_content_path, '/my/content')
        self.assertIsNone(work_nav.page)
        self.assertListEqual(work_nav.child_pages, [])
        self.assertEqual(len(work_nav.child_navs), 1)
        self.assertEqual(work_nav.has_page, False)
        self.assertEqual(work_nav.is_top, False)
        self.assertEqual(work_nav.level, 1)
        self.assertEqual(work_nav.name, 'work')
        self.assertTrue(work_nav.has_children)
        self.assertEqual(len(work_nav.children), 1)

        work_portfolio_nav = nav.child_navs[3].child_navs[0]
        self.assertEqual(work_portfolio_nav._root_content_path, '/my/content')
        self.assertEqual(work_portfolio_nav.page.page_path,
                         '/my/content/work/portfolio/index.md')
        self.assertEqual(len(work_portfolio_nav.child_pages), 3)
        self.assertListEqual(work_portfolio_nav.child_navs, [])
        self.assertEqual(work_portfolio_nav.has_page, True)
        self.assertEqual(work_portfolio_nav.is_top, False)
        self.assertEqual(work_portfolio_nav.level, 2)
        self.assertEqual(work_portfolio_nav.name, 'portfolio')
        self.assertEqual(work_portfolio_nav.child_pages[0].page_path,
                         '/my/content/work/portfolio/landscapes.md')
        self.assertEqual(work_portfolio_nav.child_pages[1].page_path,
                         '/my/content/work/portfolio/nature.md')
        self.assertEqual(work_portfolio_nav.child_pages[2].page_path,
                         '/my/content/work/portfolio/portraits.md')
        self.assertEqual(work_portfolio_nav.page.url_path, 'work/portfolio')
        self.assertEqual(work_portfolio_nav.child_pages[0].url_path,
                         'work/portfolio/landscapes')
        self.assertEqual(work_portfolio_nav.child_pages[1].url_path,
                         'work/portfolio/nature')
        self.assertEqual(work_portfolio_nav.child_pages[2].url_path,
                         'work/portfolio/portraits')
        self.assertTrue(work_portfolio_nav.has_children)
        self.assertEqual(len(work_portfolio_nav.children), 3)

    def test_symlink_following(self):
        """ Navigation parsing should follow symlinks."""
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/some/other/directory/index.md')
        self.fs.CreateLink('/my/content/about/index.md',
                           '/some/other/directory/index.md')
        self.fs.CreateFile('/some/other/other/directory/index.md')
        self.fs.CreateLink('/my/content/contact',
                           '/some/other/other/directory')

        nav = Navigation('/my/content')

        self.assertEqual(nav._root_content_path, '/my/content')
        self.assertEqual(nav.page.page_path, '/my/content/index.md')
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(len(nav.child_navs), 2)
        self.assertEqual(nav.has_page, True)
        self.assertTrue(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertEqual(nav.page.url_path, '')
        self.assertTrue(nav.has_children)
        self.assertEqual(len(nav.children), 2)

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav._root_content_path, '/my/content')
        self.assertEqual(about_nav.page.page_path,
                         '/my/content/about/index.md')
        self.assertListEqual(about_nav.child_pages, [])
        self.assertListEqual(about_nav.child_navs, [])
        self.assertEqual(about_nav.has_page, True)
        self.assertEqual(about_nav.is_top, False)
        self.assertEqual(about_nav.level, 1)
        self.assertEqual(about_nav.name, 'about')
        self.assertEqual(about_nav.page.url_path, 'about')
        self.assertFalse(about_nav.has_children)
        self.assertEqual(len(about_nav.children), 0)

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav._root_content_path, '/my/content')
        self.assertEqual(contact_nav.page.page_path,
                         '/my/content/contact/index.md')
        self.assertListEqual(contact_nav.child_pages, [])
        self.assertListEqual(contact_nav.child_navs, [])
        self.assertEqual(contact_nav.has_page, True)
        self.assertEqual(contact_nav.is_top, False)
        self.assertEqual(contact_nav.level, 1)
        self.assertEqual(contact_nav.name, 'contact')
        self.assertEqual(contact_nav.page.url_path, 'contact')
        self.assertFalse(contact_nav.has_children)
        self.assertEqual(len(contact_nav.children), 0)

    def test_nav_file_already_open(self):
        """Parsing open files should succeed."""
        fs_open = fake_filesystem.FakeFileOpen(self.fs)
        self.fs.CreateFile('/my/content/index.md')
        open_fd = fs_open('/my/content/index.md', 'r')

        nav = Navigation('/my/content')

        self.assertEqual(nav._root_content_path, '/my/content')
        self.assertListEqual(nav.child_navs, [])
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(nav.has_page, True)
        self.assertEqual(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertEqual(nav.page.page_path, '/my/content/index.md')
        self.assertEqual(nav.page.url_path, '')
        self.assertFalse(nav.has_children)
        self.assertEqual(len(nav.children), 0)

    def test_unsupported_extensions(self):
        """Unsupported extensions should be skipped."""
        self.fs.CreateFile('/my/content/index.xls')

        nav = Navigation('/my/content')

        self.assertListEqual(nav.child_navs, [])
        self.assertListEqual(nav.child_pages, [])
        self.assertFalse(nav.has_page)
        self.assertEqual(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertIsNone(nav.page)
        self.assertIsNone(nav.name)
        self.assertFalse(nav.has_children)
        self.assertEqual(len(nav.children), 0)

    @unittest.skip("Broken test")
    # PermissionError only exists in Python 3.3+, need to fix this
    # http://stackoverflow.com/a/18199529/1436323
    def test_file_persmissions(self):
        """Inaccessible files (due to permissions) should raise PermissionError."""
        self.fs.CreateFile('/my/content/index.md')
        self.os.chmod('/my/content/index.md', 0o000)

        self.assertRaises(PermissionError, Navigation, '/my/content')

    def test_weird_path_and_filenames(self):
        """All valid paths and filenames should be supported."""
        self.fs.CreateFile('/Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon/久有归天愿/diz çöktürmüş/index.md')

        nav = Navigation('/Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon/久有归天愿/diz çöktürmüş')

        self.assertEqual(nav._root_content_path, '/Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon/久有归天愿/diz çöktürmüş')
        self.assertListEqual(nav.child_navs, [])
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(nav.has_page, True)
        self.assertEqual(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertEqual(nav.page.page_path, '/Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon/久有归天愿/diz çöktürmüş/index.md')
        self.assertEqual(nav.page.url_path, '')
        self.assertFalse(nav.has_children)
        self.assertEqual(len(nav.children), 0)

    def test_get_page_dict(self):
        """The method should return a flattend dictionary of all pages."""
        self.fs.CreateFile('/my/content/index.md')

        self.fs.CreateFile('/my/content/about/index.md')

        self.fs.CreateFile('/my/content/contact/index.md')
        self.fs.CreateFile('/my/content/contact/westcoast.md')
        self.fs.CreateFile('/my/content/contact/eastcoast.md')

        self.fs.CreateFile('/my/content/work/portfolio/index.md')
        self.fs.CreateFile('/my/content/work/portfolio/landscapes.md')
        self.fs.CreateFile('/my/content/work/portfolio/portraits.md')
        self.fs.CreateFile('/my/content/work/portfolio/nature.md')

        self.fs.CreateFile('/my/content/order/digitalprints.md')
        self.fs.CreateFile('/my/content/order/framed.md')

        nav = Navigation('/my/content')

        page_dict = nav.get_page_dict()

        self.assertEqual(page_dict[''].page_path, '/my/content/index.md')
        self.assertEqual(page_dict['contact'].page_path,
                         '/my/content/contact/index.md')
        self.assertEqual(page_dict['contact/westcoast'].page_path,
                         '/my/content/contact/westcoast.md')
        self.assertEqual(page_dict['contact/eastcoast'].page_path,
                         '/my/content/contact/eastcoast.md')
        self.assertEqual(page_dict['work/portfolio'].page_path,
                         '/my/content/work/portfolio/index.md')
        self.assertEqual(page_dict['work/portfolio/landscapes'].page_path,
                         '/my/content/work/portfolio/landscapes.md')
        self.assertEqual(page_dict['work/portfolio/portraits'].page_path,
                         '/my/content/work/portfolio/portraits.md')
        self.assertEqual(page_dict['work/portfolio/nature'].page_path,
                         '/my/content/work/portfolio/nature.md')
        self.assertEqual(page_dict['order/digitalprints'].page_path,
                         '/my/content/order/digitalprints.md')
        self.assertEqual(page_dict['order/framed'].page_path,
                         '/my/content/order/framed.md')

    def test_print_debug(self):
        """ A complex nested structure with some index files and some
        non-index files should create the appropriate navigation structure.
        """
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/400.md')
        self.fs.CreateFile('/my/content/403.md')
        self.fs.CreateFile('/my/content/404.md')
        self.fs.CreateFile('/my/content/500.md')

        self.fs.CreateFile('/my/content/about/index.md')

        self.fs.CreateFile('/my/content/contact/index.md')
        self.fs.CreateFile('/my/content/contact/westcoast.md')
        self.fs.CreateFile('/my/content/contact/eastcoast.md')

        self.fs.CreateFile('/my/content/work/portfolio/index.md')
        self.fs.CreateFile('/my/content/work/portfolio/landscapes.md')
        self.fs.CreateFile('/my/content/work/portfolio/portraits.md')
        self.fs.CreateFile('/my/content/work/portfolio/nature.md')

        self.fs.CreateFile('/my/content/order/digitalprints.md')
        self.fs.CreateFile('/my/content/order/framed.md')

        nav = Navigation('/my/content')

        # Run print_debug_nav() with an IO buffer to capture the output
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        out = StringIO()
        nav.print_debug_nav(out=out)
        output = out.getvalue().strip()

        self.assertEqual(output, '''+-Navigation Structure----------------------------+|   N  = Navigtion Level                          ||          [*:9]] = [has_page:nav_level]          ||   P = Page                                      |+-------------------------------------------------+N[*:0] None (/my/content) {}''')