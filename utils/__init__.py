import random
import re
import string

import settings
from conf import Conf


def ignore_parser(group):
    def get_permission_ignores():
        rv = []
        conf = Conf(settings.CONFIG_FILE_PATH)
        for item in conf.access:
            if group not in item["groups"]:
                rv.append(item["pattern"])
        return rv

    permission_ignores = get_permission_ignores()

    def wrapper(path):
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
