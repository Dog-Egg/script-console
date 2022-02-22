import unittest

from utils import refactor_filename


class TestUtils(unittest.TestCase):
    def test_refactor_filename(self):
        rf = refactor_filename('/a/b.txt')
        self.assertEqual('/a/b(1).txt', next(rf))
        self.assertEqual('/a/b(2).txt', next(rf))
        self.assertEqual('/a/b(3).txt', next(rf))
