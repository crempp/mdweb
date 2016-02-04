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
    """PageMetaInf object tests """

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

    @unittest.skip("Test not implemented")
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
        file_string = u"""Title: MDWeb
Description: The minimalistic markdown NaCMS
Date: February 1st, 2016
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
        file_string = u"""Title: MDWeb
Description: The minimalistic markdown NaCMS
Author: Chad Rempp
Date: February 1st, 2016
Order: 1
Template: page_home.html
Robots: User-agent: *
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
        file_string = u"""Title: MDWeb
 Description: The minimalistic markdown NaCMS
Author: Chad Rempp

Date : February 1st, 2016
Order: 1
Template:     page_home.html
Robots: User-agent: *

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
        file_string = u"""# This is a comment
Title: MDWeb
Description: The minimalistic markdown NaCMS
#Author: Chad Rempp
#Date: February 1st, 2016
Order: 1
Template: page_home.html
#
Robots: User-agent: *
# Nothing to see here
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
        file_string = u"""Title: MDWeb
Description: The minimalistic markdown NaCMS
Badfield: Dragons be here
Author: Chad Rempp
Date: February 1st, 2016
Order: 1
Template: page_home.html
Robots: User-agent: *
"""
        self.assertRaises(PageMetaInfFieldException, PageMetaInf, file_string)

    def test_unicode(self):
        file_string = u"""Title: советских
Description: ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ
Author: Οδυσσέα Ελύτη
Date: February 1st, 2016
Order: 1
Template: ღმერთსი.html
Robots: User-agent: *
"""

        meta_inf = PageMetaInf(file_string)

        self.assertEqual(meta_inf.author, u'Οδυσσέα Ελύτη')
        self.assertEqual(meta_inf.date, u'February 1st, 2016')
        self.assertEqual(meta_inf.description, u'ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ')
        self.assertEqual(meta_inf.order, 1)
        self.assertEqual(meta_inf.robots, u'User-agent: *')
        self.assertEqual(meta_inf.template, u'ღმერთსი.html')
        self.assertEqual(meta_inf.title, u'советских')


