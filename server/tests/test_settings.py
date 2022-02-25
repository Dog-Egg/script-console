import importlib
import unittest
from unittest import mock


class TestSettings(unittest.TestCase):
    def test(self):
        with mock.patch('os.environ', {'SC_ADMINISTRATOR': 'root', 'SC_SCRIPTS_DIR': '/scripts'}):
            import settings
            importlib.reload(settings)
            self.assertEqual(settings.ADMINISTRATOR, 'root')
            self.assertEqual(settings.CONFIG_FILE_PATH, '/scripts/.sc-conf.yaml')
        importlib.reload(settings)
