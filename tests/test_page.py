"""
Tests for the MDWeb Navigation parser

Tests to write
  * Handle symlinks
  * File already open
  * Non supported extension (.xls)
  * Permissions
Maybe test?
  * atime, mtime
  * large file

"""
from pyfakefs import fake_filesystem_unittest
import unittest
try:
    # Python >= 3.3
    from unittest import mock
except ImportError:
    # Python < 3.3
    import mock

from mdweb.Page import PageMetaInf, Page
from mdweb.Exceptions import *


class TestPageMeta(fake_filesystem_unittest.TestCase):
    """Navigation object tests """

    def setUp(self):
        """Create fake filesystem"""
        self.setUpPyfakefs()

    def tearDown(self):
        pass

    def test_parse_empty_string(self):
        file_string = u""

        meta_inf = PageMetaInf(file_string)

        self.assertIsNone(meta_inf.author)
        self.assertIsNone(meta_inf.date)
        self.assertIsNone(meta_inf.description)
        self.assertEqual(meta_inf.order, 0)
        self.assertIsNone(meta_inf.robots)
        self.assertIsNone(meta_inf.template)
        self.assertIsNone(meta_inf.title)

    def test_parse_no_meta(self):
        file_string = u"""##MDWeb is Not a CMS (NaCMS)

MDWeb is a markdown based web site framework.

MDWeb is painstakingly designed to be as minimalistic as possible while taking
less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and
adding content. I'm a firm believer in the ethos that CMS is an evil that
should be rid from this world. I spent years fighting horrific battles with
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen."""

        meta_inf = PageMetaInf(file_string)

        self.assertIsNone(meta_inf.author)
        self.assertIsNone(meta_inf.date)
        self.assertIsNone(meta_inf.description)
        self.assertEqual(meta_inf.order, 0)
        self.assertIsNone(meta_inf.robots)
        self.assertIsNone(meta_inf.template)
        self.assertIsNone(meta_inf.title)

    def test_parse_some_fields(self):
        file_string = u"""/*
Title: MDWeb
Description: The minimalistic markdown NaCMS
Date: February 1st, 2016
*/


##MDWeb is Not a CMS (NaCMS)

MDWeb is a markdown based web site framework.

MDWeb is painstakingly designed to be as minimalistic as possible while taking
less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and
adding content. I'm a firm believer in the ethos that CMS is an evil that
should be rid from this world. I spent years fighting horrific battles with
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen.
        """

        meta_inf = PageMetaInf(file_string)

        self.assertIsNone(meta_inf.author)
        self.assertEqual(meta_inf.date, u'February 1st, 2016')
        self.assertEqual(meta_inf.description, u'The minimalistic markdown NaCMS')
        self.assertEqual(meta_inf.order, 0)
        self.assertIsNone(meta_inf.robots)
        self.assertIsNone(meta_inf.template)
        self.assertEqual(meta_inf.title, u'MDWeb')

    def test_parse_all_fields(self):
        file_string = u"""/*
Title: MDWeb
Description: The minimalistic markdown NaCMS
Author: Chad Rempp
Date: February 1st, 2016
Order: 1
Template: page_home.html
Robots: User-agent: *
*/


##MDWeb is Not a CMS (NaCMS)

MDWeb is a markdown based web site framework.

MDWeb is painstakingly designed to be as minimalistic as possible while taking
less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and
adding content. I'm a firm believer in the ethos that CMS is an evil that
should be rid from this world. I spent years fighting horrific battles with
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen.
        """

        meta_inf = PageMetaInf(file_string)

        self.assertEqual(meta_inf.author, u'Chad Rempp')
        self.assertEqual(meta_inf.date, u'February 1st, 2016')
        self.assertEqual(meta_inf.description, u'The minimalistic markdown NaCMS')
        self.assertEqual(meta_inf.order, 1)
        self.assertEqual(meta_inf.robots, u'User-agent: *')
        self.assertEqual(meta_inf.template, u'page_home.html')
        self.assertEqual(meta_inf.title, u'MDWeb')

    def test_metainf_spacing(self):
        file_string = u""" /*
Title: MDWeb
 Description: The minimalistic markdown NaCMS
Author: Chad Rempp

Date : February 1st, 2016
Order: 1
Template:     page_home.html
Robots: User-agent: *

*/


##MDWeb is Not a CMS (NaCMS)

MDWeb is a markdown based web site framework.

MDWeb is painstakingly designed to be as minimalistic as possible while taking
less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and
adding content. I'm a firm believer in the ethos that CMS is an evil that
should be rid from this world. I spent years fighting horrific battles with
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen.
        """

        meta_inf = PageMetaInf(file_string)

        self.assertEqual(meta_inf.author, u'Chad Rempp')
        self.assertEqual(meta_inf.date, u'February 1st, 2016')
        self.assertEqual(meta_inf.description, u'The minimalistic markdown NaCMS')
        self.assertEqual(meta_inf.order, 1)
        self.assertEqual(meta_inf.robots, u'User-agent: *')
        self.assertEqual(meta_inf.template, u'page_home.html')
        self.assertEqual(meta_inf.title, u'MDWeb')

    def test_comments(self):
        file_string = u"""/*
# This is a comment
Title: MDWeb
Description: The minimalistic markdown NaCMS
#Author: Chad Rempp
#Date: February 1st, 2016
Order: 1
Template: page_home.html
#
Robots: User-agent: *
# Nothing to see here
*/


##MDWeb is Not a CMS (NaCMS)

MDWeb is a markdown based web site framework.

MDWeb is painstakingly designed to be as minimalistic as possible while taking
less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and
adding content. I'm a firm believer in the ethos that CMS is an evil that
should be rid from this world. I spent years fighting horrific battles with
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen.
        """

        meta_inf = PageMetaInf(file_string)

        self.assertIsNone(meta_inf.author)
        self.assertIsNone(meta_inf.date)
        self.assertEqual(meta_inf.description, u'The minimalistic markdown NaCMS')
        self.assertEqual(meta_inf.order, 1)
        self.assertEqual(meta_inf.robots, u'User-agent: *')
        self.assertEqual(meta_inf.template, u'page_home.html')
        self.assertEqual(meta_inf.title, u'MDWeb')

    def test_unsupported_field(self):
        file_string = u"""/*
Title: MDWeb
Description: The minimalistic markdown NaCMS
Badfield: Dragons be here
Author: Chad Rempp
Date: February 1st, 2016
Order: 1
Template: page_home.html
Robots: User-agent: *
*/


##MDWeb is Not a CMS (NaCMS)

MDWeb is a markdown based web site framework.

MDWeb is painstakingly designed to be as minimalistic as possible while taking
less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and
adding content. I'm a firm believer in the ethos that CMS is an evil that
should be rid from this world. I spent years fighting horrific battles with
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen.
        """
        self.assertRaises(PageMetaInfFieldException, PageMetaInf, file_string)

    def test_unicode(self):
        file_string = u"""/*
Title: советских
Description: ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ
Author: Οδυσσέα Ελύτη
Date: February 1st, 2016
Order: 1
Template: ღმერთსი.html
Robots: User-agent: *
*/


##MDWeb is Not a CMS (NaCMS)

MDWeb is a markdown based web site framework.

MDWeb is painstakingly designed to be as minimalistic as possible while taking
less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and
adding content. I'm a firm believer in the ethos that CMS is an evil that
should be rid from this world. I spent years fighting horrific battles with
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen.
        """

        meta_inf = PageMetaInf(file_string)

        self.assertEqual(meta_inf.author, u'Οδυσσέα Ελύτη')
        self.assertEqual(meta_inf.date, u'February 1st, 2016')
        self.assertEqual(meta_inf.description, u'ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ')
        self.assertEqual(meta_inf.order, 1)
        self.assertEqual(meta_inf.robots, u'User-agent: *')
        self.assertEqual(meta_inf.template, u'ღმერთსი.html')
        self.assertEqual(meta_inf.title, u'советских')