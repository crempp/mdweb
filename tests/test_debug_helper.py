# -*- coding: utf-8 -*-
"""Tests for the Debug Helper."""
from flask.ext.testing import TestCase
from tests.sites import MDTestSiteDebugHelper, MDTestSite


class TestDebugHelperOn(TestCase):
    """Debug helper tests.

    Can't use pyfakefs for this or partials won't load"""

    def create_app(self):

        app = MDTestSiteDebugHelper(
            "MDWeb",
            app_options={}
        )
        app.start()

        return app

    def test_debug_helper_loads(self):
        # self.app.DEBUG_HELPER
        with self.app.test_client() as client:
            response = client.get('/')
            response_data = response.get_data(as_text=True)
        self.assertTrue('<div id="md_debug_display">' in response_data)


class TestDebugHelperOff(TestCase):
    """Debug helper tests.

    Can't use pyfakefs for this or partials won't load"""

    def create_app(self):
        app = MDTestSite(
            "MDWeb",
            app_options={}
        )
        app.start()

        return app

    def test_debug_helper_loads(self):
        with self.app.test_client() as client:
            response = client.get('/')
            response_data = response.get_data(as_text=True)
        self.assertTrue('<div id="md_debug_display">' not in response_data)

