import unittest
from unittest import mock

from conf.settings import Settings, ConvertError


class TestSettings(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Settings()

    def test(self):
        with mock.patch('os.environ', {'SC_SCRIPTS_DIR': '/scripts', 'SC_DEBUG': '1'}):
            self.settings.from_env()
            self.settings.freeze()
            self.assertEqual('/scripts', self.settings.SCRIPTS_DIR)
            self.assertIs(True, self.settings.DEBUG)

    def test_frozen(self):
        with self.assertRaisesRegex(RuntimeError, '^not frozen before getting setting.$'):
            getattr(self.settings, 'DEBUG')

        self.settings.freeze()

        with self.assertRaisesRegex(RuntimeError, '^settings frozen.$'):
            self.settings.DEBUG = 1

    def test_readonly(self):
        with mock.patch('os.environ', {'SC_ADMINISTRATOR': 'root'}):
            with self.assertRaisesRegex(RuntimeError,
                                        '^The environment variable \'SC_ADMINISTRATOR\', It is readonly.$'):
                self.settings.from_env()

    def test_not_exist(self):
        self.settings.freeze()
        with self.assertRaisesRegex(AttributeError, r"^'Settings' object has no attribute 'NOT_EXISTS'$"):
            self.assertRaises(self.settings.NOT_EXISTS)

    def test_setattr(self):
        with self.assertRaisesRegex(ConvertError,
                                    "^Supported values for boolean settings are 0/1, True/False, '0'/'1', "
                                    "'True'/'False' and 'true'/'false'.$"):
            self.settings.DEBUG = 'T'

        self.settings.DEBUG = 'true'
        self.settings.freeze()
        self.assertIs(True, self.settings.DEBUG)
