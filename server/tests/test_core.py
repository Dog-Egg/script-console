import os
import unittest
from unittest import mock

from web.handlers.ws import RunScriptHandler
from conf.config import Config
from fs import FileSystem


class TestCore(unittest.TestCase):
    def test_exec(self):
        execlpe_mock = mock.Mock()

        @mock.patch('os.execlpe', execlpe_mock)
        @mock.patch.multiple('web.ws', exit=mock.DEFAULT, print=mock.DEFAULT, traceback=mock.DEFAULT)
        def test(*_, **__):
            _self = mock.Mock()
            _self.fs = FileSystem('foo')
            _self.config = Config()
            _self.config.read_yaml("""
                commands:
                    -   pattern: 123\.py
                        program: python3.2
                        environments:
                            -   name: PYTHONPATH
                                value: /site-packages3.2

                    -   pattern: .*\.py
                        program: python
                """)
            _self.path = '123.py'
            RunScriptHandler.subprocess(_self)

        test()

        env = os.environ.copy()
        env.update(PYTHONPATH='/site-packages3.2')
        execlpe_mock.assert_called_once_with('python3.2', 'python3.2', 'foo/123.py', env)
