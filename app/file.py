import os

from tornado.web import MissingArgumentError

from utils import asynctools, refactor_filename
from .base import BaseHandler, admin_required


class FileTreeHandler(BaseHandler):
    async def get(self):
        fs = await self.get_file_system()
        value = fs.tree()
        self.write({'data': value})


class MakeDirHandler(BaseHandler):
    @admin_required
    async def post(self):
        path = self.get_argument('path')
        fs = await self.get_file_system()
        try:
            fs.make_dir(path)
        except FileExistsError:
            return self.finish_error(message='文件或目录已存在')
        await self.finish()


class MakeFileHandler(BaseHandler):
    @admin_required
    async def post(self):
        path = self.get_argument('path')
        fs = await self.get_file_system()
        try:
            fs.make_file(path)
        except FileExistsError:
            return self.finish_error(message='文件或目录已存在')
        await self.finish()


class FileReadHandler(BaseHandler):
    @admin_required
    async def get(self):
        path = self.get_argument('path')
        fs = await self.get_file_system()
        full_path = fs.join(path)
        try:
            with open(full_path) as fp:
                content = fp.read()
        except FileNotFoundError:
            return self.finish_error(message='文件不存在')
        except UnicodeDecodeError:
            return self.finish_error(message='非文本文件，解码失败')
        except IsADirectoryError:
            return self.finish_error(message='目录不可读')
        await self.finish({'content': content, 'path': path})


class FileWriteHandler(BaseHandler):
    @admin_required
    async def post(self):
        path = self.get_argument('path')
        content = self.get_body_argument('content')
        fs = await self.get_file_system()
        full_path = fs.join(path)
        try:
            with open(full_path, 'w') as fp:
                fp.write(content)
        except IsADirectoryError:
            return self.finish_error(message='目录不可写')


class FileRenameHandler(BaseHandler):
    @admin_required
    async def post(self):
        source = self.get_argument('source')
        target = self.get_argument('target')
        fs = await self.get_file_system()
        try:
            fs.rename(source, target)
        except FileExistsError:
            return self.finish_error(message='文件或目录已存在')
        except FileNotFoundError:
            return self.finish_error(message='文件或目录不存在')


class FileRemoveHandler(BaseHandler):
    @admin_required
    async def post(self):
        path = self.get_argument('path')
        fs = await self.get_file_system()
        fs.remove(path)
        await self.finish()


class FileUploadHandler(BaseHandler):
    @admin_required
    async def post(self):
        if 'file' not in self.request.files:
            raise MissingArgumentError('file')
        file = self.request.files['file'][0]
        dir_path = self.get_argument('dir')
        fs = await self.get_file_system()
        file_path = os.path.join(fs.join(dir_path), file['filename'])

        if await asynctools.exists(file_path):
            for file_path in refactor_filename(file_path):
                if not await asynctools.exists(file_path):
                    break

        try:
            async with asynctools.open(file_path, 'wb') as fp:
                await fp.write(file['body'])
        except FileNotFoundError:
            return self.finish_error(message='目录不存在')
        await self.finish()


class FileDownloadHandler(BaseHandler):
    @admin_required
    async def get(self):
        path = self.get_argument('path')
        fs = await self.get_file_system()
        full_path = fs.join(path)
        try:
            async with asynctools.open(full_path, 'rb') as fp:
                while True:
                    data = await fp.read(1024 * 4)
                    if not data:
                        break
                    self.write(data)
                    await self.flush()
        except FileNotFoundError:
            self.finish_error(message='文件不存在')
        await self.finish()
