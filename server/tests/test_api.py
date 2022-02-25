import json
import logging
import os.path
import tempfile
import typing
from asyncio import Future
from unittest import mock

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

import settings
from app import make_app
from app.base import BaseHandler
from db import User
from fs import FileSystem

logging.getLogger('tornado').setLevel(logging.ERROR)


class MockAdminUser:
    def __init__(self):
        self.group = settings.ADMINISTRATOR

    is_admin = User.is_admin


class TestFile(AsyncHTTPTestCase):

    def setUp(self):
        super().setUp()
        tmp_dir = tempfile.TemporaryDirectory()
        self.__tmp_dir = tmp_dir

        f1 = Future()
        f1.set_result(MockAdminUser())
        mock1 = mock.Mock()
        mock1.return_value = f1

        self.__fs = FileSystem(tmp_dir.name)
        self.__patch = mock.patch.multiple(
            BaseHandler,
            get_current_user=mock1,
            fs=self.__fs,
        )
        self.__patch.start()

    def tearDown(self):
        super().tearDown()
        self.__tmp_dir.cleanup()
        self.__patch.stop()

    def get_app(self) -> Application:
        return make_app()

    @staticmethod
    def extract_error_message(response):
        return json.loads(response.body)['message']

    def test_make_dir(self):
        def fetch():
            return self.fetch('/api/file/mkdir', method='POST', body='path=/a/b')

        response = fetch()
        self.assertEqual(200, response.code)
        self.assertTrue(os.path.isdir(self.__fs.join('a/b')))

        response = fetch()
        self.assertEqual(400, response.code)
        self.assertEqual('文件或目录已存在', self.extract_error_message(response))

    def test_make_file(self):
        def fetch():
            return self.fetch('/api/file/mkfile', method='POST', body='path=a/b')

        response = fetch()
        self.assertEqual(200, response.code)
        self.assertTrue(os.path.isfile(self.__fs.join('a/b')))

        response = fetch()
        self.assertEqual(400, response.code)
        self.assertEqual('文件或目录已存在', self.extract_error_message(response))

    def test_file_reader(self):
        def fetch(path):
            return self.fetch('/api/file/read?path=%s' % path)

        # read empty
        response = fetch('a/b')
        self.assertEqual('文件不存在', self.extract_error_message(response))

        # read dir
        self.__fs.make_dir('a')
        response = fetch('a')
        self.assertEqual('目录不可读', self.extract_error_message(response))

        # read file
        self.__fs.make_file('b.py', content='print("Hello")')
        response = fetch('b.py')
        self.assertEqual({'content': 'print("Hello")', 'path': 'b.py'}, json.loads(response.body))

    def test_file_writer(self):
        def fetch(path):
            return self.fetch('/api/file/write?path=%s' % path, method='POST', body='content=hello')

        # write dir
        self.__fs.make_dir('a')
        response = fetch('a')
        self.assertEqual('目录不可写', self.extract_error_message(response))

        # write file
        fetch('b.txt')
        with open(self.__fs.join('b.txt')) as fp:
            self.assertEqual('hello', fp.read())

    def test_move(self):
        def fetch(source, target):
            return self.fetch('/api/file/rename', method='POST', body='source=%s&target=%s' % (source, target))

        self.__fs.make_file('a/b/c.txt')
        self.__fs.make_dir('d')

        # move file
        response = fetch('a/b/c.txt', 'd/e.txt')
        self.assertEqual(200, response.code)
        self.assertTrue(os.path.isdir(self.__fs.join('a/b')))
        self.assertFalse(os.path.exists(self.__fs.join('a/b/c.txt')))
        self.assertTrue(os.path.isfile(self.__fs.join('d/e.txt')))

        # move dir
        response = fetch('a', 'z')
        self.assertEqual(200, response.code)
        self.assertTrue(os.path.isdir(self.__fs.join('z/b')))
        self.assertFalse(os.path.exists(self.__fs.join('a')))

    def test_remove(self):
        def fetch(path):
            return self.fetch('/api/file/remove', method='POST', body='path=%s' % path)

        self.__fs.make_file('/a/b.txt')
        response = fetch('/a/b.txt')
        self.assertEqual(200, response.code)
        self.assertFalse(os.path.exists(self.__fs.join('/a/b.txt')))

        # remove not exists
        self.assertFalse(os.path.exists(self.__fs.join('not exists')))
        response = fetch('not exists')
        self.assertEqual(200, response.code)

    def test_upload(self):
        from requests import PreparedRequest

        def fetch(fp: typing.IO):
            pr = PreparedRequest()
            pr.prepare_headers({})
            pr.prepare_body(data={'dir': '/'}, files={'file': fp.read()})
            return self.fetch('/api/file/upload', method='POST', body=pr.body, headers=pr.headers)

        self.__fs.make_file('a.txt', content='hello123')
        with open(self.__fs.join('a.txt')) as f:
            response = fetch(f)
        self.assertEqual(200, response.code)
        with open(self.__fs.join('file')) as f:
            self.assertEqual('hello123', f.read())

        # duplication
        with open(self.__fs.join('a.txt')) as f:
            fetch(f), fetch(f)
        self.assertTrue(os.path.exists(self.__fs.join('file(1)')))
        self.assertTrue(os.path.exists(self.__fs.join('file(2)')))

    def test_download(self):
        pass  # TODO
