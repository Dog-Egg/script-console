import os
import unittest
import mock

from runner import Runner


class TestRunner(unittest.TestCase):
    def test(self):
        def _open(filename, *args, **kwargs):
            if filename == 'foo':
                return mock.mock_open(read_data="""
                [file:*.py]
                program=python

                [file:123.py]
                program=python3.2
                priority=1
                environment=PYTHONPATH=/site-packages3.2
                """)()
            return open(filename, *args, **kwargs)

        execlpe_mock = mock.Mock()
        exit_mock = mock.Mock()

        with mock.patch('configparser.open', _open):
            with mock.patch('runner.os.execlpe', execlpe_mock):
                with mock.patch.multiple('runner', exit=exit_mock, print=mock.DEFAULT, traceback=mock.DEFAULT):
                    run = Runner('foo')
                    run('123.py')

        env = os.environ.copy()
        env.update(PYTHONPATH='/site-packages3.2')
        execlpe_mock.assert_called_once_with('python3.2', 'python3.2', '123.py', env)

        exit_mock.assert_called_once_with(1)
