"""
Tests for the MDWeb Navigation parser

"""
from pyfakefs import fake_filesystem_unittest
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
        self.assertEqual(nav.page.filepath, '/my/content/index.md')

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

        nav.print_debug_nav()

        self.assertEqual(nav._root_content_path, '/my/content')
        self.assertEqual(nav.page.filepath, '/my/content/index.md')
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(len(nav.child_navs), 2)
        self.assertEqual(nav.has_page, True)
        self.assertTrue(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav._root_content_path, '/my/content')
        self.assertEqual(about_nav.page.filepath,
                         '/my/content/about/index.md')
        self.assertListEqual(about_nav.child_pages, [])
        self.assertListEqual(about_nav.child_navs, [])
        self.assertEqual(about_nav.has_page, True)
        self.assertEqual(about_nav.is_top, False)
        self.assertEqual(about_nav.level, 1)
        self.assertEqual(about_nav.name, 'about')

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav._root_content_path, '/my/content')
        self.assertEqual(contact_nav.page.filepath,
                         '/my/content/contact/index.md')
        self.assertListEqual(contact_nav.child_pages, [])
        self.assertListEqual(contact_nav.child_navs, [])
        self.assertEqual(contact_nav.has_page, True)
        self.assertEqual(contact_nav.is_top, False)
        self.assertEqual(contact_nav.level, 1)
        self.assertEqual(contact_nav.name, 'contact')


    def test_complex_nested_structure(self):
        """ A complex nested structure with some index files and some
        non-index files should create the appropriate navigation structure.
        """
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

        nav.print_debug_nav()

        self.assertEqual(nav._root_content_path, '/my/content')
        self.assertEqual(nav.page.filepath, '/my/content/index.md')
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(len(nav.child_navs), 4)
        self.assertEqual(nav.has_page, True)
        self.assertEqual(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav._root_content_path, '/my/content')
        self.assertEqual(about_nav.page.filepath,
                         '/my/content/about/index.md')
        self.assertListEqual(about_nav.child_pages, [])
        self.assertListEqual(about_nav.child_navs, [])
        self.assertEqual(about_nav.has_page, True)
        self.assertEqual(about_nav.is_top, False)
        self.assertEqual(about_nav.level, 1)
        self.assertEqual(about_nav.name, 'about')

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav._root_content_path, '/my/content')
        self.assertEqual(contact_nav.page.filepath,
                         '/my/content/contact/index.md')
        self.assertEqual(len(contact_nav.child_pages), 2)
        self.assertListEqual(contact_nav.child_navs, [])
        self.assertEqual(contact_nav.has_page, True)
        self.assertEqual(contact_nav.is_top, False)
        self.assertEqual(contact_nav.level, 1)
        self.assertEqual(contact_nav.name, 'contact')
        self.assertEqual(contact_nav.child_pages[0].filepath,
                         '/my/content/contact/eastcoast.md')
        self.assertEqual(contact_nav.child_pages[1].filepath,
                         '/my/content/contact/westcoast.md')

        order_nav = nav.child_navs[2]
        self.assertEqual(order_nav._root_content_path, '/my/content')
        self.assertIsNone(order_nav.page)
        self.assertEqual(len(order_nav.child_pages), 2)
        self.assertListEqual(order_nav.child_navs, [])
        self.assertEqual(order_nav.has_page, False)
        self.assertEqual(order_nav.is_top, False)
        self.assertEqual(order_nav.level, 1)
        self.assertEqual(order_nav.name, 'order')
        self.assertEqual(order_nav.child_pages[0].filepath,
                         '/my/content/order/digitalprints.md')
        self.assertEqual(order_nav.child_pages[1].filepath,
                         '/my/content/order/framed.md')

        work_nav = nav.child_navs[3]
        self.assertEqual(work_nav._root_content_path, '/my/content')
        self.assertIsNone(work_nav.page)
        self.assertListEqual(work_nav.child_pages, [])
        self.assertEqual(len(work_nav.child_navs), 1)
        self.assertEqual(work_nav.has_page, False)
        self.assertEqual(work_nav.is_top, False)
        self.assertEqual(work_nav.level, 1)
        self.assertEqual(work_nav.name, 'work')

        work_portfolio_nav = nav.child_navs[3].child_navs[0]
        self.assertEqual(work_portfolio_nav._root_content_path, '/my/content')
        self.assertEqual(work_portfolio_nav.page.filepath,
                         '/my/content/work/portfolio/index.md')
        self.assertEqual(len(work_portfolio_nav.child_pages), 3)
        self.assertListEqual(work_portfolio_nav.child_navs, [])
        self.assertEqual(work_portfolio_nav.has_page, True)
        self.assertEqual(work_portfolio_nav.is_top, False)
        self.assertEqual(work_portfolio_nav.level, 2)
        self.assertEqual(work_portfolio_nav.name, 'portfolio')
        self.assertEqual(work_portfolio_nav.child_pages[0].filepath,
                         '/my/content/work/portfolio/landscapes.md')
        self.assertEqual(work_portfolio_nav.child_pages[1].filepath,
                         '/my/content/work/portfolio/nature.md')
        self.assertEqual(work_portfolio_nav.child_pages[2].filepath,
                         '/my/content/work/portfolio/portraits.md')

    @unittest.skip("Test not implemented")
    def test_nav_level_numbering(self):
        """ Navigation levels (level) should match the directory level."""
        pass

    @unittest.skip("Test not implemented")
    def test_symlink_following(self):
        """ Navigation parsing should follow symlinks."""
        pass

    @unittest.skip("Test not implemented")
    def test_nav_file_already_open(self):
        """Parsing open files should raise NavigationUnparsable."""
        pass

    @unittest.skip("Test not implemented")
    def test_unsupported_extensions(self):
        """Unsupported extensions should be skipped."""
        pass

    @unittest.skip("Test not implemented")
    def test_file_persmissions(self):
        """Inaccessible files (due to permissions) should raise NavigationUnparsable."""
        pass
