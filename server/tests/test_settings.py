import importlib
import unittest
from unittest import mock


class TestSettings(unittest.TestCase):
    def test(self):
        with mock.patch('os.environ', {'SC_ADMINISTRATOR': 'root'}):
            import settings
            importlib.reload(settings)
            self.assertEqual(settings.ADMINISTRATOR, 'root')
        importlib.reload(settings)
