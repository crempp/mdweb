# -*- coding: utf-8 -*-
"""Tests for the MDWeb Navigation parser."""
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from mdweb.Navigation import Navigation, NavigationMetaInf
from mdweb.Exceptions import ContentException, ContentStructureException


class TestNavigation(fake_filesystem_unittest.TestCase):

    """Navigation object tests."""

    def setUp(self):
        """Create fake filesystem."""
        self.setUpPyfakefs()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

    def test_empty_content_directory(self):
        """An empty content directory should create an empty nav structure."""
        self.fs.CreateDirectory('/my/content')

        self.assertRaises(ContentException, Navigation, '/my/content')

    def test_single_page(self):
        """A single index page should generate a single-page nav structure."""
        self.fs.CreateFile('/my/content/index.md')

        nav = Navigation('/my/content')

        self.assertEqual(nav.root_content_path, '/my/content')
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
        self.assertEqual(nav.order, 0)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

    def test_multiple_toplevel_pages(self):
        """Multiple pages at the top level should raise an error.

        Only index supported at the top level. Allowing pages other than
        index at the top leads to a confusing navigation structure.
        """
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/other_page.md')
        self.assertRaises(ContentStructureException, Navigation, '/my/content')

    def test_simple_nested_structure(self):
        """A simple nested structure should create navigation structure."""
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md')
        self.fs.CreateFile('/my/content/contact/index.md')

        nav = Navigation('/my/content')

        self.assertEqual(nav.root_content_path, '/my/content')
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
        self.assertEqual(nav.order, 0)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav.root_content_path, '/my/content')
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
        self.assertEqual(about_nav.order, 0)
        self.assertEqual(about_nav.id, '46b3931b9959c927df4fc65fdee94b07')
        self.assertEqual(about_nav.slug, 'about')

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav.root_content_path, '/my/content')
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
        self.assertEqual(contact_nav.order, 0)
        self.assertEqual(contact_nav.id, '2f8a6bf31f3bd67bd2d9720c58b19c9a')
        self.assertEqual(contact_nav.slug, 'contact')

    def test_complex_nested_structure(self):
        """A complex nested structure should create navigation structure."""
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

        self.assertEqual(nav.root_content_path, '/my/content')
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
        self.assertEqual(nav.order, 0)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav.root_content_path, '/my/content')
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
        self.assertEqual(about_nav.order, 0)
        self.assertEqual(about_nav.id, '46b3931b9959c927df4fc65fdee94b07')
        self.assertEqual(about_nav.slug, 'about')

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav.root_content_path, '/my/content')
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
        self.assertEqual(contact_nav.order, 0)
        self.assertEqual(contact_nav.id, '2f8a6bf31f3bd67bd2d9720c58b19c9a')
        self.assertEqual(contact_nav.slug, 'contact')

        order_nav = nav.child_navs[2]
        self.assertEqual(order_nav.root_content_path, '/my/content')
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
        self.assertEqual(order_nav.order, 0)
        self.assertEqual(order_nav.id, '70a17ffa722a3985b86d30b034ad06d7')
        self.assertEqual(order_nav.slug, 'order')

        work_nav = nav.child_navs[3]
        self.assertEqual(work_nav.root_content_path, '/my/content')
        self.assertIsNone(work_nav.page)
        self.assertListEqual(work_nav.child_pages, [])
        self.assertEqual(len(work_nav.child_navs), 1)
        self.assertEqual(work_nav.has_page, False)
        self.assertEqual(work_nav.is_top, False)
        self.assertEqual(work_nav.level, 1)
        self.assertEqual(work_nav.name, 'work')
        self.assertTrue(work_nav.has_children)
        self.assertEqual(len(work_nav.children), 1)
        self.assertEqual(work_nav.order, 0)
        self.assertEqual(work_nav.id, '67e92c8765a9bc7fb2d335c459de9eb5')
        self.assertEqual(work_nav.slug, 'work')

        work_portfolio_nav = nav.child_navs[3].child_navs[0]
        self.assertEqual(work_portfolio_nav.root_content_path, '/my/content')
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
        self.assertEqual(work_portfolio_nav.order, 0)
        self.assertEqual(work_portfolio_nav.id, 'd5324c9d8797e07c58b139b50efc5cf0')
        self.assertEqual(work_portfolio_nav.slug, 'work_portfolio')

    def test_symlink_following(self):
        """Navigation parsing should follow symlinks."""
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/some/other/directory/index.md')
        self.fs.CreateLink('/my/content/about/index.md',
                           '/some/other/directory/index.md')
        self.fs.CreateFile('/some/other/other/directory/index.md')
        self.fs.CreateLink('/my/content/contact',
                           '/some/other/other/directory')

        nav = Navigation('/my/content')

        self.assertEqual(nav.root_content_path, '/my/content')
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
        self.assertEqual(nav.order, 0)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav.root_content_path, '/my/content')
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
        self.assertEqual(about_nav.order, 0)
        self.assertEqual(about_nav.id, '46b3931b9959c927df4fc65fdee94b07')
        self.assertEqual(about_nav.slug, 'about')

        contact_nav = nav.child_navs[1]
        self.assertEqual(contact_nav.root_content_path, '/my/content')
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
        self.assertEqual(contact_nav.order, 0)
        self.assertEqual(contact_nav.id, '2f8a6bf31f3bd67bd2d9720c58b19c9a')
        self.assertEqual(contact_nav.slug, 'contact')

    def test_nav_file_already_open(self):
        """Parsing open files should succeed."""
        fs_open = fake_filesystem.FakeFileOpen(self.fs)
        self.fs.CreateFile('/my/content/index.md')
        open_fd = fs_open('/my/content/index.md', 'r')

        nav = Navigation('/my/content')

        open_fd.close()

        self.assertEqual(nav.root_content_path, '/my/content')
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
        self.assertEqual(nav.order, 0)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

    def test_unsupported_extensions(self):
        """Unsupported extensions should be skipped."""
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/stuff/index.xls')

        nav = Navigation('/my/content')

        stuff_nav = nav.child_navs[0]

        self.assertListEqual(stuff_nav.child_navs, [])
        self.assertListEqual(stuff_nav.child_pages, [])
        self.assertFalse(stuff_nav.has_page)
        self.assertIsNone(stuff_nav.page)
        self.assertFalse(stuff_nav.has_children)
        self.assertEqual(len(stuff_nav.children), 0)
        self.assertEqual(stuff_nav.id, 'c13d88cb4cb02003daedb8a84e5d272a')
        self.assertEqual(stuff_nav.slug, 'stuff')

    # PermissionError only exists in Python 3.3+, need to fix this
    # http://stackoverflow.com/a/18199529/1436323
    def test_file_persmissions(self):
        """Inaccessible files (due to perms) should raise IOError."""
        self.fs.CreateFile('/my/content/index.md')
        self.fake_os.chmod('/my/content/index.md', 0o000)

        self.assertRaises(IOError, Navigation, '/my/content')

    def test_weird_path_and_filenames(self):
        """All valid paths and filenames should be supported."""
        self.fs.CreateFile('/Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon/久有归天愿/diz çöktürmüş/index.md')

        nav = Navigation('/Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon/久有归天愿/diz çöktürmüş')

        self.assertEqual(nav.root_content_path, '/Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon/久有归天愿/diz çöktürmüş')
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
        self.assertEqual(nav.order, 0)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

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

    def test_mising_root_index(self):
        """A missing root level index should throw ContentException."""
        self.fs.CreateFile('/my/content/about/index.md')

        self.fs.CreateFile('/my/content/contact/index.md')
        self.fs.CreateFile('/my/content/contact/westcoast.md')
        self.fs.CreateFile('/my/content/contact/eastcoast.md')

        self.assertRaises(ContentException, Navigation, '/my/content')

    def test_nav_level_metainf(self):
        """Navigation Meta-inf parser should parse correctly."""
        file_string = u"""# The about section is about me and my life on earth
#
# I intend on filling it with all the interesting things I've done.

Nav Name: About Me
Order: 8
"""

        meta_inf = NavigationMetaInf(file_string)

        self.assertEqual(meta_inf.nav_name, "About Me")
        self.assertEqual(meta_inf.order, 8)

    def test_nav_metainf_file(self):
        """_navlevel.txt file should parse correctly."""
        file_string = u"""# The about section is about me and my life on earth
#
# I intend on filling it with all the interesting things I've done.

Nav Name: About Me
Order: 8
"""
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md')
        self.fs.CreateFile('/my/content/about/_navlevel.txt',
                           contents=file_string)

        nav = Navigation('/my/content')

        self.assertEqual(nav.root_content_path, '/my/content')
        self.assertEqual(nav.page.page_path, '/my/content/index.md')
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(len(nav.child_navs), 1)
        self.assertEqual(nav.has_page, True)
        self.assertTrue(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertIsNone(nav.name)
        self.assertEqual(nav.page.url_path, '')
        self.assertTrue(nav.has_children)
        self.assertEqual(len(nav.children), 1)
        self.assertEqual(nav.order, 0)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav.root_content_path, '/my/content')
        self.assertEqual(about_nav.page.page_path,
                         '/my/content/about/index.md')
        self.assertListEqual(about_nav.child_pages, [])
        self.assertListEqual(about_nav.child_navs, [])
        self.assertEqual(about_nav.has_page, True)
        self.assertEqual(about_nav.is_top, False)
        self.assertEqual(about_nav.level, 1)
        self.assertEqual(about_nav.name, 'About Me')
        self.assertEqual(about_nav.page.url_path, 'about')
        self.assertFalse(about_nav.has_children)
        self.assertEqual(len(about_nav.children), 0)
        self.assertEqual(about_nav.order, 8)
        self.assertEqual(about_nav.id, '46b3931b9959c927df4fc65fdee94b07')
        self.assertEqual(about_nav.slug, 'about')
        
    def test_nav_home_metainf_file(self):
        """Top-level _navlevel.txt should parse properly."""
        file_string = u"""# The home page is where the important things are

Nav Name: home
Order: -34
"""
        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md')
        self.fs.CreateFile('/my/content/_navlevel.txt',
                           contents=file_string)

        nav = Navigation('/my/content')

        self.assertEqual(nav.root_content_path, '/my/content')
        self.assertEqual(nav.page.page_path, '/my/content/index.md')
        self.assertListEqual(nav.child_pages, [])
        self.assertEqual(len(nav.child_navs), 1)
        self.assertEqual(nav.has_page, True)
        self.assertTrue(nav.is_top, True)
        self.assertEqual(nav.level, 0)
        self.assertEqual(nav.name, "home")
        self.assertEqual(nav.page.url_path, '')
        self.assertTrue(nav.has_children)
        self.assertEqual(len(nav.children), 1)
        self.assertEqual(nav.order, -34)
        self.assertEqual(nav.id, 'b14a7b8059d9c055954c92674ce60032')
        self.assertEqual(nav.slug, '_')

        about_nav = nav.child_navs[0]
        self.assertEqual(about_nav.root_content_path, '/my/content')
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
        self.assertEqual(about_nav.order, 0)
        self.assertEqual(about_nav.id, '46b3931b9959c927df4fc65fdee94b07')
        self.assertEqual(about_nav.slug, 'about')

    def test_nav_ordering(self):
        """Navigation should follow ordering defined in meta-inf."""
        self.fs.CreateFile('/my/content/about/_navlevel.txt',
                           contents='Order: 4')
        self.fs.CreateFile('/my/content/contact/_navlevel.txt',
                           contents='Order: 1')
        self.fs.CreateFile('/my/content/work/_navlevel.txt',
                           contents='Order: 7')

        self.fs.CreateFile('/my/content/index.md')
        self.fs.CreateFile('/my/content/about/index.md', contents='''/*
                            Order: 5
                            */''')
        self.fs.CreateFile('/my/content/contact/index.md', contents='''/*
                            Order: 10
                            */''')
        self.fs.CreateFile('/my/content/contact/westcoast.md', contents='''/*
                            Order: 6
                            */''')
        self.fs.CreateFile('/my/content/contact/eastcoast.md', contents='''/*
                            Order: 3
                            */''')
        self.fs.CreateFile('/my/content/work/portfolio/index.md',
                           contents='''/*
                           Order: 9
                           */''')
        self.fs.CreateFile('/my/content/work/portfolio/landscapes.md',
                           contents='''/*
                            Order: 10
                            */''')
        self.fs.CreateFile('/my/content/work/portfolio/portraits.md',
                           contents='''/*
                            Order: 11
                            */''')
        self.fs.CreateFile('/my/content/work/portfolio/nature.md',
                           contents='''/*
                            Order: 8
                            */''')

        nav = Navigation('/my/content')

        self.assertEqual(nav.child_navs[0].content_path, '/my/content/contact')
        self.assertEqual(nav.child_navs[0].child_pages[0].page_path,
                         '/my/content/contact/eastcoast.md')
        self.assertEqual(nav.child_navs[0].child_pages[1].page_path,
                         '/my/content/contact/westcoast.md')
        self.assertEqual(nav.child_navs[1].content_path, '/my/content/about')
        self.assertEqual(nav.child_navs[2].content_path, '/my/content/work')
        self.assertEqual(nav.child_navs[2].child_navs[0].child_pages[0]
                         .page_path, '/my/content/work/portfolio/nature.md')
        self.assertEqual(nav.child_navs[2].child_navs[0].child_pages[1]
                         .page_path, '/my/content/work/portfolio/landscapes.md')
        self.assertEqual(nav.child_navs[2].child_navs[0].child_pages[2]
                         .page_path, '/my/content/work/portfolio/portraits.md')
