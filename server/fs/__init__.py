import os
import shutil
from pathlib import Path


class FileSystem:
    def __init__(self, root):
        self.root = root

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