class TestPage(fake_filesystem_unittest.TestCase):
    """Page object tests """

    def setUp(self):
        """Create fake filesystem"""
        self.setUpPyfakefs()

    def tearDown(self):
        pass

    @mock.patch('mdweb.Page.PageMetaInf')
    def test_parse_empty_file(self, mock_page_meta_inf):
        """An empty file should parse properly."""
        file_string = u""
        self.fs.CreateFile('/my/content/index.md',
                           contents=file_string)

        p = Page('/my/content', '/my/content/index.md')

        mock_page_meta_inf.assert_called_once_with('')
        self.assertEqual(p.markdown_str, '')
        self.assertEqual(p.page_html, '')

    def test_no_file(self):
        """If the path doesn't contain a file a ContentException should be raised."""
        file_string = u"""Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back."""

        self.assertRaises(ContentException, Page, '/my/content',
                          '/my/content/index.md')

    @mock.patch('mdweb.Page.PageMetaInf')
    def test_no_meta_inf(self, mock_page_meta_inf):
        """A page with no meta information should parse."""
        file_string = u"""Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back."""
        self.fs.CreateFile('/my/content/index.md',
                           contents=file_string)

        p = Page('/my/content', '/my/content/index.md')

        mock_page_meta_inf.assert_called_once_with('')
        self.assertEqual(p.markdown_str, '''Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back.''')
        self.assertEqual(p.page_html, '''<p>Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.</p>
<p>The quick brown fox jumped over the lazy
dog's back.</p>''')

    @mock.patch('mdweb.Page.PageMetaInf')
    def test_page_with_meta_inf(self, mock_page_meta_inf):
        """A page with meta info should parse the content and meta inf."""
        file_string = '''/*
Title: MDWeb Examples
Description: Examples of how to use MDWeb
Order: 4
*/

Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back.'''
        self.fs.CreateFile('/my/content/index.md',
                           contents=file_string)

        p = Page('/my/content', '/my/content/index.md')

        mock_page_meta_inf.assert_called_once_with('''
Title: MDWeb Examples
Description: Examples of how to use MDWeb
Order: 4
''')
        self.assertEqual(p.markdown_str, '''

Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back.''')
        self.assertEqual(p.page_html, '''<p>Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.</p>
<p>The quick brown fox jumped over the lazy
dog's back.</p>''')


    @mock.patch('mdweb.Page.PageMetaInf')
    def test_markdown_formatting(self, mock_page_meta_inf):
        """Markdown should parse correctly.

        We won't test this extensively as we should trust the markdown
        libraries to test themselves."""
        file_string = '''/*
Title: MDWeb Examples
Description: Examples of how to use MDWeb
Order: 4
*/

Examples taken from https://daringfireball.net/projects/markdown/basics

A First Level Header
====================

A Second Level Header
---------------------

Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back.

### Header 3

> This is a blockquote.
>
> This is the second paragraph in the blockquote.
>
> ## This is an H2 in a blockquote

---------------------------------------

Some of these words *are emphasized*.
Some of these words _are emphasized also_.

Use two asterisks for **strong emphasis**.
Or, if you prefer, __use two underscores instead__.

---------------------------------------

*   Candy.
*   Gum.
*   Booze.


---------------------------------------

1.  Red
2.  Green
3.  Blue

---------------------------------------

*   A list item.

    With multiple paragraphs.

*   Another item in the list.

---------------------------------------

This is an [example link](http://example.com/).

This is an [example link](http://example.com/ "With a Title").

---------------------------------------

I get 10 times more traffic from [Google][1] than from
[Yahoo][2] or [MSN][3].

[1]: http://google.com/        "Google"
[2]: http://search.yahoo.com/  "Yahoo Search"
[3]: http://search.msn.com/    "MSN Search"

I start my morning with a cup of coffee and
[The New York Times][NY Times].

[ny times]: http://www.nytimes.com/

---------------------------------------

![alt text](/path/to/img.jpg "Title")

![alt text][id]

[id]: /path/to/img.jpg "Title"

---------------------------------------

I strongly recommend against using any `<blink>` tags.

I wish SmartyPants used named entities like `&mdash;`
instead of decimal-encoded entites like `&#8212;`.


If you want your page to validate under XHTML 1.0 Strict,
you've got to put paragraph tags in your blockquotes:

    <blockquote>
        <p>For example.</p>
    </blockquote>


---------------------------------------'''
        self.fs.CreateFile('/my/content/index.md',
                           contents=file_string)

        p = Page('/my/content', '/my/content/index.md')

        mock_page_meta_inf.assert_called_once_with('''
Title: MDWeb Examples
Description: Examples of how to use MDWeb
Order: 4
''')
        self.assertEqual(p.markdown_str, '''

Examples taken from https://daringfireball.net/projects/markdown/basics

A First Level Header
====================

A Second Level Header
---------------------

Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back.

### Header 3

> This is a blockquote.
>
> This is the second paragraph in the blockquote.
>
> ## This is an H2 in a blockquote

---------------------------------------

Some of these words *are emphasized*.
Some of these words _are emphasized also_.

Use two asterisks for **strong emphasis**.
Or, if you prefer, __use two underscores instead__.

---------------------------------------

*   Candy.
*   Gum.
*   Booze.


---------------------------------------

1.  Red
2.  Green
3.  Blue

---------------------------------------

*   A list item.

    With multiple paragraphs.

*   Another item in the list.

---------------------------------------

This is an [example link](http://example.com/).

This is an [example link](http://example.com/ "With a Title").

---------------------------------------

I get 10 times more traffic from [Google][1] than from
[Yahoo][2] or [MSN][3].

[1]: http://google.com/        "Google"
[2]: http://search.yahoo.com/  "Yahoo Search"
[3]: http://search.msn.com/    "MSN Search"

I start my morning with a cup of coffee and
[The New York Times][NY Times].

[ny times]: http://www.nytimes.com/

---------------------------------------

![alt text](/path/to/img.jpg "Title")

![alt text][id]

[id]: /path/to/img.jpg "Title"

---------------------------------------

I strongly recommend against using any `<blink>` tags.

I wish SmartyPants used named entities like `&mdash;`
instead of decimal-encoded entites like `&#8212;`.


If you want your page to validate under XHTML 1.0 Strict,
you've got to put paragraph tags in your blockquotes:

    <blockquote>
        <p>For example.</p>
    </blockquote>


---------------------------------------''')
        self.assertEqual(p.page_html, '''<p>Examples taken from https://daringfireball.net/projects/markdown/basics</p>
<h1>A First Level Header</h1>
<h2>A Second Level Header</h2>
<p>Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.</p>
<p>The quick brown fox jumped over the lazy
dog's back.</p>
<h3>Header 3</h3>
<blockquote>
<p>This is a blockquote.</p>
<p>This is the second paragraph in the blockquote.</p>
<h2>This is an H2 in a blockquote</h2>
</blockquote>
<hr />
<p>Some of these words <em>are emphasized</em>.
Some of these words <em>are emphasized also</em>.</p>
<p>Use two asterisks for <strong>strong emphasis</strong>.
Or, if you prefer, <strong>use two underscores instead</strong>.</p>
<hr />
<ul>
<li>Candy.</li>
<li>Gum.</li>
<li>Booze.</li>
</ul>
<hr />
<ol>
<li>Red</li>
<li>Green</li>
<li>Blue</li>
</ol>
<hr />
<ul>
<li>
<p>A list item.</p>
<p>With multiple paragraphs.</p>
</li>
<li>
<p>Another item in the list.</p>
</li>
</ul>
<hr />
<p>This is an <a href="http://example.com/">example link</a>.</p>
<p>This is an <a href="http://example.com/" title="With a Title">example link</a>.</p>
<hr />
<p>I get 10 times more traffic from <a href="http://google.com/" title="Google">Google</a> than from
<a href="http://search.yahoo.com/" title="Yahoo Search">Yahoo</a> or <a href="http://search.msn.com/" title="MSN Search">MSN</a>.</p>
<p>I start my morning with a cup of coffee and
<a href="http://www.nytimes.com/">The New York Times</a>.</p>
<hr />
<p><img alt="alt text" src="/path/to/img.jpg" title="Title" /></p>
<p><img alt="alt text" src="/path/to/img.jpg" title="Title" /></p>
<hr />
<p>I strongly recommend against using any <code>&lt;blink&gt;</code> tags.</p>
<p>I wish SmartyPants used named entities like <code>&amp;mdash;</code>
instead of decimal-encoded entites like <code>&amp;#8212;</code>.</p>
<p>If you want your page to validate under XHTML 1.0 Strict,
you've got to put paragraph tags in your blockquotes:</p>
<pre><code>&lt;blockquote&gt;
    &lt;p&gt;For example.&lt;/p&gt;
&lt;/blockquote&gt;
</code></pre>
<hr />''')