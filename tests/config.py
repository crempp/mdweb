import mock
import unittest

from mdweb import MDWebConfig

class TestConfig(unittest.TestCase):

    def setUp(self):
        pass

    # @mock.patch('mdweb.os')
    @mock.patch('mdweb.Config')
    def test_config_load(self, mock_Config):
        """ Configuration should load """

        class MockConfig (object):
            DEBUG = False
            TESTING = False
            SECRET_KEY = 'development key'
            META_INF_REGEX = r'/\*(.*)\*/'
            CONTENT_PATH = 'content/'
            THEME = 'alphabeta'

        mock_Config.return_value = MockConfig

        c = MDWebConfig('test_app')

        self.assertTrue('DEBUG' in c,
                        "Config should have DEBUG setting")
        self.assertTrue('TESTING' in c,
                        "Config should have TESTING setting")
        self.assertTrue('SECRET_KEY' in c,
                        "Config should have SECRET_KEY setting")
        self.assertTrue('META_INF_REGEX' in c,
                        "Config should have META_INF_REGEX setting")
        self.assertTrue('CONTENT_PATH' in c,
                        "Config should have CONTENT_PATH setting")
        self.assertTrue('THEME' in c,
                        "Config should have THEME setting")
        self.assertTrue('THEME_FOLDER' in c,
                        "Config should have THEME_FOLDER setting")

        print(c['THEME'])

        c2 = MDWebConfig('test_app2',
            {
                'DEBUG': False,
                'SECRET_KEY': 'bloopbleep',
            })



        self.assertTrue(False)

    def test_theme_folder_property(self):
        c = MDWebConfig('test_app')
        c.THEME = "testtheme"

