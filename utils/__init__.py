import random
import re
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
        for c in conf.script_configs:
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
            if re.search(p, path):
                return True
        return False

    return wrapper


def gen_token():
    charset = random.choices(string.digits + string.ascii_letters, k=24)
    return ''.join(charset)


if __name__ == '__main__':
    print(gen_token())
