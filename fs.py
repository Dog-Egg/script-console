import os
import shutil
from pathlib import Path

import settings
from utils import ignore_parser

ROOT = settings.SCRIPTS_DIR


def join(path):
    path = os.path.normpath(os.path.join('/', path))
    return os.path.join(ROOT, path[1:])


def make_file(path):
    path = join(path)
    if os.path.exists(path):
        raise FileExistsError(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'a').close()
    return path


def make_dir(path):
    path = join(path)
    os.makedirs(path)
    return path


def remove(path):
    path = join(path)
    p = Path(path)
    if p.is_file():
        os.remove(p)
    elif p.is_dir():
        shutil.rmtree(path)


def rename(path, target):
    path = join(path)
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    target = join(target)
    t = Path(target)
    if t.exists():
        raise FileExistsError(target)

    p.rename(t)


def get_directory(group):
    ignore = ignore_parser(group)

    def _get_directory(dir_path) -> list:
        res = []
        for entry in os.scandir(dir_path):
            entry: os.DirEntry
            node = {'title': entry.name, 'key': os.path.relpath(entry.path, ROOT)}
            if entry.name.startswith('.') or ignore(entry.path):
                continue

            if entry.is_dir():
                children = _get_directory(entry.path)
                node.update(children=children)

            elif entry.is_file():
                node.update(isLeaf=True)

            res.append(node)

        res = sorted(res, key=lambda x: 'children' not in x)
        return res

    rv = _get_directory(ROOT)

    if group == settings.ADMINISTRATOR:
        especial = [settings.IGNORE_FILENAME, settings.CONFIG_FILENAME]
        for i in especial:
            rv.append(dict(title=i, key=i, isLeaf=True, isSys=True))
    return rv
