import os
import re
import typing

from tornado.web import MissingArgumentError

from conf import settings
from utils import asynctools, refactor_filename
from web.base import APIHandler, admin_required


class FileTreeHandler(APIHandler):
    current_user_group: typing.Optional[str]

    async def prepare(self):
        user = await self.current_user
        self.current_user_group = user and user.group

    def get(self):
        self.write({'data': self.tree()})

    def tree(self):
        root = settings.SCRIPTS_DIR
        ignore = self._ignore_parser()

        def _get_tree(dir_path) -> list:
            res = []
            for entry in os.scandir(dir_path):
                entry: os.DirEntry

                relpath = os.path.relpath(entry.path, root)
                if entry.name.startswith('.') or ignore(relpath):
                    continue

                node = {'title': entry.name, 'key': relpath}
                if entry.is_dir():
                    children = _get_tree(entry.path)
                    node.update(children=children)

                elif entry.is_file():
                    node.update(isLeaf=True)

                res.append(node)

            res = sorted(res, key=lambda x: 'children' not in x)
            return res

        rv = _get_tree(root)

        # admin 登陆后，在前端展示配置文件，以供手动修改
        # if self.current_user_group == settings.ADMINISTRATOR:
        #     especial = [settings.CONFIG_FILENAME]
        #     for i in especial:
        #         rv.append(dict(title=i, key=i, isLeaf=True, isSys=True))

        return rv

    def _ignore_parser(self):
        def get_permission_ignores():
            rv = []
            for item in self.config.access:
                if self.current_user_group not in item.groups:
                    rv.append(item.pattern)
            return rv

        permission_ignores = get_permission_ignores()

        def wrapper(path):
            for p in permission_ignores:
                if re.search(p, path):
                    return True
            return False

        return wrapper


class MakeDirHandler(APIHandler):
    @admin_required
    def post(self):
        path = self.get_argument('path')
        try:
            self.fs.make_dir(path)
        except FileExistsError:
            return self.finish_error(message='文件或目录已存在')
        self.finish()


class MakeFileHandler(APIHandler):
    @admin_required
    def post(self):
        path = self.get_argument('path')
        try:
            self.fs.make_file(path)
        except FileExistsError:
            return self.finish_error(message='文件或目录已存在')
        self.finish()


class FileReadHandler(APIHandler):
    @admin_required
    def get(self):
        path = self.get_argument('path')
        full_path = self.fs.join(path)
        try:
            with open(full_path) as fp:
                content = fp.read()
        except FileNotFoundError:
            return self.finish_error(message='文件不存在')
        except UnicodeDecodeError:
            return self.finish_error(message='非文本文件，解码失败')
        except IsADirectoryError:
            return self.finish_error(message='目录不可读')
        self.finish({'content': content, 'path': path})


class FileWriteHandler(APIHandler):
    @admin_required
    def post(self):
        path = self.get_argument('path')
        content: str = self.get_body_argument('content')
        full_path = self.fs.join(path)
        try:
            with open(full_path, 'w') as fp:
                fp.write(content.replace('\r', ''))
        except IsADirectoryError:
            return self.finish_error(message='目录不可写')


class FileRenameHandler(APIHandler):
    @admin_required
    def post(self):
        source = self.get_argument('source')
        target = self.get_argument('target')
        try:
            self.fs.rename(source, target)
        except FileExistsError:
            return self.finish_error(message='文件或目录已存在')
        except FileNotFoundError:
            return self.finish_error(message='文件或目录不存在')


class FileRemoveHandler(APIHandler):
    @admin_required
    def post(self):
        path = self.get_argument('path')
        self.fs.remove(path)
        self.finish()


class FileUploadHandler(APIHandler):
    @admin_required
    async def post(self):
        if 'file' not in self.request.files:
            raise MissingArgumentError('file')
        file = self.request.files['file'][0]
        dir_path = self.get_argument('dir')
        file_path = os.path.join(self.fs.join(dir_path), file['filename'])

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


class FileDownloadHandler(APIHandler):
    @admin_required
    async def get(self):
        path = self.get_argument('path')
        full_path = self.fs.join(path)
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
