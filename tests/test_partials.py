from flask import render_template
from flask_testing import TestCase
import os
from pyfakefs import fake_filesystem_unittest, fake_filesystem
from tests.sites import MDTestSite
from mdweb.MDSite import BASE_PATH
from mdweb.Page import Page, load_page


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
        self.assertContext('ga_tracking', '''<script async src="https://www.googletagmanager.com/gtag/js?id=UA-5854565-2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-00000000-1');
</script>''')

    def test_og_full_data(self):
        with self.app.test_client() as client:
            response = client.get('/')
        self.assertEqual(response.data[:598], og_full_data_response)

    def test_og_partial_data(self):
        with self.app.test_client() as client:
            response = client.get('/download')
        self.assertEqual(response.data[:414], og_partial_data_response)

    def test_og_no_data(self):
        with self.app.test_client() as client:
            response = client.get('/about/empty')
        self.assertEqual(response.data[:303], og_no_data_response)


og_full_data_response = b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta property="og:title" content="MDWeb" />
<meta property="og:image" content="/contentassets/teaser.png" />
<meta property="og:description" content="The minimalistic markdown NaCMS" />
<meta property="article:published_time" content="2016/10/02" />
<meta property="article:author" content="Chad Rempp" />
<meta property="og:url" content="" />
<meta property="og:type" content="article" />
    <link rel="icon" href="/favicon.ico">
    <title>MDWeb</title>
    <link href="/static/css/style.css" rel="stylesheet">
  </head>
'''

og_partial_data_response = b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta property="og:title" content="Download MDWeb" />
<meta property="og:description" content="Download MDWeb" />

<meta property="og:url" content="download" />
<meta property="og:type" content="article" />
    <link rel="icon" href="/favicon.ico">
    <title>MDWeb</title>
    <link href="/static/css/style.css" rel="stylesheet">
  </head>
'''

og_no_data_response = b'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    
<meta property="og:url" content="about/empty" />
<meta property="og:type" content="article" />
    <link rel="icon" href="/favicon.ico">
    <title>MDWeb</title>
    <link href="/static/css/style.css" rel="stylesheet">
  </head>
'''
