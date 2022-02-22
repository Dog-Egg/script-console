import os
import unittest
import tempfile

from mock import mock

from fs import FileSystem


class TestFileSystem(unittest.TestCase):
    def test_join(self):
        with tempfile.TemporaryDirectory() as temp:
            fs = FileSystem(temp)

            self.assertEqual(fs.join('/a'), os.path.join(temp, 'a'))
            self.assertEqual(fs.join('./a'), os.path.join(temp, 'a'))
            self.assertEqual(fs.join('../a'), os.path.join(temp, 'a'))
            self.assertEqual(fs.join('a'), os.path.join(temp, 'a'))
            self.assertEqual(fs.join('/a/b'), os.path.join(temp, 'a/b'))
            self.assertEqual(fs.join('./a/b'), os.path.join(temp, 'a/b'))
            self.assertEqual(fs.join('../a/b'), os.path.join(temp, 'a/b'))
            self.assertEqual(fs.join('./a/../b'), os.path.join(temp, 'b'))
            self.assertEqual(fs.join('../a/../../b'), os.path.join(temp, 'b'))

    def test_make_file_and_dir(self):
        with tempfile.TemporaryDirectory() as temp:
            fs = FileSystem(temp)

            # make file
            fs.make_file('a.txt')
            self.assertTrue(os.path.isfile(os.path.join(temp, 'a.txt')))

            fs.make_file('/a/b.txt')
            self.assertTrue(os.path.isfile(os.path.join(temp, 'a/b.txt')))

            with self.assertRaises(FileExistsError):
                fs.make_file('a.txt')

            # make dir
            fs.make_dir('d')
            self.assertTrue(os.path.isdir(os.path.join(temp, 'd')))

            fs.make_dir('a/b/c')
            self.assertTrue(os.path.isdir(os.path.join(temp, 'a/b/c')))

            with self.assertRaises(FileExistsError):
                fs.make_dir('a')

    def test_remove(self):
        with tempfile.TemporaryDirectory() as temp:
            fs = FileSystem(temp)

            fs.make_file('a/b/c/d.txt')
            fs.remove('a/b/c/d.txt')
            self.assertFalse(os.path.exists(os.path.join(temp, 'a/b/c/d.txt')))
            self.assertTrue(os.path.exists(os.path.join(temp, 'a/b/c/')))

            fs.remove('a/b')
            self.assertFalse(os.path.exists(os.path.join(temp, 'a/b')))
            self.assertTrue(os.path.exists(os.path.join(temp, 'a/')))

            fs.remove('a/b')

    def test_rename(self):
        with tempfile.TemporaryDirectory() as temp:
            fs = FileSystem(temp)

            fs.make_file('a/b/c/d.txt')
            fs.rename('a/b', 'a/e')
            self.assertTrue(os.path.exists(os.path.join(temp, 'a/e/c/d.txt')))

            fs.rename('a/e/c/d.txt', 'a/e/c/e.txt')
            self.assertTrue(os.path.exists(os.path.join(temp, 'a/e/c/e.txt')))

            with self.assertRaises(FileNotFoundError):
                fs.rename('b', 'z')

            fs.make_dir('b')
            with self.assertRaises(FileExistsError):
                fs.rename('b', 'a')

    def test_run_file(self):
        def _open(filename, *args, **kwargs):
            if filename == 'foo/.sc-conf.yaml':
                return mock.mock_open(read_data="""
                commands:
                    -   pattern: 123\.py
                        program: python3.2
                        environment:
                            PYTHONPATH: /site-packages3.2

                    -   pattern: .*\.py
                        program: python
                """)()
            return open(filename, *args, **kwargs)

        execlpe_mock = mock.Mock()

        with mock.patch('fs._config.open', _open):
            with mock.patch('fs._fs.os.execlpe', execlpe_mock):
                with mock.patch.multiple('fs._fs', print=mock.DEFAULT):
                    fs = FileSystem('foo')
                    fs.run_file('123.py')

        env = os.environ.copy()
        env.update(PYTHONPATH='/site-packages3.2')
        execlpe_mock.assert_called_once_with('python3.2', 'python3.2', 'foo/123.py', env)


if __name__ == '__main__':
    unittest.main()
