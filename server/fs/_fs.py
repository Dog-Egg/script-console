import os
import re
import shutil
from pathlib import Path

import settings
from ._config import Config


class FileSystem:
    def __init__(self, root, *, group=None):
        self.root = root
        self._config = None
        self._conf_path = os.path.join(self.root, settings.CONFIG_FILENAME)
        self.group = group

    @property
    def config(self):
        if self._config is None:
            self._config = Config(self._conf_path)
        return self._config

    def join(self, path):
        path = os.path.normpath(os.path.join('/', path))
        return os.path.join(self.root, path[1:])

    def make_file(self, path, *, content=''):
        path = self.join(path)
        if os.path.exists(path):
            raise FileExistsError(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as fp:
            fp.write(content)
        return path

    def make_dir(self, path):
        path = self.join(path)
        os.makedirs(path)
        return path

    def remove(self, path):
        path = self.join(path)
        p = Path(path)
        if p.is_file():
            os.remove(p)
        elif p.is_dir():
            shutil.rmtree(path)

    def rename(self, source, target):
        source = self.join(source)
        s = Path(source)
        if not s.exists():
            raise FileNotFoundError(source)

        target = self.join(target)
        t = Path(target)
        if t.exists():
            raise FileExistsError(target)

        s.rename(t)

    def tree(self):
        ignore = self._ignore_parser()

        def _get_tree(dir_path) -> list:
            res = []
            for entry in os.scandir(dir_path):
                entry: os.DirEntry

                relpath = os.path.relpath(entry.path, self.root)
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

        rv = _get_tree(self.root)

        if self.group == settings.ADMINISTRATOR:
            especial = [settings.CONFIG_FILENAME]
            for i in especial:
                rv.append(dict(title=i, key=i, isLeaf=True, isSys=True))
        return rv

    def _ignore_parser(self):
        def get_permission_ignores():
            rv = []
            for item in self.config.access:
                if self.group not in item.groups:
                    rv.append(item.pattern)
            return rv

        permission_ignores = get_permission_ignores()

        def wrapper(path):
            for p in permission_ignores:
                if re.search(p, path):
                    return True
            return False

        return wrapper

    def run_file(self, path):
        if self.config.error:
            raise self.config.error

        command = self.config.get_command(path)
        if not command:
            raise RuntimeError('Not found executable program')

        path = self.join(path)
        program = command.program
        name = os.path.basename(program)
        env = os.environ.copy()
        env.update(command.environment)
        print('\033[1;33m' + ('Command "%s"' % ' '.join([program, path])) + '\x1B[0m', os.linesep)
        os.execlpe(program, name, path, env)
