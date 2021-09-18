import fnmatch
import os
import random
import string

from gitignore_parser import parse_gitignore

import settings
from conf import Conf


def ignore_parser(group):
    def get_permission_ignores():
        if group == settings.ADMINISTRATOR:
            return []

        rv = []
        conf = Conf(settings.CONFIG_FILE_PATH)
        for c in conf.file_configs:
            if c.groups and group not in c.groups:
                rv.append(c.pattern)
        return rv

    try:
        ignore = parse_gitignore(settings.IGNORE_FILE_PATH)
    except FileNotFoundError:
        def ignore(_):
            return False

    permission_ignores = get_permission_ignores()

    def wrapper(path):
        result = ignore(path)
        if result:
            return result

        for p in permission_ignores:
            if fnmatch.fnmatch(path, p):
                return True
        return False

    return wrapper


def find_scripts(group):
    ignore = ignore_parser(group)
    root = settings.SCRIPTS_DIR

    def _find_scripts(dir_path) -> list:
        res = []
        for entry in os.scandir(dir_path):
            entry: os.DirEntry
            node = {'name': entry.name, 'path': os.path.relpath(entry.path, root)}
            if entry.name.startswith('.') or ignore(entry.path):
                continue

            if entry.is_dir():
                children = _find_scripts(entry.path)
                if not children:
                    continue
                node.update(children=children)

            res.append(node)

        res = sorted(res, key=lambda x: 'children' not in x)
        return res

    rv = _find_scripts(root)

    if group == settings.ADMINISTRATOR:
        especial = [settings.IGNORE_FILENAME, settings.CONFIG_FILENAME]
        for i in especial:
            rv.append(dict(name=i, path=i, sys=True))
    return rv


def gen_token():
    charset = random.choices(string.digits + string.ascii_letters, k=24)
    return ''.join(charset)


if __name__ == '__main__':
    print(gen_token())
