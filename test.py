import os
import unittest
import mock
import tempfile

import settings
from runner import Runner
import fs


class TestRunner(unittest.TestCase):
    def test(self):
        def _open(filename, *args, **kwargs):
            if filename == 'foo':
                return mock.mock_open(read_data="""
                scripts:
                    -   pattern: .*\.py
                        program: python

                    -   pattern: 123\.py
                        program: python3.2
                        priority: 1
                        environment:
                            PYTHONPATH: /site-packages3.2
                """)()
            return open(filename, *args, **kwargs)

        execlpe_mock = mock.Mock()

        with mock.patch('conf.open', _open):
            with mock.patch('runner.os.execlpe', execlpe_mock):
                with mock.patch.multiple('runner', print=mock.DEFAULT):
                    run = Runner('foo')
                    run('123.py')

        env = os.environ.copy()
        env.update(PYTHONPATH='/site-packages3.2')
        execlpe_mock.assert_called_once_with('python3.2', 'python3.2', '123.py', env)


def mock_fs_root(fn):
    def wrapper(*args, **kwargs):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch('fs.ROOT', d):
                return fn(*args, **kwargs)

    return wrapper


class TestFs(unittest.TestCase):
    def test_join(self):
        self.assertEqual(fs.join('/a'), os.path.join(settings.SCRIPTS_DIR, 'a'))
        self.assertEqual(fs.join('./a'), os.path.join(settings.SCRIPTS_DIR, 'a'))
        self.assertEqual(fs.join('../a'), os.path.join(settings.SCRIPTS_DIR, 'a'))
        self.assertEqual(fs.join('a'), os.path.join(settings.SCRIPTS_DIR, 'a'))
        self.assertEqual(fs.join('/a/b'), os.path.join(settings.SCRIPTS_DIR, 'a/b'))
        self.assertEqual(fs.join('./a/b'), os.path.join(settings.SCRIPTS_DIR, 'a/b'))
        self.assertEqual(fs.join('../a/b'), os.path.join(settings.SCRIPTS_DIR, 'a/b'))
        self.assertEqual(fs.join('./a/../b'), os.path.join(settings.SCRIPTS_DIR, 'b'))
        self.assertEqual(fs.join('../a/../../b'), os.path.join(settings.SCRIPTS_DIR, 'b'))

    @mock_fs_root
    def test_make_file(self):
        fs.make_file('a.txt')
        self.assertTrue(os.path.isfile(os.path.join(fs.ROOT, 'a.txt')))

        fs.make_file('/a/b.txt')
        self.assertTrue(os.path.isfile(os.path.join(fs.ROOT, 'a/b.txt')))

        with self.assertRaises(FileExistsError):
            fs.make_file('a.txt')
            fs.make_file('a/b.txt')

    @mock_fs_root
    def test_make_dir(self):
        fs.make_dir('a')
        self.assertTrue(os.path.isdir(os.path.join(fs.ROOT, 'a')))

        fs.make_dir('a/b/c')
        self.assertTrue(os.path.isdir(os.path.join(fs.ROOT, 'a/b/c')))

        with self.assertRaises(FileExistsError):
            fs.make_dir('a')
            fs.make_dir('a/b/c')

    @mock_fs_root
    def test_make(self):
        fs.make_file('a')
        with self.assertRaises(FileExistsError):
            fs.make_dir('a')

        fs.make_dir('b/c/d')
        with self.assertRaises(FileExistsError):
            fs.make_file('b/c/d')

    @mock_fs_root
    def test_remove(self):
        fs.make_file('a/b/c/d.txt')
        fs.remove('a/b/c/d.txt')
        self.assertFalse(os.path.exists(os.path.join(fs.ROOT, 'a/b/c/d.txt')))
        self.assertTrue(os.path.exists(os.path.join(fs.ROOT, 'a/b/c/')))

        fs.remove('a/b')
        self.assertFalse(os.path.exists(os.path.join(fs.ROOT, 'a/b')))
        self.assertTrue(os.path.exists(os.path.join(fs.ROOT, 'a/')))

        fs.remove('a/b')

    @mock_fs_root
    def test_rename(self):
        fs.make_file('a/b/c/d.txt')
        fs.rename('a/b', 'a/e')
        self.assertTrue(os.path.exists(os.path.join(fs.ROOT, 'a/e/c/d.txt')))

        fs.rename('a/e/c/d.txt', 'a/e/c/e.txt')
        self.assertTrue(os.path.exists(os.path.join(fs.ROOT, 'a/e/c/e.txt')))

        with self.assertRaises(FileNotFoundError):
            fs.rename('b', 'z')

        with self.assertRaises(FileExistsError):
            fs.make_dir('b')
            fs.rename('b', 'a')


if __name__ == '__main__':
    unittest.main()
